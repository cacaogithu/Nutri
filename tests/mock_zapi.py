"""
Mock Z-API implementation for testing without hitting real API.
Stores all API calls in test_messages.json for inspection.
"""
import json
import os
import time
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_MESSAGES_FILE = TEST_DATA_DIR / "test_messages.json"

class MockZAPI:
    """Mock Z-API that simulates responses without making real API calls."""
    
    def __init__(self, simulate_delays: bool = True, error_rate: float = 0.0):
        """
        Args:
            simulate_delays: Whether to simulate network delays
            error_rate: Probability of returning an error (0.0 to 1.0)
        """
        self.simulate_delays = simulate_delays
        self.error_rate = error_rate
        self.call_history = []
        TEST_DATA_DIR.mkdir(exist_ok=True)
        self._load_history()
    
    def _load_history(self):
        """Load previous test messages from file."""
        if TEST_MESSAGES_FILE.exists():
            try:
                with open(TEST_MESSAGES_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.call_history = data.get('calls', [])
            except:
                self.call_history = []
        else:
            self.call_history = []
    
    def _save_call(self, endpoint: str, payload: Dict, response: Dict, success: bool):
        """Save API call to history file."""
        call_record = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "payload": payload,
            "response": response,
            "success": success
        }
        self.call_history.append(call_record)
        
        # Keep last 1000 calls
        if len(self.call_history) > 1000:
            self.call_history = self.call_history[-1000:]
        
        # Save to file
        with open(TEST_MESSAGES_FILE, 'w', encoding='utf-8') as f:
            json.dump({"calls": self.call_history}, f, indent=2, ensure_ascii=False)
    
    def _simulate_delay(self, min_ms: int = 50, max_ms: int = 200):
        """Simulate network delay."""
        if self.simulate_delays:
            import random
            delay = random.uniform(min_ms / 1000, max_ms / 1000)
            time.sleep(delay)
    
    def _should_error(self) -> bool:
        """Determine if this call should return an error."""
        import random
        return random.random() < self.error_rate
    
    def send_text(self, phone: str, message: str) -> Dict:
        """Mock send-text endpoint."""
        self._simulate_delay()
        
        payload = {
            "phone": phone,
            "message": message
        }
        
        if self._should_error():
            response = {
                "success": False,
                "error": "Mock API error: Rate limit exceeded",
                "error_code": "RATE_LIMIT"
            }
            self._save_call("/send-text", payload, response, False)
            return response
        
        response = {
            "success": True,
            "data": {
                "messageId": f"mock_msg_{int(time.time() * 1000)}",
                "phone": phone,
                "status": "sent",
                "timestamp": datetime.now().isoformat()
            }
        }
        self._save_call("/send-text", payload, response, True)
        return response
    
    def send_link(self, phone: str, message: str, image_url: str, link_url: str) -> Dict:
        """Mock send-link endpoint."""
        self._simulate_delay()
        
        payload = {
            "phone": phone,
            "message": message,
            "image": image_url,
            "linkUrl": link_url
        }
        
        if self._should_error():
            response = {
                "success": False,
                "error": "Mock API error: Invalid image URL",
                "error_code": "INVALID_URL"
            }
            self._save_call("/send-link", payload, response, False)
            return response
        
        response = {
            "success": True,
            "data": {
                "messageId": f"mock_link_{int(time.time() * 1000)}",
                "phone": phone,
                "status": "sent"
            }
        }
        self._save_call("/send-link", payload, response, True)
        return response
    
    def send_button_message(self, phone: str, message: str, buttons: list) -> Dict:
        """Mock send-button-list endpoint."""
        self._simulate_delay()
        
        payload = {
            "phone": phone,
            "message": message,
            "buttonList": buttons
        }
        
        if self._should_error():
            response = {
                "success": False,
                "error": "Mock API error: Too many buttons",
                "error_code": "INVALID_BUTTONS"
            }
            self._save_call("/send-button-list", payload, response, False)
            return response
        
        response = {
            "success": True,
            "data": {
                "messageId": f"mock_button_{int(time.time() * 1000)}",
                "phone": phone,
                "status": "sent"
            }
        }
        self._save_call("/send-button-list", payload, response, True)
        return response
    
    def send_typing_indicator(self, phone: str) -> Dict:
        """Mock typing indicator endpoint."""
        self._simulate_delay(min_ms=10, max_ms=50)
        
        payload = {"phone": phone}
        response = {
            "success": True,
            "data": {"status": "typing_indicator_sent"}
        }
        self._save_call("/typing", payload, response, True)
        return response
    
    def send_viewed_indicator(self, phone: str) -> Dict:
        """Mock viewed indicator endpoint."""
        self._simulate_delay(min_ms=10, max_ms=50)
        
        payload = {"phone": phone}
        response = {
            "success": True,
            "data": {"status": "viewed_indicator_sent"}
        }
        self._save_call("/viewed", payload, response, True)
        return response
    
    def send_file(self, phone: str, file_path: str, caption: str = "") -> Dict:
        """Mock send-file endpoint for PDFs."""
        self._simulate_delay(min_ms=100, max_ms=500)
        
        payload = {
            "phone": phone,
            "file": file_path,
            "caption": caption
        }
        
        if self._should_error():
            response = {
                "success": False,
                "error": "Mock API error: File too large",
                "error_code": "FILE_TOO_LARGE"
            }
            self._save_call("/send-file", payload, response, False)
            return response
        
        response = {
            "success": True,
            "data": {
                "messageId": f"mock_file_{int(time.time() * 1000)}",
                "phone": phone,
                "status": "sent"
            }
        }
        self._save_call("/send-file", payload, response, True)
        return response
    
    def get_call_history(self) -> list:
        """Get all recorded API calls."""
        return self.call_history.copy()
    
    def clear_history(self):
        """Clear call history."""
        self.call_history = []
        if TEST_MESSAGES_FILE.exists():
            TEST_MESSAGES_FILE.unlink()

# Global mock instance
_mock_instance: Optional[MockZAPI] = None

def get_mock_zapi(simulate_delays: bool = True, error_rate: float = 0.0) -> MockZAPI:
    """Get or create global mock Z-API instance."""
    global _mock_instance
    if _mock_instance is None:
        _mock_instance = MockZAPI(simulate_delays=simulate_delays, error_rate=error_rate)
    return _mock_instance


