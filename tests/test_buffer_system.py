"""
Tests for the message buffer system.
"""
import unittest
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from database import Database
from buffer_manager import BufferManager

class TestBufferSystem(unittest.TestCase):
    
    def setUp(self):
        """Set up test database."""
        self.test_dir = tempfile.mkdtemp()
        self.db_file = os.path.join(self.test_dir, "test_db.json")
        self.db = Database(db_file=self.db_file)
        self.buffer_manager = BufferManager()
    
    def tearDown(self):
        """Clean up test database."""
        shutil.rmtree(self.test_dir)
        if self.buffer_manager.running:
            self.buffer_manager.stop()
    
    def test_add_message_to_buffer(self):
        """Test adding message to buffer."""
        phone = "+14079897162"
        message = "Test message"
        
        result = self.buffer_manager.add_message(phone, message)
        
        self.assertTrue(result["success"])
        self.assertTrue(result["buffered"])
        
        # Check buffer exists
        buffer = self.db.get_message_buffer(phone)
        self.assertIsNotNone(buffer)
        self.assertEqual(buffer["phone"], phone)
    
    def test_buffer_expiration(self):
        """Test buffer expiration detection."""
        phone = "+14079897162"
        
        # Create expired buffer
        now = datetime.now()
        expired_time = (now - timedelta(seconds=20)).isoformat()
        
        self.db.upsert_message_buffer(
            phone=phone,
            last_message_at=expired_time,
            buffer_expires_at=expired_time,
            processing=False
        )
        
        # Check expired buffers
        expired = self.db.get_expired_buffers(now.isoformat())
        self.assertEqual(len(expired), 1)
        self.assertEqual(expired[0]["phone"], phone)
    
    def test_buffer_locking(self):
        """Test buffer locking mechanism."""
        phone = "+14079897162"
        
        # Create buffer
        self.db.upsert_message_buffer(
            phone=phone,
            last_message_at=datetime.now().isoformat(),
            buffer_expires_at=(datetime.now() + timedelta(seconds=15)).isoformat(),
            processing=False
        )
        
        # Acquire lock
        success = self.db.acquire_buffer_lock(phone, "test_process")
        self.assertTrue(success)
        
        # Try to acquire again (should fail)
        success2 = self.db.acquire_buffer_lock(phone, "test_process2")
        self.assertFalse(success2)
        
        # Release lock
        self.db.release_buffer_lock(phone)
        
        # Now should be able to acquire
        success3 = self.db.acquire_buffer_lock(phone, "test_process3")
        self.assertTrue(success3)
    
    def test_message_batching(self):
        """Test that multiple messages are batched."""
        phone = "+14079897162"
        
        # Add multiple messages
        for i in range(3):
            self.buffer_manager.add_message(phone, f"Message {i}")
        
        # Check all messages are saved
        interactions = self.db.get_client_interactions(phone, limit=10)
        incoming = [i for i in interactions if i["direction"] == "incoming"]
        self.assertEqual(len(incoming), 3)
    
    def test_retry_counting(self):
        """Test retry count increment."""
        phone = "+14079897162"
        
        self.db.upsert_message_buffer(
            phone=phone,
            last_message_at=datetime.now().isoformat(),
            buffer_expires_at=datetime.now().isoformat(),
            processing=False,
            retry_count=0
        )
        
        self.db.increment_buffer_retry(phone)
        
        buffer = self.db.get_message_buffer(phone)
        self.assertEqual(buffer["retry_count"], 1)

if __name__ == '__main__':
    unittest.main()


