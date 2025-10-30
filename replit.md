# Sistema de Agente de IA Nutricional

## Visão Geral
Sistema completo de inteligência artificial com dois agentes especializados para WhatsApp e dashboard administrativo. Desenvolvido para escalar o produto de assinatura nutricional de R$47/mês.

## Arquitetura do Sistema

### Componentes Principais

1. **Agente de Vendas (Sales Agent)**
   - Primeiro contato no WhatsApp
   - Qualificação de leads
   - Apresentação da metodologia
   - Conversão para assinantes (R$47/mês)
   - Localização: `agent_sales.py`

2. **Agente Nutricional (Nutrition Agent)**
   - Anamnese nutricional completa
   - Geração de planos alimentares personalizados
   - Base de alimentos brasileiros (TACO)
   - Acompanhamento contínuo
   - Localização: `agent_nutrition.py`

3. **Dashboard Administrativo**
   - Interface Streamlit em `app.py`
   - Métricas em tempo real
   - Gestão de clientes e leads
   - Histórico de interações
   - Área de testes dos agentes

4. **Integração WhatsApp**
   - API: Z-API
   - Credenciais configuradas em `config.py`
   - Módulo de comunicação: `whatsapp_api.py`
   - Webhook receiver: `webhook_server.py`

5. **Sistema de IA**
   - OpenAI via Replit AI Integrations
   - Modelo: GPT-5
   - Sem necessidade de API key própria
   - Implementação: `ai_agent.py`

### Estrutura de Arquivos

```
├── app.py                    # Dashboard Streamlit principal
├── config.py                 # Configurações e credenciais
├── database.py               # Sistema de persistência JSON
├── knowledge_base.py         # Base de conhecimento nutricional
├── ai_agent.py              # Cliente OpenAI e lógica de IA
├── agent_sales.py           # Agente de vendas
├── agent_nutrition.py       # Agente nutricional
├── whatsapp_api.py          # Integração Z-API WhatsApp
├── webhook_server.py        # Servidor webhook Flask
├── message_router.py        # Roteamento de mensagens
├── admin_actions.py         # Ações administrativas
└── data/                    # Banco de dados JSON
    └── database.json
```

### Fluxo de Dados

1. **Lead entra em contato** → Agente de Vendas
2. **Lead converte** → Torna-se Cliente → Agente Nutricional
3. **Cliente responde anamnese** → IA processa e gera plano personalizado
4. **Todas interações** → Armazenadas em database.json
5. **Dashboard** → Exibe métricas e permite gestão

### Base de Conhecimento

**Questionário de Anamnese:**
- Dados pessoais (nome, idade, peso, altura)
- Histórico de saúde (doenças, medicamentos, alergias)
- Hábitos alimentares (refeições, preferências)
- Hidratação
- Atividade física
- Objetivos nutricionais
- Medidas antropométricas

**Alimentos Brasileiros (TACO):**
- Proteínas: frango, ovos, carne, peixe, feijão
- Carboidratos: arroz, batata doce, macarrão, tapioca
- Vegetais: brócolis, alface, tomate, cenoura
- Frutas: banana, maçã, mamão, laranja
- Gorduras saudáveis: azeite, castanhas

### Tecnologias Utilizadas

- **Frontend:** Streamlit
- **Backend:** Python 3.11
- **IA:** OpenAI GPT-5 (via Replit AI Integrations)
- **WhatsApp:** Z-API
- **Database:** JSON file-based
- **Webhook:** Flask
- **Libraries:** requests, pandas, openai, tenacity, flask, streamlit

### Configuração Z-API

As credenciais Z-API são armazenadas de forma segura como variáveis de ambiente:
- `Z_API_INSTANCE`: ID da instância Z-API
- `Z_API_TOKEN`: Token de autenticação Z-API

Base URL: `https://api.z-api.io/instances/{instance}/token/{token}`

**Segurança:** Nunca commite credenciais no código. Use sempre variáveis de ambiente.

### Modelo de Negócio

- **Produto:** Acompanhamento nutricional personalizado via WhatsApp
- **Preço:** R$ 47,00/mês (assinatura recorrente)
- **Automação:** 2 agentes IA (vendas + nutrição)
- **Objetivo:** Escalar sem aumentar equipe

### Funcionalidades Implementadas

✅ Agente de vendas com IA (GPT-5)
✅ Agente nutricional com IA (GPT-5)
✅ Anamnese completa automatizada
✅ Geração de planos alimentares personalizados
✅ Dashboard administrativo completo
✅ Sistema de database JSON
✅ Integração WhatsApp Z-API (segura)
✅ Webhook para mensagens recebidas
✅ Roteamento inteligente de mensagens
✅ **Escalação para atendimento humano (completa)**
  - Agentes detectam casos complexos automaticamente
  - Roteador previne respostas automáticas após escalação
  - Motivos de escalação registrados
  - Administrador pode escalar manualmente
✅ Métricas de conversão e receita
✅ Segurança: Credenciais em variáveis de ambiente

### Próximas Fases (Futuro)

- Aprendizado supervisionado com respostas aprovadas
- Integração de pagamentos para assinaturas
- Portal do cliente para visualizar planos
- Analytics avançado com funis de conversão
- Suporte multi-canal (Telegram, web chat)

### Como Usar

**Dashboard:**
```bash
streamlit run app.py --server.port 5000
```

**Webhook Server (opcional):**
```bash
python webhook_server.py
```

**Testar Agentes:**
Use a aba "🧪 Testar Agentes" no dashboard para simular conversas.

### Data Storage

Todos os dados são armazenados em `data/database.json`:
- Clientes ativos
- Leads em prospecção
- Histórico de interações
- Dados de anamnese
- Planos nutricionais
- Assinaturas ativas

### Observações Importantes

1. **OpenAI:** Sistema usa Replit AI Integrations - cobrado em créditos Replit
2. **WhatsApp:** Mensagens enviadas via Z-API usando credenciais fornecidas
3. **Database:** Sistema file-based, adequado para MVP e milhares de clientes
4. **Agentes:** Conversam em português brasileiro de forma natural
5. **Planos:** Baseados exclusivamente em alimentos da tabela TACO brasileira

## Projeto Status

- **Início do Desenvolvimento:** 30 de outubro de 2025
- **Status Atual:** MVP completo e funcional
- **Prazo Original:** 10 semanas (até 20 de novembro de 2025)
- **Investimento:** US$ 15,000

---

**Desenvolvido para escalar o negócio de nutrição com IA mantendo qualidade e personalização.**
