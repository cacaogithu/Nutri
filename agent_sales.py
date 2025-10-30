from ai_agent import AIAgent
from database import db
from whatsapp_api import whatsapp
from knowledge_base import SALES_METHODOLOGY
import json

class SalesAgent:
    def __init__(self):
        self.agent = AIAgent("sales")
        self.system_prompt = f"""Você é um agente de vendas especializado em nutrição e bem-estar.
Seu objetivo é apresentar nossa metodologia nutricional personalizada e converter leads em clientes pagantes.

METODOLOGIA:
{SALES_METHODOLOGY}

INSTRUÇÕES:
1. Seja amigável, profissional e empático
2. Responda perguntas sobre a metodologia de forma clara e convincente
3. Destaque os benefícios: acompanhamento 24/7, planos personalizados, suporte contínuo
4. Quando o lead demonstrar interesse, conduza para o fechamento da assinatura de R$ 47/mês
5. Mantenha respostas concisas (máximo 3-4 parágrafos no WhatsApp)
6. Use linguagem brasileira natural e acessível
7. Se o cliente aceitar assinar, informe que ele será transferido para o nutricionista personalizado

IMPORTANTE: Você deve identificar se a mensagem é:
- Uma saudação inicial (ofereça informações sobre o serviço)
- Uma dúvida sobre a metodologia (explique com entusiasmo)
- Um interesse em assinar (conduza para o fechamento)
- Uma confirmação de assinatura (parabenize e informe próximos passos)

Retorne SEMPRE em formato JSON com:
{{"response": "sua resposta aqui", "action": "continue|convert|escalate", "reason": "explicação da ação"}}
"""
    
    def process_message(self, phone: str, message: str) -> dict:
        lead = db.get_lead(phone)
        
        if not lead:
            lead_id = db.add_lead(phone, "Novo Lead", "whatsapp")
            lead = db.get_lead(phone)
        
        db.add_interaction(phone, "sales", message, "incoming")
        
        recent_interactions = db.get_client_interactions(phone, limit=10)
        context = "\n".join([
            f"{'Cliente' if i['direction'] == 'incoming' else 'Agente'}: {i['message']}"
            for i in reversed(recent_interactions[-5:])
        ])
        
        response_json = self.agent.generate_structured_response(
            self.system_prompt,
            message,
            context=f"Histórico recente:\n{context}"
        )
        
        try:
            result = json.loads(response_json)
            response_text = result.get("response", "")
            action = result.get("action", "continue")
            
            if action == "convert":
                client_id = db.convert_lead_to_client(phone)
                if client_id:
                    response_text += "\n\n✅ Seja bem-vindo(a)! Sua assinatura está ativa. Agora vou te conectar com seu nutricionista personalizado que irá iniciar sua avaliação nutricional completa."
                    db.update_client(phone, {"agent": "nutrition"})
            
            db.add_interaction(phone, "sales", response_text, "outgoing")
            
            whatsapp.send_text(phone, response_text)
            
            return {
                "success": True,
                "response": response_text,
                "action": action
            }
            
        except json.JSONDecodeError:
            fallback_response = "Obrigado pelo contato! Nossa metodologia oferece acompanhamento nutricional personalizado por apenas R$ 47/mês. Gostaria de saber mais detalhes?"
            whatsapp.send_text(phone, fallback_response)
            db.add_interaction(phone, "sales", fallback_response, "outgoing")
            return {"success": True, "response": fallback_response, "action": "continue"}

sales_agent = SalesAgent()
