import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import threading

class Database:
    def __init__(self, db_file: str = "data/database.json"):
        self.db_file = db_file
        self.lock = threading.Lock()
        self._ensure_data_dir()
        self._init_db()
    
    def _ensure_data_dir(self):
        os.makedirs("data", exist_ok=True)
    
    def _init_db(self):
        if not os.path.exists(self.db_file):
            initial_data = {
                "clients": {},
                "leads": {},
                "interactions": [],
                "diet_plans": {},
                "subscriptions": {}
            }
            self._save(initial_data)
    
    def _load(self) -> Dict:
        with self.lock:
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                return {
                    "clients": {},
                    "leads": {},
                    "interactions": [],
                    "diet_plans": {},
                    "subscriptions": {}
                }
    
    def _save(self, data: Dict):
        with self.lock:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_lead(self, phone: str, name: str, source: str = "whatsapp"):
        data = self._load()
        lead_id = f"lead_{phone}"
        data["leads"][lead_id] = {
            "phone": phone,
            "name": name,
            "source": source,
            "status": "new",
            "created_at": datetime.now().isoformat(),
            "agent": "sales"
        }
        self._save(data)
        return lead_id
    
    def get_lead(self, phone: str) -> Optional[Dict]:
        data = self._load()
        lead_id = f"lead_{phone}"
        return data["leads"].get(lead_id)
    
    def update_lead(self, phone: str, updates: Dict):
        data = self._load()
        lead_id = f"lead_{phone}"
        if lead_id in data["leads"]:
            data["leads"][lead_id].update(updates)
            data["leads"][lead_id]["updated_at"] = datetime.now().isoformat()
            self._save(data)
    
    def convert_lead_to_client(self, phone: str):
        data = self._load()
        lead_id = f"lead_{phone}"
        if lead_id in data["leads"]:
            lead = data["leads"][lead_id]
            client_id = f"client_{phone}"
            data["clients"][client_id] = {
                "phone": phone,
                "name": lead.get("name", ""),
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "anamnesis_completed": False,
                "diet_plan_generated": False
            }
            data["subscriptions"][client_id] = {
                "client_id": client_id,
                "price": 47.00,
                "status": "active",
                "started_at": datetime.now().isoformat()
            }
            data["leads"][lead_id]["status"] = "converted"
            self._save(data)
            return client_id
        return None
    
    def get_client(self, phone: str) -> Optional[Dict]:
        data = self._load()
        client_id = f"client_{phone}"
        return data["clients"].get(client_id)
    
    def update_client(self, phone: str, updates: Dict):
        data = self._load()
        client_id = f"client_{phone}"
        if client_id in data["clients"]:
            data["clients"][client_id].update(updates)
            data["clients"][client_id]["updated_at"] = datetime.now().isoformat()
            self._save(data)
    
    def save_anamnesis(self, phone: str, anamnesis_data: Dict):
        data = self._load()
        client_id = f"client_{phone}"
        if client_id in data["clients"]:
            data["clients"][client_id]["anamnesis"] = anamnesis_data
            data["clients"][client_id]["anamnesis_completed"] = True
            data["clients"][client_id]["anamnesis_date"] = datetime.now().isoformat()
            self._save(data)
    
    def save_diet_plan(self, phone: str, diet_plan: Dict):
        data = self._load()
        client_id = f"client_{phone}"
        plan_id = f"plan_{phone}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        data["diet_plans"][plan_id] = {
            "client_id": client_id,
            "phone": phone,
            "plan": diet_plan,
            "created_at": datetime.now().isoformat()
        }
        if client_id in data["clients"]:
            data["clients"][client_id]["diet_plan_generated"] = True
            data["clients"][client_id]["latest_plan_id"] = plan_id
        self._save(data)
        return plan_id
    
    def add_interaction(self, phone: str, agent: str, message: str, direction: str = "incoming"):
        data = self._load()
        interaction = {
            "phone": phone,
            "agent": agent,
            "message": message,
            "direction": direction,
            "timestamp": datetime.now().isoformat()
        }
        data["interactions"].append(interaction)
        self._save(data)
    
    def get_client_interactions(self, phone: str, limit: int = 50) -> List[Dict]:
        data = self._load()
        interactions = [i for i in data["interactions"] if i["phone"] == phone]
        return sorted(interactions, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def get_all_clients(self) -> List[Dict]:
        data = self._load()
        return list(data["clients"].values())
    
    def get_all_leads(self) -> List[Dict]:
        data = self._load()
        return list(data["leads"].values())
    
    def get_active_subscriptions(self) -> List[Dict]:
        data = self._load()
        return [s for s in data["subscriptions"].values() if s["status"] == "active"]
    
    def get_recent_interactions(self, limit: int = 100) -> List[Dict]:
        data = self._load()
        return sorted(data["interactions"], key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def get_conversion_stats(self) -> Dict:
        data = self._load()
        total_leads = len(data["leads"])
        converted_leads = len([l for l in data["leads"].values() if l.get("status") == "converted"])
        active_clients = len([c for c in data["clients"].values() if c.get("status") == "active"])
        active_subscriptions = len([s for s in data["subscriptions"].values() if s.get("status") == "active"])
        
        return {
            "total_leads": total_leads,
            "converted_leads": converted_leads,
            "conversion_rate": (converted_leads / total_leads * 100) if total_leads > 0 else 0,
            "active_clients": active_clients,
            "active_subscriptions": active_subscriptions,
            "monthly_revenue": active_subscriptions * 47.00
        }

db = Database()
