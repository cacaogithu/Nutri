# Sistema de Testes - Agente IA Nutricional

## 📋 Tipos de Testes Disponíveis

### 1. Testes Automatizados Rápidos ⚡

**test_database_only.py** - Testes ultra-rápidos do database (✅ Recomendado)
```bash
python tests/test_database_only.py
```
- **Duração:** < 1 segundo
- **Escopo:** Database, CRUD operations, estatísticas
- **Status:** ✅ 10/10 testes passando
- **Isolamento:** ✅ Usa database temporário, não afeta dados de produção
- **Cleanup:** ✅ Automático ao final dos testes
- **Uso:** CI/CD, desenvolvimento rápido, seguro para executar a qualquer momento

### 2. Testes de Escalação 🆘

**test_escalation.py** - Validação do fluxo de escalação humana
```bash
python test_escalation.py
```
- **Duração:** < 2 segundos
- **Escopo:** Escalação de leads e clientes, roteamento
- **Status:** ✅ Todos passando
- **Uso:** Validar feature de human handoff

### 3. Testes Completos com IA (Manual) 🤖

**IMPORTANTE:** Os testes que envolvem chamadas de IA devem ser executados manualmente através do dashboard devido ao tempo de resposta da API OpenAI.

#### Usando o Dashboard para Heavy Testing:

1. **Acesse a aba "🧪 Testar Agentes"**
   - Use números de teste diferentes: `+5511999000XXX`
   - Teste o fluxo completo de vendas
   - Teste o fluxo completo de nutrição

2. **Cenários de Teste Recomendados:**

   **Sales Agent:**
   - Primeiro contato: "Olá, gostaria de conhecer o serviço"
   - Pergunta sobre preço: "Quanto custa?"
   - Interesse: "Quero assinar!"
   - Escalação: "Preciso falar com um humano sobre uma situação especial"

   **Nutrition Agent:**
   - Início: "Olá, estou pronto para começar"
   - Nome: "Meu nome é [Nome Teste]"
   - Dados: "Peso 80kg, altura 175cm"
   - Objetivo: "Quero emagrecer de forma saudável"
   - Atividade: "Pratico musculação 3x por semana"
   - Preferências: "Não como carne vermelha"
   - Alergias: "Alergia a lactose"

3. **Verificar no Dashboard:**
   - Tab "💬 Conversas Completas": Ver histórico completo
   - Tab "👥 Clientes": Verificar dados salvos
   - Tab "📊 Visão Geral": Confirmar métricas atualizadas

## 🧹 Limpeza de Dados de Teste

**IMPORTANTE:** Os testes automatizados (test_database_only.py) usam database isolado temporário e não poluem os dados de produção.

Para limpar dados de teste manuais do dashboard:

```bash
# Backup do database atual
cp data/database.json data/database_backup.json

# Limpar apenas dados de teste (números +5511999XXXXX)
python -c "
from database import db
data = db._load()
data['leads'] = {k: v for k, v in data['leads'].items() if '+5511999' not in str(v.get('phone', ''))}
data['clients'] = {k: v for k, v in data['clients'].items() if '+5511999' not in str(v.get('phone', ''))}
data['interactions'] = [i for i in data['interactions'] if '+5511999' not in str(i.get('phone', ''))]
db._save(data)
print('✅ Dados de teste limpos!')
"
```

## 📊 Testes de Carga (Futuro)

Os arquivos `test_complete_flow.py` e `test_quick.py` contêm estrutura para testes de carga mas foram desabilitados porque chamam a API OpenAI real, causando:
- Timeouts longos (30-60 segundos por teste)
- Custo de créditos Replit
- Dados de teste misturados com dados reais

**Recomendação:** Use o dashboard para testes manuais com IA até implementarmos mocks.

## ✅ Checklist de Testes Antes de Deploy

1. ✅ Executar `test_database_only.py` (deve passar 10/10)
2. ✅ Executar `test_escalation.py` (deve passar todos)
3. ✅ Testar manualmente no dashboard:
   - Fluxo completo de vendas (lead → cliente)
   - Fluxo completo de nutrição (anamnese → plano)
   - Escalação para humano
   - Envio de mensagem manual
4. ✅ Verificar métricas no dashboard
5. ✅ Verificar logs sem erros

## 🎯 Melhorias Futuras

- [ ] Implementar mocks para OpenAI API
- [ ] Testes isolados (database temporário)
- [ ] Testes de carga automatizados
- [ ] Integração contínua (CI/CD)
- [ ] Testes de performance
- [ ] Testes de segurança automatizados

---

**Nota:** Para heavy testing em produção, use sempre números de teste com prefixo identificável (ex: `+5511999000XXX`) e limpe regularmente pelo dashboard.
