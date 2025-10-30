#!/usr/bin/env python3

import sys
from agent_sales import sales_agent
from agent_nutrition import nutrition_agent
from database import db

def test_sales_flow():
    print("=" * 60)
    print("TESTANDO AGENTE DE VENDAS")
    print("=" * 60)
    
    test_phone = "+5511987654321"
    
    print("\n1. Primeiro contato:")
    result1 = sales_agent.process_message(test_phone, "Olá! Gostaria de conhecer o serviço de nutrição")
    print(f"✅ Resposta: {result1.get('response', '')[:150]}...")
    print(f"   Ação: {result1.get('action', 'N/A')}")
    
    print("\n2. Pergunta sobre preço:")
    result2 = sales_agent.process_message(test_phone, "Quanto custa?")
    print(f"✅ Resposta: {result2.get('response', '')[:150]}...")
    print(f"   Ação: {result2.get('action', 'N/A')}")
    
    print("\n3. Confirmação de assinatura:")
    result3 = sales_agent.process_message(test_phone, "Sim, quero assinar!")
    print(f"✅ Resposta: {result3.get('response', '')[:150]}...")
    print(f"   Ação: {result3.get('action', 'N/A')}")
    
    return test_phone

def test_nutrition_flow(phone):
    print("\n" + "=" * 60)
    print("TESTANDO AGENTE NUTRICIONAL")
    print("=" * 60)
    
    print("\n1. Início da anamnese:")
    result1 = nutrition_agent.process_message(phone, "Olá! Estou pronto para começar")
    print(f"✅ Resposta: {result1.get('response', '')[:150]}...")
    print(f"   Status: {result1.get('status', 'N/A')}")
    
    print("\n2. Respondendo nome:")
    result2 = nutrition_agent.process_message(phone, "Meu nome é João Silva")
    print(f"✅ Resposta: {result2.get('response', '')[:150]}...")
    
    print("\n3. Respondendo peso e altura:")
    result3 = nutrition_agent.process_message(phone, "Peso 85kg e tenho 175cm de altura")
    print(f"✅ Resposta: {result3.get('response', '')[:150]}...")
    
    print("\n4. Objetivo:")
    result4 = nutrition_agent.process_message(phone, "Meu objetivo é emagrecimento saudável")
    print(f"✅ Resposta: {result4.get('response', '')[:150]}...")

def test_database():
    print("\n" + "=" * 60)
    print("TESTANDO DATABASE")
    print("=" * 60)
    
    stats = db.get_conversion_stats()
    print(f"\n📊 Estatísticas:")
    print(f"   Total de leads: {stats['total_leads']}")
    print(f"   Leads convertidos: {stats['converted_leads']}")
    print(f"   Taxa de conversão: {stats['conversion_rate']:.1f}%")
    print(f"   Clientes ativos: {stats['active_clients']}")
    print(f"   Receita mensal: R$ {stats['monthly_revenue']:.2f}")
    
    clients = db.get_all_clients()
    print(f"\n👥 Clientes cadastrados: {len(clients)}")
    
    interactions = db.get_recent_interactions(limit=5)
    print(f"\n💬 Interações recentes: {len(interactions)}")

if __name__ == "__main__":
    print("\n🧪 TESTE COMPLETO DO SISTEMA DE IA NUTRICIONAL\n")
    
    try:
        test_phone = test_sales_flow()
        
        test_nutrition_flow(test_phone)
        
        test_database()
        
        print("\n" + "=" * 60)
        print("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("=" * 60)
        print("\n💡 Acesse o dashboard para visualizar os dados:")
        print("   streamlit run app.py --server.port 5000\n")
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
