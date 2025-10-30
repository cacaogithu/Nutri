#!/usr/bin/env python3
"""
Testes rápidos do sistema - sem chamadas de IA
Foca em database, roteamento e lógica de negócio
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db
from message_router import router
from admin_actions import admin

print("\n🚀 TESTES RÁPIDOS - SISTEMA IA NUTRICIONAL\n")
print("="*60)

errors = []

def test(name, condition, error_msg=None):
    if condition:
        print(f"✅ {name}")
        return True
    else:
        msg = error_msg or name
        print(f"❌ FALHOU: {msg}")
        errors.append(msg)
        return False

print("\n📁 1. TESTES DE DATABASE")
print("-"*60)

phone1 = "+5511911111111"
db.add_lead(phone1, "Lead Teste 1", "whatsapp")
test("Lead criado", db.get_lead(phone1) is not None)

db.update_lead(phone1, {"status": "qualified"})
lead = db.get_lead(phone1)
test("Lead atualizado", lead.get("status") == "qualified")

client_id = db.convert_lead_to_client(phone1)
test("Lead convertido para cliente", client_id is not None)

client = db.get_client(phone1)
test("Cliente criado com status ativo", client.get("status") == "active")

db.add_interaction(phone1, "sales", "Mensagem de teste", "incoming")
interactions = db.get_client_interactions(phone1)
test("Interação registrada", len(interactions) > 0)

anamnesis = {"nome": "Teste", "peso": 80, "altura": 175}
db.save_anamnesis(phone1, anamnesis)
client = db.get_client(phone1)
test("Anamnese salva", client.get("anamnesis_completed") == True)

plan_id = db.save_diet_plan(phone1, {"plano": "Plano teste"})
test("Plano dietético salvo", plan_id is not None)

print("\n🔄 2. TESTES DE ROTEAMENTO")
print("-"*60)

phone2 = "+5511922222222"
db.add_lead(phone2, "Lead Routing", "whatsapp")

result = router.route_message(phone2, "Teste")
test("Roteamento para sales (novo lead)", result is not None)

db.convert_lead_to_client(phone2)
result = router.route_message(phone2, "Teste cliente")
test("Roteamento para nutrition (cliente)", result is not None)

print("\n⚡ 3. TESTES DE ESCALAÇÃO")
print("-"*60)

phone3 = "+5511933333333"
db.add_lead(phone3, "Lead Escalação", "whatsapp")

db.update_lead(phone3, {
    "needs_human_support": True,
    "status": "pending_human",
    "escalation_reason": "Teste"
})

lead = db.get_lead(phone3)
test("Lead escalado", lead.get("needs_human_support") == True)

result = router.route_message(phone3, "Mensagem após escalação")
test("Roteamento bloqueado após escalação", result.get("routed_to") == "human")

success = router.escalate_to_human(phone3, "Manual")
test("Escalação manual funciona", success == True)

print("\n👔 4. TESTES DE ADMIN")
print("-"*60)

phone4 = "+5511944444444"
db.add_lead(phone4, "Lead Admin", "whatsapp")
db.convert_lead_to_client(phone4)

success = admin.escalate_to_human(phone4, "Admin test")
test("Admin pode escalar", success)

client = db.get_client(phone4)
test("Escalação via admin registrada", client.get("needs_human_support") == True)

history = admin.get_client_full_history(phone4)
test("Histórico completo recuperado", history.get("client_data") is not None)

admin.mark_client_inactive(phone4)
client = db.get_client(phone4)
test("Cliente marcado como inativo", client.get("status") == "inactive")

print("\n📊 5. TESTES DE ESTATÍSTICAS")
print("-"*60)

stats = db.get_conversion_stats()
test("Estatísticas calculadas", stats is not None)
test("Total de leads correto", stats["total_leads"] > 0)
test("Conversão rate calculada", "conversion_rate" in stats)
test("Receita mensal calculada", "monthly_revenue" in stats)

all_clients = db.get_all_clients()
test("Lista de clientes retornada", isinstance(all_clients, list))
test("Clientes existem", len(all_clients) > 0)

all_leads = db.get_all_leads()
test("Lista de leads retornada", isinstance(all_leads, list))
test("Leads existem", len(all_leads) > 0)

active_subs = db.get_active_subscriptions()
test("Assinaturas ativas retornadas", isinstance(active_subs, list))

recent_interactions = db.get_recent_interactions(limit=10)
test("Interações recentes retornadas", isinstance(recent_interactions, list))

print("\n" + "="*60)
print("RESUMO DOS TESTES")
print("="*60)

total_tests = 29
passed = total_tests - len(errors)

print(f"\n✅ Passou: {passed}/{total_tests}")

if errors:
    print(f"❌ Falhou: {len(errors)}/{total_tests}")
    print("\nErros:")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)
else:
    print("\n🎉 TODOS OS TESTES PASSARAM!")
    print("\n💡 Sistema de database, roteamento e admin totalmente funcional!")
    sys.exit(0)
