import requests
from typing import Optional, Dict
from config import Z_API_BASE_URL

class WhatsAppAPI:
    def __init__(self):
        self.base_url = Z_API_BASE_URL
    
    def send_text(self, phone: str, message: str) -> Dict:
        url = f"{self.base_url}/send-text"
        
        if not phone.startswith('+'):
            phone = f"+{phone}"
        
        payload = {
            "phone": phone,
            "message": message
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def send_link(self, phone: str, message: str, image_url: str, link_url: str) -> Dict:
        url = f"{self.base_url}/send-link"
        
        if not phone.startswith('+'):
            phone = f"+{phone}"
        
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
            return {"success": False, "error": str(e)}
    
    def send_button_message(self, phone: str, message: str, buttons: list) -> Dict:
        url = f"{self.base_url}/send-button-list"
        
        if not phone.startswith('+'):
            phone = f"+{phone}"
        
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
            return {"success": False, "error": str(e)}

whatsapp = WhatsAppAPI()
