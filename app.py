import streamlit as st
from datetime import datetime
import json
from database import db
from agent_sales import sales_agent
from agent_nutrition import nutrition_agent

st.set_page_config(
    page_title="Dashboard Nutricional IA",
    page_icon="🥗",
    layout="wide"
)

st.title("🥗 Dashboard - Agente de IA Nutricional")
st.markdown("Sistema de Inteligência Artificial com Agentes de Vendas e Nutrição")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Visão Geral", 
    "👥 Clientes", 
    "🔔 Leads",
    "💬 Interações",
    "🧪 Testar Agentes"
])

with tab1:
    st.header("Visão Geral do Negócio")
    
    stats = db.get_conversion_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 Clientes Ativos",
            value=stats["active_clients"]
        )
    
    with col2:
        st.metric(
            label="💰 Receita Mensal",
            value=f"R$ {stats['monthly_revenue']:.2f}"
        )
    
    with col3:
        st.metric(
            label="📈 Taxa de Conversão",
            value=f"{stats['conversion_rate']:.1f}%"
        )
    
    with col4:
        st.metric(
            label="🎯 Leads Totais",
            value=stats["total_leads"]
        )
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💵 Assinaturas Ativas")
        subscriptions = db.get_active_subscriptions()
        st.write(f"**Total:** {len(subscriptions)} assinaturas de R$ 47,00/mês")
        st.write(f"**Receita Anual Projetada:** R$ {stats['monthly_revenue'] * 12:.2f}")
    
    with col2:
        st.subheader("📊 Conversões Recentes")
        recent_clients = db.get_all_clients()[-5:]
        for client in reversed(recent_clients):
            created = client.get("created_at", "")
            if created:
                try:
                    dt = datetime.fromisoformat(created)
                    st.write(f"✅ {client.get('name', 'Cliente')} - {dt.strftime('%d/%m/%Y %H:%M')}")
                except:
                    st.write(f"✅ {client.get('name', 'Cliente')}")

with tab2:
    st.header("👥 Clientes Ativos")
    
    clients = db.get_all_clients()
    
    if clients:
        st.write(f"**Total de clientes:** {len(clients)}")
        
        for client in reversed(clients):
            with st.expander(f"📱 {client.get('name', 'Cliente')} - {client.get('phone', '')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Status:** {client.get('status', 'N/A')}")
                    st.write(f"**Telefone:** {client.get('phone', 'N/A')}")
                    st.write(f"**Cadastro:** {client.get('created_at', 'N/A')[:10] if client.get('created_at') else 'N/A'}")
                
                with col2:
                    st.write(f"**Anamnese Completa:** {'✅ Sim' if client.get('anamnesis_completed') else '❌ Não'}")
                    st.write(f"**Plano Gerado:** {'✅ Sim' if client.get('diet_plan_generated') else '❌ Não'}")
                
                if client.get('anamnesis'):
                    st.write("**Dados da Anamnese:**")
                    anamnesis = client.get('anamnesis', {})
                    st.json(anamnesis)
                
                interactions = db.get_client_interactions(client.get('phone', ''), limit=5)
                if interactions:
                    st.write("**Últimas Interações:**")
                    for interaction in interactions[:3]:
                        direction = "📥" if interaction['direction'] == 'incoming' else "📤"
                        st.write(f"{direction} {interaction['message'][:100]}...")
    else:
        st.info("Nenhum cliente cadastrado ainda.")

with tab3:
    st.header("🔔 Leads em Prospecção")
    
    leads = db.get_all_leads()
    
    if leads:
        active_leads = [l for l in leads if l.get('status') != 'converted']
        converted_leads = [l for l in leads if l.get('status') == 'converted']
        
        st.write(f"**Leads ativos:** {len(active_leads)}")
        st.write(f"**Leads convertidos:** {len(converted_leads)}")
        
        st.subheader("Leads Ativos")
        for lead in reversed(active_leads):
            with st.expander(f"🎯 {lead.get('name', 'Lead')} - {lead.get('phone', '')}"):
                st.write(f"**Status:** {lead.get('status', 'N/A')}")
                st.write(f"**Telefone:** {lead.get('phone', 'N/A')}")
                st.write(f"**Origem:** {lead.get('source', 'N/A')}")
                st.write(f"**Criado em:** {lead.get('created_at', 'N/A')[:16] if lead.get('created_at') else 'N/A'}")
                
                interactions = db.get_client_interactions(lead.get('phone', ''), limit=3)
                if interactions:
                    st.write("**Últimas mensagens:**")
                    for interaction in interactions[:3]:
                        st.write(f"• {interaction['message'][:80]}...")
    else:
        st.info("Nenhum lead cadastrado ainda.")

with tab4:
    st.header("💬 Histórico de Interações")
    
    interactions = db.get_recent_interactions(limit=50)
    
    if interactions:
        st.write(f"**Total de interações:** {len(interactions)}")
        
        for interaction in interactions[:20]:
            timestamp = interaction.get('timestamp', '')
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime('%d/%m/%Y %H:%M')
            except:
                time_str = timestamp[:16] if timestamp else ''
            
            agent_emoji = "💼" if interaction['agent'] == 'sales' else "🥗"
            direction_emoji = "📥" if interaction['direction'] == 'incoming' else "📤"
            
            st.write(f"{direction_emoji} {agent_emoji} **{interaction['phone']}** - {time_str}")
            st.write(f"_{interaction['message'][:150]}..._" if len(interaction['message']) > 150 else f"_{interaction['message']}_")
            st.divider()
    else:
        st.info("Nenhuma interação registrada ainda.")

with tab5:
    st.header("🧪 Testar Agentes de IA")
    
    st.write("Use esta área para simular conversas com os agentes e testar o sistema.")
    
    agent_type = st.selectbox(
        "Selecione o agente:",
        ["Agente de Vendas", "Agente Nutricional"]
    )
    
    test_phone = st.text_input("Número de telefone (para teste):", "+5511999999999")
    test_message = st.text_area("Mensagem do cliente:")
    
    if st.button("Enviar para o Agente", type="primary"):
        if test_message and test_phone:
            with st.spinner("Processando com IA..."):
                try:
                    if agent_type == "Agente de Vendas":
                        result = sales_agent.process_message(test_phone, test_message)
                    else:
                        result = nutrition_agent.process_message(test_phone, test_message)
                    
                    if result.get("success"):
                        st.success("✅ Mensagem processada com sucesso!")
                        st.write("**Resposta do agente:**")
                        st.info(result.get("response", ""))
                        
                        if result.get("action"):
                            st.write(f"**Ação:** {result['action']}")
                        
                        if result.get("plan"):
                            st.write("**Plano gerado:**")
                            st.text(result['plan'])
                    else:
                        st.error(f"❌ Erro: {result.get('error', 'Erro desconhecido')}")
                except Exception as e:
                    st.error(f"❌ Erro ao processar: {str(e)}")
        else:
            st.warning("⚠️ Preencha o número de telefone e a mensagem.")
    
    st.divider()
    st.subheader("📊 Estatísticas do Teste")
    
    if test_phone:
        client = db.get_client(test_phone)
        lead = db.get_lead(test_phone)
        
        if client:
            st.write(f"**Status:** Cliente ativo")
            st.json(client)
        elif lead:
            st.write(f"**Status:** Lead em prospecção")
            st.json(lead)
        else:
            st.info("Nenhum registro encontrado para este número.")

st.sidebar.title("ℹ️ Sobre o Sistema")
st.sidebar.info("""
**Agente de IA Nutricional**

Sistema completo com:
- 🤖 Agente de Vendas (WhatsApp)
- 🥗 Agente Nutricional (WhatsApp)
- 📊 Dashboard Administrativo
- 💾 Banco de dados integrado

**Funcionalidades:**
- Qualificação automática de leads
- Anamnese nutricional completa
- Planos alimentares personalizados
- Acompanhamento 24/7

**Assinatura:** R$ 47,00/mês
""")

st.sidebar.divider()
st.sidebar.write("**Credenciais Z-API configuradas ✅**")
st.sidebar.write("**OpenAI via Replit AI ✅**")
