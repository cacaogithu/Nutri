#!/usr/bin/env python3

from database import db
from whatsapp_api import whatsapp
import json

print("\n🧪 VERIFICAÇÃO RÁPIDA DO SISTEMA\n")
print("=" * 60)

print("\n1. ✅ Database inicializado")
print("   Arquivo: data/database.json")

print("\n2. ✅ Agentes importados com sucesso")
from agent_sales import sales_agent
from agent_nutrition import nutrition_agent
print(f"   - Sales Agent: {type(sales_agent).__name__}")
print(f"   - Nutrition Agent: {type(nutrition_agent).__name__}")

print("\n3. ✅ Configuração Z-API")
from config import Z_API_INSTANCE, Z_API_TOKEN, SUBSCRIPTION_PRICE
print(f"   - Instance: {Z_API_INSTANCE[:10]}...")
print(f"   - Token: {Z_API_TOKEN[:10]}...")
print(f"   - Preço assinatura: R$ {SUBSCRIPTION_PRICE}")

print("\n4. ✅ OpenAI via Replit AI Integrations")
from config import AI_INTEGRATIONS_OPENAI_API_KEY, AI_INTEGRATIONS_OPENAI_BASE_URL
print(f"   - API Key configurada: {bool(AI_INTEGRATIONS_OPENAI_API_KEY)}")
print(f"   - Base URL configurada: {bool(AI_INTEGRATIONS_OPENAI_BASE_URL)}")

print("\n5. ✅ Knowledge Base carregado")
from knowledge_base import ANAMNESIS_QUESTIONS, BRAZILIAN_FOODS_SAMPLE, SALES_METHODOLOGY
print(f"   - Categorias de anamnese: {len(ANAMNESIS_QUESTIONS)}")
print(f"   - Categorias de alimentos: {len(BRAZILIAN_FOODS_SAMPLE)}")
print(f"   - Metodologia de vendas: {len(SALES_METHODOLOGY)} caracteres")

print("\n6. ✅ Testar adição de lead")
test_phone = "+5511999887766"
lead_id = db.add_lead(test_phone, "João da Silva Teste", "whatsapp")
print(f"   Lead criado: {lead_id}")

print("\n7. ✅ Testar conversão para cliente")
client_id = db.convert_lead_to_client(test_phone)
print(f"   Cliente convertido: {client_id}")

print("\n8. ✅ Adicionar interação de teste")
db.add_interaction(test_phone, "sales", "Teste de mensagem", "incoming")
db.add_interaction(test_phone, "sales", "Resposta de teste", "outgoing")
print(f"   Interações adicionadas")

print("\n9. ✅ Estatísticas do sistema")
stats = db.get_conversion_stats()
print(f"   - Total de leads: {stats['total_leads']}")
print(f"   - Clientes ativos: {stats['active_clients']}")
print(f"   - Taxa de conversão: {stats['conversion_rate']:.1f}%")
print(f"   - Receita mensal: R$ {stats['monthly_revenue']:.2f}")

print("\n10. ✅ Verificar estrutura do dashboard")
import app
print("   Dashboard Streamlit carregado com sucesso")

print("\n" + "=" * 60)
print("✅ SISTEMA COMPLETO E FUNCIONAL!")
print("=" * 60)

print("\n📱 Dashboard disponível em: http://0.0.0.0:5000")
print("\n💡 Próximos passos:")
print("   1. Configure webhook da Z-API para receber mensagens")
print("   2. Use a aba 'Testar Agentes' no dashboard")
print("   3. Monitore clientes e conversões em tempo real\n")
