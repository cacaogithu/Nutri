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
    
    @staticmethod
    def approve_response(phone: str, interaction_timestamp: str, agent: str, context: str = ""):
        """
        Approve an AI response for supervised learning.
        
        Args:
            phone: Phone number
            interaction_timestamp: Timestamp of the interaction to approve
            agent: Agent type (sales, nutrition)
            context: Optional context about why this is a good response
        
        Returns:
            Dict with success status
        """
        try:
            # Get the interaction
            interactions = db.get_client_interactions(phone, limit=1000)
            interaction = None
            
            for i in interactions:
                if i.get("timestamp") == interaction_timestamp and i.get("direction") == "outgoing":
                    interaction = i
                    break
            
            if not interaction:
                return {
                    "success": False,
                    "error": "Interaction not found"
                }
            
            # Get conversation context
            if not context:
                # Build context from recent interactions
                recent = [i for i in interactions if i.get("timestamp") <= interaction_timestamp][-5:]
                context = "\n".join([
                    f"{'User' if i['direction'] == 'incoming' else 'Agent'}: {i.get('message', '')[:200]}"
                    for i in recent
                ])
            
            # Save approved response
            db.save_approved_response(
                phone=phone,
                context=context,
                response=interaction.get("message", ""),
                agent=agent
            )
            
            return {
                "success": True,
                "message": "Response approved and saved for learning"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def get_approved_responses(agent: str = None, limit: int = 50):
        """Get approved responses for learning."""
        return db.get_approved_responses(agent=agent, limit=limit)

admin = AdminActions()
