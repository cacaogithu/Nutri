from flask import Flask, request, jsonify
from database import db
from buffer_manager import buffer_manager
from config import ALLOWED_PHONE_NUMBER, TESTING_MODE
import logging
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Start buffer manager on startup
with app.app_context():
    buffer_manager.start()

def _normalize_phone(phone: str) -> str:
    """Normalize phone number."""
    phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    if not phone.startswith('+'):
        if phone.startswith('55'):
            phone = f"+{phone}"
        else:
            phone = f"+{phone}"
    return phone

def _check_access_control(phone: str) -> bool:
    """Check if phone number is allowed."""
    normalized = _normalize_phone(phone)
    allowed = _normalize_phone(ALLOWED_PHONE_NUMBER)
    
    if normalized != allowed:
        logger.warning(f"🚫 Webhook access denied for {normalized} (allowed: {allowed})")
        return False
    return True

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Z-API webhook endpoint.
    Responds immediately (< 1s) to prevent Z-API timeout.
    Messages are buffered and processed asynchronously.
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        phone = data.get('phone', '')
        message_data = data.get('message', {})
        message = message_data.get('text', '') or message_data.get('message', '')
        
        if not phone or not message:
            return jsonify({"error": "Missing phone or message"}), 400
        
        # Normalize phone
        phone = _normalize_phone(phone)
        
        # Access control - check before processing
        if not _check_access_control(phone):
            # Still return 200 to prevent Z-API retries, but log the block
            db.create_alert(
                type='webhook_blocked',
                phone=phone,
                details=f"Webhook blocked: phone not in allow-list"
            )
            return jsonify({
                "success": True,
                "message": "Received",
                "blocked": True
            }), 200
        
        # Add message to buffer (returns immediately)
        result = buffer_manager.add_message(
            phone=phone,
            message=message,
            metadata={
                "webhook_data": data,
                "source": "zapi_webhook"
            }
        )
        
        # Return immediate response to Z-API (< 1 second)
        return jsonify({
            "success": True,
            "message": "Buffered",
            "webhook_id": result.get("expires_at"),
            "received_at": result.get("expires_at")
        }), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        # Still return 200 to prevent Z-API retries
        return jsonify({
            "success": False,
            "error": str(e)
        }), 200

@app.route('/webhook/status', methods=['GET'])
def status():
    """Health check endpoint."""
    from whatsapp_api import whatsapp
    
    health = whatsapp.health_check()
    
    return jsonify({
        "status": "online",
        "service": "WhatsApp AI Nutrition Agent",
        "testing_mode": TESTING_MODE,
        "buffer_manager_running": buffer_manager.running,
        "zapi_health": health
    }), 200

@app.route('/webhook/health', methods=['GET'])
def health():
    """Detailed health check."""
    from whatsapp_api import whatsapp
    
    health_data = {
        "status": "healthy",
        "testing_mode": TESTING_MODE,
        "buffer_manager": {
            "running": buffer_manager.running,
            "worker_alive": buffer_manager.worker_thread.is_alive() if buffer_manager.worker_thread else False
        },
        "zapi": whatsapp.health_check(),
        "database": {
            "status": "connected"
        }
    }
    
    return jsonify(health_data), 200

if __name__ == '__main__':
    # Start buffer manager
    buffer_manager.start()
    
    try:
        app.run(host='0.0.0.0', port=3000, debug=False)
    finally:
        buffer_manager.stop()
