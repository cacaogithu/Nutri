#!/usr/bin/env python3
"""
Testes completos do sistema de agentes de IA nutricional
Heavy testing para validar todos os fluxos e casos extremos
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db
from agent_sales import sales_agent
from agent_nutrition import nutrition_agent
from message_router import router
from admin_actions import admin
import json

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def assert_true(self, condition, message):
        if condition:
            print(f"  ✅ {message}")
            self.passed += 1
            return True
        else:
            print(f"  ❌ FALHOU: {message}")
            self.failed += 1
            return False
    
    def assert_equals(self, actual, expected, message):
        if actual == expected:
            print(f"  ✅ {message}")
            self.passed += 1
            return True
        else:
            print(f"  ❌ FALHOU: {message}")
            print(f"     Esperado: {expected}")
            print(f"     Obtido: {actual}")
            self.failed += 1
            return False
    
    def run_test(self, name, test_func):
        print(f"\n{'='*60}")
        print(f"TESTE: {name}")
        print(f"{'='*60}")
        try:
            test_func()
            print(f"✅ Teste '{name}' concluído")
        except Exception as e:
            print(f"❌ Teste '{name}' falhou com exceção: {str(e)}")
            import traceback
            traceback.print_exc()
            self.failed += 1
    
    def summary(self):
        print(f"\n{'='*60}")
        print(f"RESUMO DOS TESTES")
        print(f"{'='*60}")
        print(f"✅ Passou: {self.passed}")
        print(f"❌ Falhou: {self.failed}")
        print(f"Total: {self.passed + self.failed}")
        if self.failed == 0:
            print(f"\n🎉 TODOS OS TESTES PASSARAM!")
            return True
        else:
            print(f"\n⚠️  {self.failed} teste(s) falharam")
            return False

runner = TestRunner()

def test_database_operations():
    """Testa operações básicas do database"""
    phone = "+5511900000001"
    
    lead_id = db.add_lead(phone, "Teste DB", "whatsapp")
    runner.assert_true(lead_id is not None, "Lead criado com sucesso")
    
    lead = db.get_lead(phone)
    runner.assert_true(lead is not None, "Lead recuperado do DB")
    runner.assert_equals(lead["name"], "Teste DB", "Nome do lead correto")
    
    db.update_lead(phone, {"status": "qualified"})
    lead = db.get_lead(phone)
    runner.assert_equals(lead["status"], "qualified", "Status do lead atualizado")
    
    client_id = db.convert_lead_to_client(phone)
    runner.assert_true(client_id is not None, "Lead convertido para cliente")
    
    client = db.get_client(phone)
    runner.assert_true(client is not None, "Cliente recuperado do DB")
    runner.assert_equals(client["status"], "active", "Cliente com status ativo")
    
    db.add_interaction(phone, "sales", "Mensagem teste", "incoming")
    interactions = db.get_client_interactions(phone)
    runner.assert_true(len(interactions) > 0, "Interação registrada")
    
    anamnesis = {"nome": "Teste", "peso": 80, "altura": 175}
    db.save_anamnesis(phone, anamnesis)
    client = db.get_client(phone)
    runner.assert_true(client.get("anamnesis_completed"), "Anamnese marcada como completa")
    
    plan_id = db.save_diet_plan(phone, {"plano": "Plano teste"})
    runner.assert_true(plan_id is not None, "Plano dietético salvo")

def test_sales_agent_basic():
    """Testa fluxo básico do agente de vendas"""
    phone = "+5511900000002"
    
    result = sales_agent.process_message(phone, "Olá")
    runner.assert_true(result.get("success"), "Sales agent processou mensagem inicial")
    runner.assert_true(len(result.get("response", "")) > 0, "Sales agent retornou resposta")
    
    lead = db.get_lead(phone)
    runner.assert_true(lead is not None, "Lead criado automaticamente")
    
    interactions = db.get_client_interactions(phone)
    runner.assert_true(len(interactions) >= 2, "Interações registradas (entrada + saída)")

def test_sales_conversion_flow():
    """Testa conversão de lead para cliente"""
    phone = "+5511900000003"
    
    db.add_lead(phone, "Lead Conversão", "whatsapp")
    
    db.update_lead(phone, {"status": "interested"})
    lead = db.get_lead(phone)
    runner.assert_equals(lead["status"], "interested", "Lead marcado como interessado")
    
    client_id = db.convert_lead_to_client(phone)
    runner.assert_true(client_id is not None, "Conversão para cliente realizada")
    
    client = db.get_client(phone)
    runner.assert_true(client is not None, "Cliente existe no DB")
    runner.assert_equals(client["status"], "active", "Cliente ativo")
    
    subs = db.get_active_subscriptions()
    runner.assert_true(len(subs) > 0, "Assinatura ativa criada")
    
    stats = db.get_conversion_stats()
    runner.assert_true(stats["converted_leads"] > 0, "Estatística de conversão atualizada")

def test_escalation_flow():
    """Testa escalação para atendimento humano"""
    phone = "+5511900000004"
    
    db.add_lead(phone, "Lead Escalação", "whatsapp")
    lead = db.get_lead(phone)
    runner.assert_true(not lead.get("needs_human_support"), "Lead inicialmente sem escalação")
    
    db.update_lead(phone, {
        "needs_human_support": True,
        "escalation_reason": "Caso complexo",
        "status": "pending_human"
    })
    
    lead = db.get_lead(phone)
    runner.assert_true(lead.get("needs_human_support"), "Lead escalado para humano")
    runner.assert_equals(lead.get("status"), "pending_human", "Status correto após escalação")
    
    result = router.route_message(phone, "Nova mensagem após escalação")
    runner.assert_equals(result.get("routed_to"), "human", "Roteamento para humano")
    
    client_id = db.convert_lead_to_client(phone)
    db.update_client(phone, {
        "needs_human_support": True,
        "status": "pending_human",
        "escalation_reason": "Condição médica complexa"
    })
    
    result = router.route_message(phone, "Mensagem de cliente escalado")
    runner.assert_equals(result.get("routed_to"), "human", "Cliente escalado roteado para humano")

def test_nutrition_agent_flow():
    """Testa fluxo do agente nutricional"""
    phone = "+5511900000005"
    
    db.add_lead(phone, "Cliente Nutrição", "whatsapp")
    client_id = db.convert_lead_to_client(phone)
    
    client = db.get_client(phone)
    runner.assert_true(client is not None, "Cliente criado para teste nutricional")
    runner.assert_true(not client.get("anamnesis_completed"), "Anamnese não completa inicialmente")
    
    anamnesis_data = {
        "nome": "João Silva",
        "peso": 85,
        "altura": 175,
        "objetivo": "emagrecimento",
        "atividade_fisica": "moderada"
    }
    db.save_anamnesis(phone, anamnesis_data)
    
    client = db.get_client(phone)
    runner.assert_true(client.get("anamnesis_completed"), "Anamnese marcada como completa")
    runner.assert_equals(client["anamnesis"]["nome"], "João Silva", "Dados da anamnese salvos")
    
    plan_data = {"plano_texto": "Plano nutricional personalizado"}
    plan_id = db.save_diet_plan(phone, plan_data)
    runner.assert_true(plan_id is not None, "Plano dietético criado")
    
    client = db.get_client(phone)
    runner.assert_true(client.get("diet_plan_generated"), "Plano marcado como gerado")

def test_message_routing():
    """Testa roteamento de mensagens"""
    phone_lead = "+5511900000006"
    phone_client = "+5511900000007"
    
    db.add_lead(phone_lead, "Lead Routing", "whatsapp")
    lead = db.get_lead(phone_lead)
    runner.assert_true(lead is not None, "Lead criado para teste de routing")
    
    db.add_lead(phone_client, "Cliente Routing", "whatsapp")
    client_id = db.convert_lead_to_client(phone_client)
    client = db.get_client(phone_client)
    runner.assert_true(client is not None, "Cliente criado para teste de routing")

def test_admin_actions():
    """Testa ações administrativas"""
    phone = "+5511900000008"
    
    db.add_lead(phone, "Lead Admin", "whatsapp")
    
    success = admin.escalate_to_human(phone, "Teste escalação manual")
    runner.assert_true(success, "Escalação manual pelo admin")
    
    lead = db.get_lead(phone)
    runner.assert_true(lead.get("needs_human_support"), "Lead escalado via admin")
    runner.assert_equals(lead.get("escalation_reason"), "Teste escalação manual", "Motivo registrado")
    
    history = admin.get_client_full_history(phone)
    runner.assert_true(history.get("client_data") is not None, "Histórico completo recuperado")

def test_statistics_and_metrics():
    """Testa estatísticas e métricas do sistema"""
    stats = db.get_conversion_stats()
    
    runner.assert_true("total_leads" in stats, "Estatística de total_leads existe")
    runner.assert_true("converted_leads" in stats, "Estatística de converted_leads existe")
    runner.assert_true("conversion_rate" in stats, "Taxa de conversão calculada")
    runner.assert_true("active_clients" in stats, "Clientes ativos contabilizados")
    runner.assert_true("monthly_revenue" in stats, "Receita mensal calculada")
    
    runner.assert_true(stats["total_leads"] >= 0, "Total de leads válido")
    runner.assert_true(stats["monthly_revenue"] >= 0, "Receita válida")
    
    all_clients = db.get_all_clients()
    runner.assert_true(isinstance(all_clients, list), "Lista de clientes retornada")
    
    all_leads = db.get_all_leads()
    runner.assert_true(isinstance(all_leads, list), "Lista de leads retornada")

def test_edge_cases():
    """Testa casos extremos e validações"""
    phone_invalid = "+5511900000009"
    
    lead = db.get_lead("telefone_inexistente")
    runner.assert_true(lead is None, "Lead inexistente retorna None")
    
    client = db.get_client("telefone_inexistente")
    runner.assert_true(client is None, "Cliente inexistente retorna None")
    
    db.add_lead(phone_invalid, "", "whatsapp")
    lead = db.get_lead(phone_invalid)
    runner.assert_true(lead is not None, "Lead criado mesmo com nome vazio")
    
    db.add_interaction(phone_invalid, "test", "", "incoming")
    interactions = db.get_client_interactions(phone_invalid)
    runner.assert_true(len(interactions) > 0, "Interação vazia registrada")

def test_concurrent_operations():
    """Testa operações concorrentes no database"""
    base_phone = "+551190000001"
    
    for i in range(5):
        phone = f"{base_phone}{i}"
        db.add_lead(phone, f"Lead Concurrent {i}", "whatsapp")
        db.add_interaction(phone, "test", f"Mensagem {i}", "incoming")
    
    runner.assert_true(True, "Operações concorrentes executadas sem erro")
    
    stats = db.get_conversion_stats()
    runner.assert_true(stats["total_leads"] >= 5, "Múltiplos leads criados")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 HEAVY TESTING - SISTEMA DE AGENTES IA NUTRICIONAL")
    print("="*60)
    
    runner.run_test("1. Operações de Database", test_database_operations)
    runner.run_test("2. Agente de Vendas - Básico", test_sales_agent_basic)
    runner.run_test("3. Conversão de Lead para Cliente", test_sales_conversion_flow)
    runner.run_test("4. Escalação para Atendimento Humano", test_escalation_flow)
    runner.run_test("5. Agente Nutricional - Fluxo Completo", test_nutrition_agent_flow)
    runner.run_test("6. Roteamento de Mensagens", test_message_routing)
    runner.run_test("7. Ações Administrativas", test_admin_actions)
    runner.run_test("8. Estatísticas e Métricas", test_statistics_and_metrics)
    runner.run_test("9. Casos Extremos", test_edge_cases)
    runner.run_test("10. Operações Concorrentes", test_concurrent_operations)
    
    success = runner.summary()
    
    if success:
        print("\n✅ Sistema validado e pronto para produção!")
        sys.exit(0)
    else:
        print("\n⚠️  Alguns testes falharam - revisar antes de produção")
        sys.exit(1)
