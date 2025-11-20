"""
Multi-Agent Orchestrator - Coordinates multiple specialized agents
with shared memory and tool capabilities.
"""
import logging
from typing import Dict, Optional, List
from database import db
from agent_tools import agent_tools
from agent_sales import sales_agent
from agent_nutrition import nutrition_agent

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """
    Orchestrates multiple agents with shared context and tool access.
    """
    
    def __init__(self):
        self.agents = {
            "sales": sales_agent,
            "nutrition": nutrition_agent,
            # Future agents can be added here:
            # "billing": billing_agent,
            # "compliance": compliance_agent,
        }
        self.shared_memory = {}  # Shared context across agents
    
    def get_agent(self, agent_type: str):
        """Get agent by type."""
        return self.agents.get(agent_type)
    
    def route_to_agent(self, phone: str, message: str, context: Optional[Dict] = None) -> Dict:
        """
        Route message to appropriate agent based on client/lead status.
        
        Args:
            phone: Phone number
            message: Message text
            context: Additional context (from buffer, etc.)
        
        Returns:
            Dict with response and metadata
        """
        # Check client status
        client = db.get_client(phone)
        
        if client:
            # Client exists - route to nutrition agent
            agent_type = "nutrition"
            agent = self.agents["nutrition"]
            
            # Check for escalation
            if client.get('needs_human_support') or client.get('status') == 'pending_human':
                return {
                    "success": True,
                    "routed_to": "human",
                    "message": "Esta conversa foi escalada para atendimento humano."
                }
        else:
            # No client - route to sales agent
            agent_type = "sales"
            agent = self.agents["sales"]
            
            # Check lead escalation
            lead = db.get_lead(phone)
            if lead and (lead.get('needs_human_support') or lead.get('status') == 'pending_human'):
                return {
                    "success": True,
                    "routed_to": "human",
                    "message": "Esta conversa foi escalada para atendimento humano."
                }
        
        # Process with agent
        try:
            result = agent.process_message(phone, message)
            result["agent_type"] = agent_type
            return result
        except Exception as e:
            logger.error(f"Agent processing error ({agent_type}): {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_type": agent_type
            }
    
    def handoff_agent(self, phone: str, from_agent: str, to_agent: str, reason: str = ""):
        """
        Hand off conversation from one agent to another.
        
        Args:
            phone: Phone number
            from_agent: Current agent type
            to_agent: Target agent type
            reason: Reason for handoff
        """
        if to_agent not in self.agents:
            logger.error(f"Invalid agent for handoff: {to_agent}")
            return False
        
        # Update client/lead record
        client = db.get_client(phone)
        if client:
            db.update_client(phone, {
                "agent": to_agent,
                "last_handoff": {
                    "from": from_agent,
                    "to": to_agent,
                    "reason": reason,
                    "timestamp": db._load().get("timestamp", "")
                }
            })
        else:
            lead = db.get_lead(phone)
            if lead:
                db.update_lead(phone, {
                    "agent": to_agent,
                    "last_handoff": {
                        "from": from_agent,
                        "to": to_agent,
                        "reason": reason
                    }
                })
        
        logger.info(f"🔄 Handoff: {phone} from {from_agent} to {to_agent} ({reason})")
        return True
    
    def execute_tool(self, tool_name: str, phone: str, **kwargs) -> Dict:
        """Execute a tool through the tool registry."""
        return agent_tools.execute_tool(tool_name, phone, **kwargs)
    
    def get_shared_context(self, phone: str) -> Dict:
        """Get shared context for a phone number."""
        return self.shared_memory.get(phone, {})
    
    def update_shared_context(self, phone: str, updates: Dict):
        """Update shared context for a phone number."""
        if phone not in self.shared_memory:
            self.shared_memory[phone] = {}
        self.shared_memory[phone].update(updates)
    
    def get_conversation_summary(self, phone: str, limit: int = 20) -> str:
        """Get conversation summary for context."""
        interactions = db.get_client_interactions(phone, limit=limit)
        
        summary = []
        for interaction in reversed(interactions):
            direction = interaction.get("direction", "incoming")
            agent = interaction.get("agent", "unknown")
            message = interaction.get("message", "")[:100]  # Truncate long messages
            
            if direction == "incoming":
                summary.append(f"User: {message}")
            else:
                summary.append(f"{agent.capitalize()}: {message}")
        
        return "\n".join(summary)

# Global instance
orchestrator = AgentOrchestrator()


