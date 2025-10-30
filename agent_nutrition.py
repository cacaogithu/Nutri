from ai_agent import AIAgent
from database import db
from whatsapp_api import whatsapp
from knowledge_base import ANAMNESIS_QUESTIONS, BRAZILIAN_FOODS_SAMPLE, get_all_anamnesis_questions
import json

class NutritionAgent:
    def __init__(self):
        self.agent = AIAgent("nutrition")
        
        questions_text = "\n".join([
            f"- {q['key']}: {q['question']}"
            for q in get_all_anamnesis_questions()
        ])
        
        self.system_prompt = f"""Você é um nutricionista especializado em atendimento personalizado via WhatsApp.
Seu papel é conduzir a anamnese nutricional completa e gerar planos alimentares hiperpersonalizados.

PROCESSO DE ANAMNESE:
Você deve coletar as seguintes informações do cliente de forma conversacional e natural:

{questions_text}

INSTRUÇÕES PARA ANAMNESE:
1. Faça UMA pergunta por vez para não sobrecarregar o cliente
2. Seja empático e encorajador
3. Adapte a linguagem ao perfil do cliente
4. Valide as respostas (ex: peso e altura devem ser números razoáveis)
5. Mantenha um tom profissional mas amigável
6. Quando todas as informações forem coletadas, informe que irá gerar o plano personalizado

ALIMENTOS BRASILEIROS DISPONÍVEIS (Base TACO):
{json.dumps(BRAZILIAN_FOODS_SAMPLE, ensure_ascii=False, indent=2)}

GERAÇÃO DO PLANO NUTRICIONAL:
Quando todas as informações estiverem completas, gere um plano que inclua:
- Café da manhã, almoço, jantar e lanches
- Calorias totais adequadas ao objetivo
- Macros balanceados (proteínas, carboidratos, gorduras)
- Alimentos da tabela TACO (brasileiros)
- Consideração de restrições e preferências
- Dicas de preparo e horários

IMPORTANTE: Retorne SEMPRE em formato JSON:
{{
  "response": "sua mensagem ao cliente",
  "status": "collecting|ready_to_generate|plan_generated|followup|escalate",
  "next_question": "próxima pergunta ou null",
  "anamnesis_complete": true/false,
  "should_generate_plan": true/false,
  "escalate_reason": "motivo da escalação se status=escalate"
}}

Se o cliente apresentar condições médicas complexas, solicitações que fogem do escopo nutricional, ou casos que exigem atenção especializada presencial, use status: "escalate" e explique o motivo.
"""
    
    def process_message(self, phone: str, message: str) -> dict:
        client = db.get_client(phone)
        
        if not client:
            return {
                "success": False,
                "error": "Cliente não encontrado. Por favor, complete a assinatura primeiro."
            }
        
        db.add_interaction(phone, "nutrition", message, "incoming")
        
        recent_interactions = db.get_client_interactions(phone, limit=20)
        context = "\n".join([
            f"{'Cliente' if i['direction'] == 'incoming' else 'Nutricionista'}: {i['message']}"
            for i in reversed(recent_interactions[-10:])
        ])
        
        anamnesis_data = client.get("anamnesis", {})
        context += f"\n\nDados coletados até agora: {json.dumps(anamnesis_data, ensure_ascii=False)}"
        
        response_json = self.agent.generate_structured_response(
            self.system_prompt,
            message,
            context=f"Histórico e dados:\n{context}"
        )
        
        try:
            result = json.loads(response_json)
            response_text = result.get("response", "")
            status = result.get("status", "collecting")
            should_generate_plan = result.get("should_generate_plan", False)
            anamnesis_complete = result.get("anamnesis_complete", False)
            
            if status == "escalate":
                db.update_client(phone, {
                    "needs_human_support": True,
                    "escalation_reason": result.get("escalate_reason", "Caso complexo identificado pelo nutricionista IA"),
                    "status": "pending_human"
                })
                response_text += "\n\n🔔 Seu caso será encaminhado para um nutricionista especializado que entrará em contato em breve para um atendimento mais detalhado."
                db.add_interaction(phone, "nutrition", response_text, "outgoing")
                whatsapp.send_text(phone, response_text)
                
                return {
                    "success": True,
                    "response": response_text,
                    "status": "escalated",
                    "escalated": True
                }
            
            db.add_interaction(phone, "nutrition", response_text, "outgoing")
            whatsapp.send_text(phone, response_text)
            
            if should_generate_plan and anamnesis_complete:
                self._extract_and_save_anamnesis(phone, context, recent_interactions)
                
                plan = self._generate_diet_plan(phone)
                if plan:
                    db.add_interaction(phone, "nutrition", plan, "outgoing")
                    whatsapp.send_text(phone, plan)
                    return {
                        "success": True,
                        "response": response_text,
                        "plan": plan,
                        "status": "plan_generated"
                    }
            
            return {
                "success": True,
                "response": response_text,
                "status": status
            }
            
        except json.JSONDecodeError:
            fallback_response = "Entendi! Vamos continuar sua avaliação nutricional. Pode me contar um pouco mais sobre seus hábitos alimentares?"
            whatsapp.send_text(phone, fallback_response)
            db.add_interaction(phone, "nutrition", fallback_response, "outgoing")
            return {"success": True, "response": fallback_response, "status": "collecting"}
    
    def _extract_and_save_anamnesis(self, phone: str, context: str, interactions: list):
        extraction_prompt = f"""Com base no histórico de conversas abaixo, extraia TODOS os dados da anamnese nutricional em formato JSON.

Histórico:
{context}

Retorne um JSON com todas as informações coletadas, usando as chaves: nome, data_nascimento, peso, altura, sexo, doencas, medicamentos, alergias, refeicoes_dia, apetite, preferencias, agua_dia, pratica_exercicio, intensidade, objetivo_principal, objetivo_detalhes, etc.

Se alguma informação não foi mencionada, use null.
"""
        
        try:
            anamnesis_json = self.agent.generate_structured_response(
                "Você é um assistente de extração de dados. Retorne apenas JSON válido.",
                extraction_prompt
            )
            anamnesis_data = json.loads(anamnesis_json)
            db.save_anamnesis(phone, anamnesis_data)
        except:
            pass
    
    def _generate_diet_plan(self, phone: str) -> str:
        client = db.get_client(phone)
        if not client:
            return ""
        
        anamnesis = client.get("anamnesis", {})
        
        plan_prompt = f"""Gere um plano nutricional COMPLETO e DETALHADO para o cliente com os seguintes dados:

{json.dumps(anamnesis, ensure_ascii=False, indent=2)}

Use EXCLUSIVAMENTE alimentos da tabela TACO brasileira:
{json.dumps(BRAZILIAN_FOODS_SAMPLE, ensure_ascii=False, indent=2)}

O plano deve incluir:

📋 CAFÉ DA MANHÃ (horário sugerido + alimentos + quantidades + calorias)
📋 LANCHE DA MANHÃ (horário + alimentos + quantidades + calorias)
📋 ALMOÇO (horário + alimentos + quantidades + calorias)
📋 LANCHE DA TARDE (horário + alimentos + quantidades + calorias)
📋 JANTAR (horário + alimentos + quantidades + calorias)
📋 CEIA (se necessário)

📊 RESUMO NUTRICIONAL DIÁRIO:
- Calorias totais
- Proteínas (g)
- Carboidratos (g)
- Gorduras (g)

💡 DICAS PERSONALIZADAS:
- Preparo dos alimentos
- Hidratação
- Horários recomendados
- Suplementação (se necessário)

⚠️ OBSERVAÇÕES IMPORTANTES baseadas nas restrições e objetivos do cliente

Seja específico, prático e motivador. O plano deve ser fácil de seguir.
"""
        
        try:
            plan = self.agent.generate_response(
                "Você é um nutricionista experiente especializado em planos alimentares personalizados usando alimentos brasileiros.",
                plan_prompt
            )
            
            db.save_diet_plan(phone, {"plan_text": plan, "anamnesis": anamnesis})
            
            return f"🎉 SEU PLANO NUTRICIONAL PERSONALIZADO ESTÁ PRONTO!\n\n{plan}"
        except Exception as e:
            return f"Estou finalizando seu plano personalizado. Em breve você receberá todas as orientações! 💚"

nutrition_agent = NutritionAgent()
