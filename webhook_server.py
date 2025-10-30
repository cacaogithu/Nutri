from flask import Flask, request, jsonify
from agent_sales import sales_agent
from agent_nutrition import nutrition_agent
from database import db
import threading

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        phone = data.get('phone', '')
        message = data.get('message', {}).get('text', '')
        
        if not phone or not message:
            return jsonify({"error": "Missing phone or message"}), 400
        
        phone = phone.replace('+', '').replace(' ', '').replace('-', '')
        
        def process_async():
            client = db.get_client(phone)
            
            if client:
                nutrition_agent.process_message(phone, message)
            else:
                sales_agent.process_message(phone, message)
        
        thread = threading.Thread(target=process_async)
        thread.start()
        
        return jsonify({"success": True, "message": "Processing"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/webhook/status', methods=['GET'])
def status():
    return jsonify({
        "status": "online",
        "service": "WhatsApp AI Nutrition Agent"
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
