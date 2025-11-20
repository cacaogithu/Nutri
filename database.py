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
                "subscriptions": {},
                "message_buffers": {},
                "system_alerts": [],
                "tool_executions": [],
                "pdf_documents": {},
                "approved_responses": []
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
                    "subscriptions": {},
                    "message_buffers": {},
                    "system_alerts": [],
                    "tool_executions": [],
                    "pdf_documents": {},
                    "approved_responses": []
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
    
    def add_interaction(self, phone: str, agent: str, message: str, direction: str = "incoming", metadata: Optional[Dict] = None):
        data = self._load()
        interaction = {
            "phone": phone,
            "agent": agent,
            "message": message,
            "direction": direction,
            "timestamp": datetime.now().isoformat()
        }
        if metadata:
            interaction.update(metadata)
        data["interactions"].append(interaction)
        self._save(data)
        return interaction
    
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
    
    # Message Buffer Methods
    def upsert_message_buffer(self, phone: str, last_message_at: str, buffer_expires_at: str, 
                             processing: bool = False, retry_count: int = 0):
        """Create or update message buffer."""
        data = self._load()
        if "message_buffers" not in data:
            data["message_buffers"] = {}
        
        buffer_key = f"buffer_{phone}"
        existing = data["message_buffers"].get(buffer_key, {})
        
        data["message_buffers"][buffer_key] = {
            "phone": phone,
            "last_message_at": last_message_at,
            "buffer_expires_at": buffer_expires_at,
            "processing": processing,
            "retry_count": retry_count,
            "created_at": existing.get("created_at", datetime.now().isoformat()),
            "updated_at": datetime.now().isoformat(),
            "locked_at": existing.get("locked_at"),
            "locked_by": existing.get("locked_by")
        }
        self._save(data)
    
    def get_message_buffer(self, phone: str) -> Optional[Dict]:
        """Get message buffer for phone."""
        data = self._load()
        buffer_key = f"buffer_{phone}"
        return data.get("message_buffers", {}).get(buffer_key)
    
    def delete_message_buffer(self, phone: str):
        """Delete message buffer."""
        data = self._load()
        buffer_key = f"buffer_{phone}"
        if "message_buffers" in data and buffer_key in data["message_buffers"]:
            del data["message_buffers"][buffer_key]
            self._save(data)
    
    def get_expired_buffers(self, now_iso: str) -> List[Dict]:
        """Get all expired buffers that are not processing."""
        data = self._load()
        buffers = data.get("message_buffers", {})
        now = datetime.fromisoformat(now_iso)
        
        expired = []
        for buffer in buffers.values():
            if buffer.get("processing", False):
                continue
            expires_at = datetime.fromisoformat(buffer.get("buffer_expires_at", now_iso))
            if expires_at <= now:
                expired.append(buffer)
        
        return expired
    
    def acquire_buffer_lock(self, phone: str, process_id: str) -> bool:
        """Atomically acquire lock for buffer."""
        data = self._load()
        buffer_key = f"buffer_{phone}"
        
        if "message_buffers" not in data:
            return False
        
        buffer = data["message_buffers"].get(buffer_key)
        if not buffer:
            return False
        
        # Check if already locked
        if buffer.get("processing", False):
            return False
        
        # Acquire lock
        buffer["processing"] = True
        buffer["locked_at"] = datetime.now().isoformat()
        buffer["locked_by"] = process_id
        buffer["updated_at"] = datetime.now().isoformat()
        
        self._save(data)
        return True
    
    def release_buffer_lock(self, phone: str):
        """Release lock for buffer."""
        data = self._load()
        buffer_key = f"buffer_{phone}"
        
        if "message_buffers" in data and buffer_key in data["message_buffers"]:
            buffer = data["message_buffers"][buffer_key]
            buffer["processing"] = False
            buffer["locked_at"] = None
            buffer["locked_by"] = None
            buffer["updated_at"] = datetime.now().isoformat()
            self._save(data)
    
    def increment_buffer_retry(self, phone: str):
        """Increment retry count for buffer."""
        data = self._load()
        buffer_key = f"buffer_{phone}"
        
        if "message_buffers" in data and buffer_key in data["message_buffers"]:
            buffer = data["message_buffers"][buffer_key]
            buffer["retry_count"] = buffer.get("retry_count", 0) + 1
            buffer["last_retry_at"] = datetime.now().isoformat()
            buffer["updated_at"] = datetime.now().isoformat()
            self._save(data)
    
    def get_messages_since(self, phone: str, since_iso: str) -> List[Dict]:
        """Get all messages for phone since timestamp."""
        data = self._load()
        since = datetime.fromisoformat(since_iso)
        
        messages = []
        for interaction in data.get("interactions", []):
            if interaction.get("phone") == phone:
                msg_time = datetime.fromisoformat(interaction.get("timestamp", since_iso))
                if msg_time >= since and interaction.get("direction") == "incoming":
                    messages.append(interaction)
        
        return sorted(messages, key=lambda x: x.get("timestamp", ""))
    
    def get_stuck_locks(self, threshold_iso: str) -> List[Dict]:
        """Get buffers with stuck locks."""
        data = self._load()
        threshold = datetime.fromisoformat(threshold_iso)
        stuck = []
        
        for buffer in data.get("message_buffers", {}).values():
            if buffer.get("processing", False) and buffer.get("locked_at"):
                locked_at = datetime.fromisoformat(buffer["locked_at"])
                if locked_at < threshold:
                    stuck.append(buffer)
        
        return stuck
    
    def get_unprocessed_buffers(self, threshold_iso: str) -> List[Dict]:
        """Get buffers that expired but weren't processed."""
        data = self._load()
        threshold = datetime.fromisoformat(threshold_iso)
        unprocessed = []
        
        for buffer in data.get("message_buffers", {}).values():
            if not buffer.get("processing", False):
                expires_at = datetime.fromisoformat(buffer.get("buffer_expires_at", threshold_iso))
                if expires_at < threshold:
                    unprocessed.append(buffer)
        
        return unprocessed
    
    def get_high_retry_buffers(self, min_retries: int) -> List[Dict]:
        """Get buffers with high retry counts."""
        data = self._load()
        return [
            buffer for buffer in data.get("message_buffers", {}).values()
            if buffer.get("retry_count", 0) >= min_retries
        ]
    
    # System Alerts Methods
    def create_alert(self, type: str, phone: str, details: str):
        """Create system alert."""
        data = self._load()
        if "system_alerts" not in data:
            data["system_alerts"] = []
        
        alert = {
            "type": type,
            "phone": phone,
            "details": details,
            "created_at": datetime.now().isoformat(),
            "resolved": False
        }
        data["system_alerts"].append(alert)
        
        # Keep last 1000 alerts
        if len(data["system_alerts"]) > 1000:
            data["system_alerts"] = data["system_alerts"][-1000:]
        
        self._save(data)
        return alert
    
    def get_alerts(self, unresolved_only: bool = True, limit: int = 100) -> List[Dict]:
        """Get system alerts."""
        data = self._load()
        alerts = data.get("system_alerts", [])
        
        if unresolved_only:
            alerts = [a for a in alerts if not a.get("resolved", False)]
        
        return sorted(alerts, key=lambda x: x.get("created_at", ""), reverse=True)[:limit]
    
    # Tool Executions Methods
    def log_tool_execution(self, phone: str, tool_name: str, input_data: Dict, output_data: Dict):
        """Log tool execution for audit."""
        data = self._load()
        if "tool_executions" not in data:
            data["tool_executions"] = []
        
        execution = {
            "phone": phone,
            "tool_name": tool_name,
            "input": input_data,
            "output": output_data,
            "timestamp": datetime.now().isoformat()
        }
        data["tool_executions"].append(execution)
        
        # Keep last 5000 executions
        if len(data["tool_executions"]) > 5000:
            data["tool_executions"] = data["tool_executions"][-5000:]
        
        self._save(data)
        return execution
    
    # PDF Documents Methods
    def save_pdf_document(self, phone: str, plan_id: str, file_path: str):
        """Save PDF document record."""
        data = self._load()
        if "pdf_documents" not in data:
            data["pdf_documents"] = {}
        
        doc_key = f"pdf_{phone}_{plan_id}"
        data["pdf_documents"][doc_key] = {
            "phone": phone,
            "plan_id": plan_id,
            "file_path": file_path,
            "created_at": datetime.now().isoformat(),
            "sent_at": None
        }
        self._save(data)
        return doc_key
    
    def mark_pdf_sent(self, phone: str, plan_id: str):
        """Mark PDF as sent."""
        data = self._load()
        doc_key = f"pdf_{phone}_{plan_id}"
        if "pdf_documents" in data and doc_key in data["pdf_documents"]:
            data["pdf_documents"][doc_key]["sent_at"] = datetime.now().isoformat()
            self._save(data)
    
    def get_pdf_documents(self, phone: Optional[str] = None) -> List[Dict]:
        """Get PDF documents, optionally filtered by phone."""
        data = self._load()
        docs = list(data.get("pdf_documents", {}).values())
        
        if phone:
            docs = [d for d in docs if d.get("phone") == phone]
        
        return sorted(docs, key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Approved Responses Methods
    def save_approved_response(self, phone: str, context: str, response: str, agent: str):
        """Save approved response for learning."""
        data = self._load()
        if "approved_responses" not in data:
            data["approved_responses"] = []
        
        approved = {
            "phone": phone,
            "context": context,
            "response": response,
            "agent": agent,
            "approved_at": datetime.now().isoformat()
        }
        data["approved_responses"].append(approved)
        self._save(data)
        return approved
    
    def get_approved_responses(self, agent: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get approved responses, optionally filtered by agent."""
        data = self._load()
        responses = data.get("approved_responses", [])
        
        if agent:
            responses = [r for r in responses if r.get("agent") == agent]
        
        return sorted(responses, key=lambda x: x.get("approved_at", ""), reverse=True)[:limit]

db = Database()
