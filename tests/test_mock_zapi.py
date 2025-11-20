"""
Tests for Z-API mock system.
"""
import unittest
import os
import tempfile
import shutil
from tests.mock_zapi import MockZAPI, get_mock_zapi

class TestMockZAPI(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        # Override test data directory
        import tests.mock_zapi as mock_module
        mock_module.TEST_DATA_DIR = os.path.join(self.test_dir, "test_data")
        mock_module.TEST_MESSAGES_FILE = os.path.join(mock_module.TEST_DATA_DIR, "test_messages.json")
        
        self.mock = MockZAPI(simulate_delays=False, error_rate=0.0)
    
    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.test_dir)
        self.mock.clear_history()
    
    def test_send_text(self):
        """Test sending text message."""
        result = self.mock.send_text("+14079897162", "Test message")
        
        self.assertTrue(result["success"])
        self.assertIn("data", result)
        self.assertIn("messageId", result["data"])
    
    def test_send_text_with_error(self):
        """Test error simulation."""
        error_mock = MockZAPI(simulate_delays=False, error_rate=1.0)
        result = error_mock.send_text("+14079897162", "Test")
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)
    
    def test_call_history(self):
        """Test that calls are recorded in history."""
        self.mock.send_text("+14079897162", "Message 1")
        self.mock.send_text("+14079897162", "Message 2")
        
        history = self.mock.get_call_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["endpoint"], "/send-text")
        self.assertEqual(history[1]["endpoint"], "/send-text")
    
    def test_send_file(self):
        """Test sending file."""
        # Create dummy file
        test_file = os.path.join(self.test_dir, "test.pdf")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        result = self.mock.send_file("+14079897162", test_file, "Test PDF")
        
        self.assertTrue(result["success"])
        self.assertIn("messageId", result["data"])
    
    def test_typing_indicator(self):
        """Test typing indicator."""
        result = self.mock.send_typing_indicator("+14079897162")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["status"], "typing_indicator_sent")
    
    def test_viewed_indicator(self):
        """Test viewed indicator."""
        result = self.mock.send_viewed_indicator("+14079897162")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["status"], "viewed_indicator_sent")

if __name__ == '__main__':
    unittest.main()


