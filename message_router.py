from database import db
from agent_orchestrator import orchestrator

class MessageRouter:
    """
    Routes messages to appropriate agents via the orchestrator.
    """
    
    def __init__(self):
        self.orchestrator = orchestrator
    
    def route_message(self, phone: str, message: str, context: dict = None) -> dict:
        """
        Route message through orchestrator to appropriate agent.
        
        Args:
            phone: Phone number
            message: Message text (may be batched from buffer)
            context: Optional context from buffer system
        
        Returns:
            Dict with response and routing info
        """
        return self.orchestrator.route_to_agent(phone, message, context)
    
    def escalate_to_human(self, phone: str, reason: str = "Cliente solicitou"):
        """
        Escalate conversation to human support.
        
        Args:
            phone: Phone number
            reason: Escalation reason
        
        Returns:
            bool: Success status
        """
        # Use tool system for escalation
        result = self.orchestrator.execute_tool("escalate_to_human", phone, reason=reason)
        return result.get("success", False)

router = MessageRouter()
