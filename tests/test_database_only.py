#!/usr/bin/env python3
"""
Testes ultra-rápidos - apenas database
Sem chamadas de IA ou roteamento
Usa database isolado temporário
"""

import sys
import os
import tempfile
import shutil
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database

temp_dir = tempfile.mkdtemp()
temp_db_file = os.path.join(temp_dir, "test_database.json")
db = Database(db_file=temp_db_file)

print("\n⚡ TESTES RÁPIDOS - DATABASE ONLY\n")

errors = 0
passed = 0

def test(condition, name):
    global errors, passed
    if condition:
        print(f"✅ {name}")
        passed += 1
    else:
        print(f"❌ {name}")
        errors += 1

phone = "+5511999998888"

lead_id = db.add_lead(phone, "Teste", "whatsapp")
test(lead_id is not None, "1. Lead criado")

lead = db.get_lead(phone)
test(lead is not None, "2. Lead recuperado")

db.update_lead(phone, {"status": "qualified"})
lead = db.get_lead(phone)
test(lead.get("status") == "qualified", "3. Lead atualizado")

client_id = db.convert_lead_to_client(phone)
test(client_id is not None, "4. Cliente convertido")

client = db.get_client(phone)
test(client.get("status") == "active", "5. Cliente ativo")

db.add_interaction(phone, "test", "msg", "incoming")
interactions = db.get_client_interactions(phone)
test(len(interactions) > 0, "6. Interação salva")

db.save_anamnesis(phone, {"nome": "Test"})
client = db.get_client(phone)
test(client.get("anamnesis_completed"), "7. Anamnese completa")

plan_id = db.save_diet_plan(phone, {"plan": "test"})
test(plan_id is not None, "8. Plano salvo")

stats = db.get_conversion_stats()
test(stats["total_leads"] > 0, "9. Estatísticas calculadas")

all_clients = db.get_all_clients()
test(len(all_clients) > 0, "10. Clientes listados")

print(f"\n{'='*40}")
print(f"Passou: {passed}/10")
print(f"Falhou: {errors}/10")

shutil.rmtree(temp_dir)
print(f"🧹 Database temporário limpo")

if errors == 0:
    print("\n✅ TODOS OS TESTES PASSARAM!")
    sys.exit(0)
else:
    print(f"\n❌ {errors} teste(s) falharam")
    sys.exit(1)
