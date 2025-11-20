"""
Message Buffer Manager - Implements 15-second sliding window buffer
for batching rapid messages before AI processing.
"""
import threading
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from database import db
from config import (
    BUFFER_WINDOW_SECONDS,
    BUFFER_CHECK_INTERVAL_SECONDS,
    BUFFER_LOCK_TIMEOUT_SECONDS
)

logger = logging.getLogger(__name__)

class BufferManager:
    """Manages message buffers with sliding window and locking mechanism."""
    
    def __init__(self):
        self.running = False
        self.worker_thread: Optional[threading.Thread] = None
        self.health_check_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
    
    def start(self):
        """Start background workers."""
        if self.running:
            return
        
        self.running = True
        
        # Start buffer checker worker
        self.worker_thread = threading.Thread(target=self._buffer_checker_worker, daemon=True)
        self.worker_thread.start()
        
        # Start health check worker
        self.health_check_thread = threading.Thread(target=self._health_check_worker, daemon=True)
        self.health_check_thread.start()
        
        logger.info("Buffer manager started")
    
    def stop(self):
        """Stop background workers."""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=2)
        if self.health_check_thread:
            self.health_check_thread.join(timeout=2)
        logger.info("Buffer manager stopped")
    
    def add_message(self, phone: str, message: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Add message to buffer. Returns immediately with success status.
        This allows webhook to respond quickly to Z-API.
        """
        phone = self._normalize_phone(phone)
        now = datetime.now()
        expires_at = now + timedelta(seconds=BUFFER_WINDOW_SECONDS)
        
        # Get or create buffer
        buffer_data = db.get_message_buffer(phone)
        
        if buffer_data:
            # Check for stuck buffer (retry logic)
            created_at = datetime.fromisoformat(buffer_data.get('created_at', now.isoformat()))
            age_seconds = (now - created_at).total_seconds()
            
            if age_seconds > 120:  # 2 minutes old
                logger.warning(f"⚠️ Stuck buffer detected for {phone}, resetting")
                retry_count = buffer_data.get('retry_count', 0) + 1
                db.create_alert(
                    type='buffer_stuck',
                    phone=phone,
                    details=f"Buffer stuck for {age_seconds:.0f}s, retry #{retry_count}"
                )
            else:
                retry_count = buffer_data.get('retry_count', 0)
        else:
            retry_count = 0
        
        # Update or create buffer with new expiration
        db.upsert_message_buffer(
            phone=phone,
            last_message_at=now.isoformat(),
            buffer_expires_at=expires_at.isoformat(),
            processing=False,
            retry_count=retry_count
        )
        
        # Save message to database
        db.add_interaction(phone, "user", message, "incoming", metadata=metadata)
        
        logger.debug(f"Message buffered for {phone}, expires at {expires_at.isoformat()}")
        
        return {
            "success": True,
            "buffered": True,
            "phone": phone,
            "expires_at": expires_at.isoformat()
        }
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number."""
        phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if not phone.startswith('+'):
            if phone.startswith('55'):
                phone = f"+{phone}"
            else:
                phone = f"+{phone}"
        return phone
    
    def _buffer_checker_worker(self):
        """Background worker that checks for expired buffers every N seconds."""
        while self.running:
            try:
                self._check_expired_buffers()
            except Exception as e:
                logger.error(f"Error in buffer checker: {e}")
            
            time.sleep(BUFFER_CHECK_INTERVAL_SECONDS)
    
    def _check_expired_buffers(self):
        """Check for expired buffers and process them."""
        now = datetime.now()
        expired_buffers = db.get_expired_buffers(now.isoformat())
        
        for buffer in expired_buffers:
            phone = buffer['phone']
            
            # Try to acquire lock
            if not self._acquire_lock(phone):
                continue  # Another process is handling it
            
            try:
                # Get all messages for this phone since buffer started
                buffer_created = datetime.fromisoformat(buffer.get('created_at', now.isoformat()))
                messages = db.get_messages_since(phone, buffer_created.isoformat())
                
                if messages:
                    # Process batched messages
                    self._process_batched_messages(phone, messages)
                
                # Clear buffer
                db.delete_message_buffer(phone)
                
            except Exception as e:
                logger.error(f"Error processing buffer for {phone}: {e}")
                # Release lock on error
                db.release_buffer_lock(phone)
                # Increment retry count
                db.increment_buffer_retry(phone)
    
    def _acquire_lock(self, phone: str) -> bool:
        """Atomically acquire lock for buffer processing."""
        buffer = db.get_message_buffer(phone)
        if not buffer:
            return False
        
        # Check if already locked
        if buffer.get('processing', False):
            locked_at = buffer.get('locked_at')
            if locked_at:
                lock_age = (datetime.now() - datetime.fromisoformat(locked_at)).total_seconds()
                if lock_age > BUFFER_LOCK_TIMEOUT_SECONDS:
                    logger.warning(f"⚠️ Stuck lock detected for {phone} ({lock_age:.0f}s), forcing unlock")
                    db.release_buffer_lock(phone)
                    db.create_alert(
                        type='buffer_stuck_lock',
                        phone=phone,
                        details=f"Lock stuck for {lock_age:.0f}s, forced unlock"
                    )
                else:
                    return False  # Still locked
        
        # Try to acquire lock
        process_id = f"process_{int(time.time() * 1000)}"
        success = db.acquire_buffer_lock(phone, process_id)
        
        if success:
            logger.debug(f"🔒 Lock acquired for {phone} by {process_id}")
        
        return success
    
    def _process_batched_messages(self, phone: str, messages: List[Dict]):
        """Process batched messages through message router."""
        from message_router import router
        from whatsapp_api import whatsapp
        
        # Combine messages into single text with timestamps
        message_text = "\n".join([
            f"[{msg.get('timestamp', '')[:19]}] {msg.get('message', '')}"
            for msg in messages
        ])
        
        # Send typing indicator
        whatsapp.send_typing_indicator(phone)
        
        logger.info(f"📦 Processing {len(messages)} batched messages for {phone}")
        
        # Route through message router (which will call appropriate agent)
        try:
            result = router.route_message(phone, message_text)
            
            # Send viewed indicator after response
            if result.get('success'):
                whatsapp.send_viewed_indicator(phone)
            
        except Exception as e:
            logger.error(f"Error routing batched messages for {phone}: {e}")
            db.create_alert(
                type='buffer_processing_error',
                phone=phone,
                details=f"Error processing batch: {str(e)}"
            )
    
    def _health_check_worker(self):
        """Background worker that runs health checks every 5 minutes."""
        while self.running:
            try:
                time.sleep(300)  # 5 minutes
                self._run_health_checks()
            except Exception as e:
                logger.error(f"Error in health check worker: {e}")
    
    def _run_health_checks(self):
        """Run health checks to detect and fix issues."""
        now = datetime.now()
        five_minutes_ago = (now - timedelta(minutes=5)).isoformat()
        one_minute_ago = (now - timedelta(minutes=1)).isoformat()
        
        # Check for stuck locks (> 5 minutes)
        stuck_locks = db.get_stuck_locks(five_minutes_ago)
        for lock in stuck_locks:
            logger.warning(f"🔓 Force unlocking stuck lock for {lock['phone']}")
            db.release_buffer_lock(lock['phone'])
            db.create_alert(
                type='health_check_stuck_lock',
                phone=lock['phone'],
                details="Stuck lock detected and force-unlocked"
            )
        
        # Check for unprocessed buffers (> 1 minute expired)
        unprocessed = db.get_unprocessed_buffers(one_minute_ago)
        for buffer in unprocessed:
            logger.warning(f"⚡ Force processing expired buffer for {buffer['phone']}")
            # Trigger processing by updating expires_at to now
            db.upsert_message_buffer(
                phone=buffer['phone'],
                last_message_at=buffer.get('last_message_at', now.isoformat()),
                buffer_expires_at=now.isoformat(),
                processing=False,
                retry_count=buffer.get('retry_count', 0)
            )
            db.create_alert(
                type='health_check_unprocessed',
                phone=buffer['phone'],
                details="Expired buffer force-processed"
            )
        
        # Check for high retry counts (>= 5)
        high_retries = db.get_high_retry_buffers(5)
        for buffer in high_retries:
            db.create_alert(
                type='health_check_high_retries',
                phone=buffer['phone'],
                details=f"Buffer has {buffer.get('retry_count', 0)} retries, needs manual review"
            )

# Global instance
buffer_manager = BufferManager()


