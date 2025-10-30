from database import db
from whatsapp_api import whatsapp
from message_router import router

class AdminActions:
    
    @staticmethod
    def escalate_to_human(phone: str, reason: str = "Solicitado pelo admin"):
        success = router.escalate_to_human(phone, reason)
        if success:
            message = f"🔔 Sua conversa foi transferida para atendimento humano. Um especialista entrará em contato em breve.\n\nMotivo: {reason}"
            whatsapp.send_text(phone, message)
            db.add_interaction(phone, "system", message, "outgoing")
            return {"success": True, "message": "Cliente escalado para atendimento humano"}
        return {"success": False, "error": "Cliente não encontrado"}
    
    @staticmethod
    def send_manual_message(phone: str, message: str, agent: str = "human"):
        result = whatsapp.send_text(phone, message)
        if result.get("success"):
            db.add_interaction(phone, agent, message, "outgoing")
            return {"success": True, "message": "Mensagem enviada com sucesso"}
        return {"success": False, "error": result.get("error", "Erro ao enviar mensagem")}
    
    @staticmethod
    def get_client_full_history(phone: str):
        client = db.get_client(phone)
        if not client:
            client = db.get_lead(phone)
        
        interactions = db.get_client_interactions(phone, limit=1000)
        
        return {
            "client_data": client,
            "interactions": interactions
        }
    
    @staticmethod
    def mark_client_inactive(phone: str):
        db.update_client(phone, {"status": "inactive"})
        return {"success": True, "message": "Cliente marcado como inativo"}
    
    @staticmethod
    def reset_anamnesis(phone: str):
        db.update_client(phone, {
            "anamnesis": {},
            "anamnesis_completed": False
        })
        message = "Sua anamnese foi reiniciada. Vamos começar novamente! Qual é o seu nome completo?"
        whatsapp.send_text(phone, message)
        db.add_interaction(phone, "nutrition", message, "outgoing")
        return {"success": True, "message": "Anamnese reiniciada"}

admin = AdminActions()
