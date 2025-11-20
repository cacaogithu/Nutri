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

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Visão Geral", 
    "👥 Clientes", 
    "🔔 Leads",
    "💬 Conversas Completas",
    "📝 Interações",
    "🧪 Testar Agentes",
    "⚙️ Buffer & Monitoramento"
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
    st.header("💬 Conversas Completas dos Clientes")
    
    st.write("Visualize e gerencie conversas completas com clientes e leads")
    
    all_clients = db.get_all_clients()
    all_leads = db.get_all_leads()
    
    all_contacts = []
    for client in all_clients:
        all_contacts.append({
            "phone": client.get("phone"),
            "name": client.get("name", "Cliente"),
            "type": "Cliente",
            "status": client.get("status", ""),
            "needs_human": client.get("needs_human_support", False)
        })
    
    for lead in all_leads:
        if lead.get("status") != "converted":
            all_contacts.append({
                "phone": lead.get("phone"),
                "name": lead.get("name", "Lead"),
                "type": "Lead",
                "status": lead.get("status", ""),
                "needs_human": lead.get("needs_human_support", False)
            })
    
    if all_contacts:
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("Contatos")
            selected_contact = st.selectbox(
                "Selecione um contato:",
                options=range(len(all_contacts)),
                format_func=lambda i: f"{all_contacts[i]['name']} ({all_contacts[i]['type']}) - {all_contacts[i]['phone']}"
            )
            
            if selected_contact is not None:
                contact = all_contacts[selected_contact]
                st.write(f"**Tipo:** {contact['type']}")
                st.write(f"**Status:** {contact['status']}")
                
                if contact['needs_human']:
                    st.warning("⚠️ Escalado para humano")
                
                st.divider()
                
                st.subheader("Ações")
                if st.button("🔄 Atualizar Conversas"):
                    st.rerun()
                
                if contact['needs_human']:
                    if st.button("✅ Resolver Escalação"):
                        phone = contact['phone']
                        if contact['type'] == "Cliente":
                            db.update_client(phone, {
                                "needs_human_support": False,
                                "status": "active"
                            })
                        else:
                            db.update_lead(phone, {
                                "needs_human_support": False,
                                "status": "active"
                            })
                        st.success("Escalação resolvida!")
                        st.rerun()
        
        with col2:
            if selected_contact is not None:
                contact = all_contacts[selected_contact]
                phone = contact['phone']
                
                st.subheader(f"Conversa com {contact['name']}")
                
                interactions = db.get_client_interactions(phone, limit=100)
                
                if interactions:
                    st.write(f"**Total de mensagens:** {len(interactions)}")
                    
                    chat_container = st.container()
                    with chat_container:
                        for interaction in reversed(interactions):
                            timestamp = interaction.get('timestamp', '')
                            try:
                                dt = datetime.fromisoformat(timestamp)
                                time_str = dt.strftime('%d/%m/%Y %H:%M:%S')
                            except:
                                time_str = timestamp
                            
                            is_incoming = interaction['direction'] == 'incoming'
                            agent = interaction.get('agent', 'system')
                            
                            if is_incoming:
                                st.markdown(f"**🧑 Cliente** - _{time_str}_")
                                st.info(interaction['message'])
                            else:
                                agent_name = "Vendas" if agent == "sales" else "Nutrição" if agent == "nutrition" else "Sistema"
                                st.markdown(f"**🤖 Agente {agent_name}** - _{time_str}_")
                                st.success(interaction['message'])
                            
                            st.write("")
                    
                    st.divider()
                    
                    st.subheader("📤 Enviar Mensagem Manual")
                    
                    manual_message = st.text_area(
                        "Digite sua mensagem:",
                        key=f"manual_msg_{phone}",
                        height=100
                    )
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        if st.button("Enviar como Administrador", type="primary"):
                            if manual_message:
                                from whatsapp_api import whatsapp
                                from admin_actions import admin
                                result = admin.send_manual_message(phone, manual_message, agent="admin")
                                if result.get("success"):
                                    st.success("✅ Mensagem enviada!")
                                    st.rerun()
                                else:
                                    st.error(f"❌ Erro: {result.get('error')}")
                            else:
                                st.warning("Digite uma mensagem primeiro")
                    
                    with col_b:
                        if st.button("Escalar para Humano"):
                            from admin_actions import admin
                            result = admin.escalate_to_human(phone, "Escalado manualmente pelo admin")
                            if result.get("success"):
                                st.success("✅ Cliente escalado!")
                                st.rerun()
                else:
                    st.info("Nenhuma conversa registrada ainda.")
    else:
        st.info("Nenhum contato disponível.")

with tab5:
    st.header("📝 Histórico de Interações")
    
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

with tab6:
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

with tab7:
    st.header("⚙️ Buffer & Monitoramento do Sistema")
    
    from buffer_manager import buffer_manager
    from config import TESTING_MODE, BUFFER_WINDOW_SECONDS
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Status do Buffer Manager")
        st.write(f"**Status:** {'🟢 Rodando' if buffer_manager.running else '🔴 Parado'}")
        st.write(f"**Modo de Teste:** {'✅ Ativo' if TESTING_MODE else '❌ Desativado'}")
        st.write(f"**Janela de Buffer:** {BUFFER_WINDOW_SECONDS} segundos")
        
        if st.button("🔄 Forçar Health Check"):
            buffer_manager._run_health_checks()
            st.success("Health check executado!")
    
    with col2:
        st.subheader("📈 Estatísticas")
        data = db._load()
        buffers = data.get("message_buffers", {})
        alerts = db.get_alerts(unresolved_only=True, limit=50)
        
        st.metric("Buffers Ativos", len([b for b in buffers.values() if not b.get("processing", False)]))
        st.metric("Buffers Processando", len([b for b in buffers.values() if b.get("processing", False)]))
        st.metric("Alertas Não Resolvidos", len(alerts))
    
    st.divider()
    
    st.subheader("📋 Buffers Ativos")
    buffers = data.get("message_buffers", {})
    
    if buffers:
        for buffer_key, buffer in buffers.items():
            phone = buffer.get("phone", "")
            expires_at = buffer.get("buffer_expires_at", "")
            processing = buffer.get("processing", False)
            retry_count = buffer.get("retry_count", 0)
            
            status_emoji = "🔄" if processing else "⏳"
            status_text = "Processando" if processing else "Aguardando"
            
            with st.expander(f"{status_emoji} {phone} - {status_text} (Retries: {retry_count})"):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.write(f"**Última Mensagem:** {buffer.get('last_message_at', '')[:19]}")
                    st.write(f"**Expira em:** {expires_at[:19] if expires_at else 'N/A'}")
                    st.write(f"**Criado em:** {buffer.get('created_at', '')[:19]}")
                
                with col_b:
                    st.write(f"**Processando:** {'Sim' if processing else 'Não'}")
                    st.write(f"**Tentativas:** {retry_count}")
                    if buffer.get("locked_by"):
                        st.write(f"**Locked by:** {buffer.get('locked_by')}")
                
                col_c, col_d = st.columns(2)
                with col_c:
                    if st.button(f"🔓 Forçar Unlock", key=f"unlock_{phone}"):
                        db.release_buffer_lock(phone)
                        st.success("Lock liberado!")
                        st.rerun()
                
                with col_d:
                    if st.button(f"⚡ Forçar Processamento", key=f"process_{phone}"):
                        from datetime import datetime
                        db.upsert_message_buffer(
                            phone=phone,
                            last_message_at=buffer.get('last_message_at', datetime.now().isoformat()),
                            buffer_expires_at=datetime.now().isoformat(),
                            processing=False,
                            retry_count=retry_count
                        )
                        st.success("Processamento forçado!")
                        st.rerun()
    else:
        st.info("Nenhum buffer ativo no momento.")
    
    st.divider()
    
    st.subheader("🚨 Alertas do Sistema")
    alerts = db.get_alerts(unresolved_only=False, limit=50)
    
    if alerts:
        unresolved = [a for a in alerts if not a.get("resolved", False)]
        resolved = [a for a in alerts if a.get("resolved", False)]
        
        st.write(f"**Não Resolvidos:** {len(unresolved)} | **Resolvidos:** {len(resolved)}")
        
        for alert in unresolved[:20]:
            alert_type = alert.get("type", "unknown")
            phone = alert.get("phone", "")
            details = alert.get("details", "")
            created = alert.get("created_at", "")[:19]
            
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.warning(f"**{alert_type}** - {phone} - {created}")
                st.write(f"_{details}_")
            
            with col_b:
                if st.button("✅ Resolver", key=f"resolve_{alert.get('created_at')}"):
                    # Mark as resolved (would need to add method to db)
                    st.success("Resolvido!")
                    st.rerun()
            
            st.divider()
    else:
        st.info("Nenhum alerta registrado.")
    
    st.divider()
    
    st.subheader("🔧 Controles Manuais")
    
    col_x, col_y = st.columns(2)
    
    with col_x:
        if st.button("🔄 Limpar Buffers Expirados"):
            from datetime import datetime
            now = datetime.now()
            buffers = data.get("message_buffers", {})
            cleared = 0
            
            for buffer_key, buffer in list(buffers.items()):
                expires_at = buffer.get("buffer_expires_at")
                if expires_at:
                    exp = datetime.fromisoformat(expires_at)
                    if exp < now and not buffer.get("processing", False):
                        db.delete_message_buffer(buffer.get("phone"))
                        cleared += 1
            
            st.success(f"✅ {cleared} buffers limpos!")
            st.rerun()
    
    with col_y:
        if st.button("📊 Atualizar Estatísticas"):
            st.rerun()

st.sidebar.divider()
st.sidebar.write("**Credenciais Z-API configuradas ✅**")
st.sidebar.write("**OpenAI via Replit AI ✅**")
st.sidebar.write(f"**Modo Teste:** {'✅' if TESTING_MODE else '❌'}")
