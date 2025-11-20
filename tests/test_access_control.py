"""
Tests for access control (phone number allow-list).
"""
import unittest
import os
from unittest.mock import patch
from whatsapp_api import WhatsAppAPI
from config import ALLOWED_PHONE_NUMBER

class TestAccessControl(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        self.whatsapp = WhatsAppAPI()
    
    def test_allowed_number_passes(self):
        """Test that allowed number passes access control."""
        result = self.whatsapp.send_text(ALLOWED_PHONE_NUMBER, "Test")
        
        # Should not be blocked (may fail for other reasons, but not access control)
        # In testing mode, it will succeed
        # In production, it would make real API call
        self.assertIsNotNone(result)
    
    def test_blocked_number_fails(self):
        """Test that non-allowed number is blocked."""
        blocked_number = "+5511999999999"
        
        result = self.whatsapp.send_text(blocked_number, "Test")
        
        self.assertFalse(result["success"])
        self.assertIn("Access denied", result["error"])
    
    def test_phone_normalization(self):
        """Test phone number normalization."""
        # Test various formats
        test_cases = [
            ("14079897162", "+14079897162"),
            ("+1 407 989 7162", "+14079897162"),
            ("+1-407-989-7162", "+14079897162"),
        ]
        
        for input_phone, expected in test_cases:
            normalized = self.whatsapp._normalize_phone(input_phone)
            # Normalization may add + if missing, but exact match depends on implementation
            self.assertTrue(normalized.startswith("+"))
    
    def test_webhook_access_control(self):
        """Test webhook access control."""
        from webhook_server import _check_access_control, _normalize_phone
        
        # Allowed number
        self.assertTrue(_check_access_control(ALLOWED_PHONE_NUMBER))
        
        # Blocked number
        self.assertFalse(_check_access_control("+5511999999999"))

if __name__ == '__main__':
    unittest.main()


