import requests
import logging
from typing import Optional, Dict
from config import Z_API_BASE_URL, TESTING_MODE, ALLOWED_PHONE_NUMBER

logger = logging.getLogger(__name__)

# Import mock if in testing mode
if TESTING_MODE:
    from tests.mock_zapi import get_mock_zapi

class WhatsAppAPI:
    def __init__(self):
        self.base_url = Z_API_BASE_URL
        self.testing_mode = TESTING_MODE
        if TESTING_MODE:
            self.mock = get_mock_zapi()
            logger.info("🧪 Testing mode enabled - using mock Z-API")
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number to E.164 format."""
        phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if not phone.startswith('+'):
            # Assume Brazilian number if no country code
            if phone.startswith('55'):
                phone = f"+{phone}"
            else:
                phone = f"+{phone}"
        return phone
    
    def _check_access_control(self, phone: str) -> bool:
        """Check if phone number is allowed."""
        normalized = self._normalize_phone(phone)
        allowed = self._normalize_phone(ALLOWED_PHONE_NUMBER)
        
        if normalized != allowed:
            logger.warning(f"🚫 Access denied for {normalized} (allowed: {allowed})")
            return False
        return True
    
    def send_text(self, phone: str, message: str) -> Dict:
        """Send text message via Z-API."""
        phone = self._normalize_phone(phone)
        
        # Access control
        if not self._check_access_control(phone):
            return {
                "success": False,
                "error": "Access denied: Phone number not in allow-list"
            }
        
        if self.testing_mode:
            return self.mock.send_text(phone, message)
        
        url = f"{self.base_url}/send-text"
        payload = {
            "phone": phone,
            "message": message
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            logger.error(f"Z-API error: {e}")
            return {"success": False, "error": str(e)}
    
    def send_link(self, phone: str, message: str, image_url: str, link_url: str) -> Dict:
        """Send link message via Z-API."""
        phone = self._normalize_phone(phone)
        
        if not self._check_access_control(phone):
            return {
                "success": False,
                "error": "Access denied: Phone number not in allow-list"
            }
        
        if self.testing_mode:
            return self.mock.send_link(phone, message, image_url, link_url)
        
        url = f"{self.base_url}/send-link"
        payload = {
            "phone": phone,
            "message": message,
            "image": image_url,
            "linkUrl": link_url
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            logger.error(f"Z-API error: {e}")
            return {"success": False, "error": str(e)}
    
    def send_button_message(self, phone: str, message: str, buttons: list) -> Dict:
        """Send button message via Z-API."""
        phone = self._normalize_phone(phone)
        
        if not self._check_access_control(phone):
            return {
                "success": False,
                "error": "Access denied: Phone number not in allow-list"
            }
        
        if self.testing_mode:
            return self.mock.send_button_message(phone, message, buttons)
        
        url = f"{self.base_url}/send-button-list"
        payload = {
            "phone": phone,
            "message": message,
            "buttonList": buttons
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            logger.error(f"Z-API error: {e}")
            return {"success": False, "error": str(e)}
    
    def send_typing_indicator(self, phone: str) -> Dict:
        """Send typing indicator via Z-API."""
        phone = self._normalize_phone(phone)
        
        if not self._check_access_control(phone):
            return {"success": False, "error": "Access denied"}
        
        if self.testing_mode:
            return self.mock.send_typing_indicator(phone)
        
        # Try Z-API typing endpoint (may not be available in all plans)
        url = f"{self.base_url}/typing"
        payload = {"phone": phone}
        
        try:
            response = requests.post(url, json=payload, timeout=5)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException:
            # If endpoint doesn't exist, just log and return success
            logger.debug("Typing indicator endpoint not available")
            return {"success": True, "data": {"status": "simulated"}}
    
    def send_viewed_indicator(self, phone: str) -> Dict:
        """Send viewed indicator via Z-API."""
        phone = self._normalize_phone(phone)
        
        if not self._check_access_control(phone):
            return {"success": False, "error": "Access denied"}
        
        if self.testing_mode:
            return self.mock.send_viewed_indicator(phone)
        
        # Try Z-API viewed endpoint (may not be available in all plans)
        url = f"{self.base_url}/viewed"
        payload = {"phone": phone}
        
        try:
            response = requests.post(url, json=payload, timeout=5)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException:
            # If endpoint doesn't exist, just log and return success
            logger.debug("Viewed indicator endpoint not available")
            return {"success": True, "data": {"status": "simulated"}}
    
    def send_file(self, phone: str, file_path: str, caption: str = "") -> Dict:
        """Send file (PDF) via Z-API."""
        phone = self._normalize_phone(phone)
        
        if not self._check_access_control(phone):
            return {
                "success": False,
                "error": "Access denied: Phone number not in allow-list"
            }
        
        if self.testing_mode:
            return self.mock.send_file(phone, file_path, caption)
        
        url = f"{self.base_url}/send-file"
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {
                    "phone": phone,
                    "caption": caption
                }
                response = requests.post(url, files=files, data=data, timeout=30)
                response.raise_for_status()
                return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            logger.error(f"Z-API file send error: {e}")
            return {"success": False, "error": str(e)}
    
    def health_check(self) -> Dict:
        """Check Z-API connectivity and credentials."""
        if self.testing_mode:
            return {"success": True, "mode": "testing", "message": "Mock Z-API active"}
        
        try:
            # Try a lightweight endpoint to verify credentials
            url = f"{self.base_url}/status"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return {"success": True, "message": "Z-API connection healthy"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

whatsapp = WhatsAppAPI()
