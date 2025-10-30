from database import db
from agent_sales import sales_agent
from agent_nutrition import nutrition_agent

class MessageRouter:
    def __init__(self):
        self.sales_agent = sales_agent
        self.nutrition_agent = nutrition_agent
    
    def route_message(self, phone: str, message: str) -> dict:
        client = db.get_client(phone)
        
        if client:
            if client.get('needs_human_support') or client.get('status') == 'pending_human':
                db.add_interaction(phone, "system", message, "incoming")
                return {
                    "success": True,
                    "routed_to": "human",
                    "message": "Esta conversa foi escalada para atendimento humano. Não enviando resposta automática."
                }
            
            return self.nutrition_agent.process_message(phone, message)
        else:
            lead = db.get_lead(phone)
            if lead and (lead.get('needs_human_support') or lead.get('status') == 'pending_human'):
                db.add_interaction(phone, "system", message, "incoming")
                return {
                    "success": True,
                    "routed_to": "human",
                    "message": "Esta conversa foi escalada para atendimento humano. Não enviando resposta automática."
                }
            
            return self.sales_agent.process_message(phone, message)
    
    def escalate_to_human(self, phone: str, reason: str = "Cliente solicitou"):
        client = db.get_client(phone)
        if client:
            db.update_client(phone, {
                "needs_human_support": True,
                "escalation_reason": reason
            })
            return True
        
        lead = db.get_lead(phone)
        if lead:
            db.update_lead(phone, {
                "needs_human_support": True,
                "escalation_reason": reason
            })
            return True
        
        return False

router = MessageRouter()
