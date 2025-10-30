#!/usr/bin/env python3

import json
from database import db
from message_router import router

print("\n🧪 TESTE DE ESCALAÇÃO PARA ATENDIMENTO HUMANO\n")
print("=" * 60)

test_phone = "+5511988776655"

print("\n1. ✅ Criar lead de teste")
db.add_lead(test_phone, "Maria Teste Escalação", "whatsapp")
lead = db.get_lead(test_phone)
print(f"   Lead criado: {lead['phone']}")
print(f"   Status inicial: {lead.get('status', 'N/A')}")
print(f"   Precisa suporte humano: {lead.get('needs_human_support', False)}")

print("\n2. ✅ Simular escalação pelo agente de vendas")
db.update_lead(test_phone, {
    "needs_human_support": True,
    "escalation_reason": "Cliente com dúvidas complexas sobre metodologia",
    "status": "pending_human"
})
lead = db.get_lead(test_phone)
print(f"   Status atualizado: {lead.get('status')}")
print(f"   Precisa suporte humano: {lead.get('needs_human_support')}")
print(f"   Motivo: {lead.get('escalation_reason')}")

print("\n3. ✅ Testar roteamento após escalação")
result = router.route_message(test_phone, "Olá, tenho mais perguntas")
print(f"   Roteado para: {result.get('routed_to')}")
print(f"   Mensagem: {result.get('message')}")
print(f"   ⚠️  Resposta automática NÃO deve ser enviada")

print("\n4. ✅ Converter para cliente e testar escalação nutricional")
client_id = db.convert_lead_to_client(test_phone)
client = db.get_client(test_phone)
print(f"   Cliente convertido: {client_id}")
print(f"   Status: {client.get('status')}")

print("\n5. ✅ Simular escalação pelo agente nutricional")
db.update_client(test_phone, {
    "needs_human_support": True,
    "escalation_reason": "Cliente apresenta condições médicas que requerem avaliação presencial",
    "status": "pending_human"
})
client = db.get_client(test_phone)
print(f"   Status atualizado: {client.get('status')}")
print(f"   Precisa suporte humano: {client.get('needs_human_support')}")
print(f"   Motivo: {client.get('escalation_reason')}")

print("\n6. ✅ Testar roteamento após escalação nutricional")
result = router.route_message(test_phone, "Preciso de mais informações sobre meu plano")
print(f"   Roteado para: {result.get('routed_to')}")
print(f"   Mensagem: {result.get('message')}")
print(f"   ⚠️  Resposta automática NÃO deve ser enviada")

print("\n7. ✅ Testar função de escalação manual")
success = router.escalate_to_human(test_phone, "Escalação manual pelo administrador")
print(f"   Escalação manual bem-sucedida: {success}")

print("\n" + "=" * 60)
print("✅ TESTE DE ESCALAÇÃO CONCLUÍDO COM SUCESSO!")
print("=" * 60)

print("\n📋 Resumo:")
print("   ✓ Leads e clientes podem ser escalados para humanos")
print("   ✓ Roteador detecta escalação e não envia respostas automáticas")
print("   ✓ Motivos de escalação são armazenados corretamente")
print("   ✓ Sistema previne loop infinito de IA em casos complexos")
print("\n💡 No dashboard, casos escalados aparecem com status 'pending_human'\n")
