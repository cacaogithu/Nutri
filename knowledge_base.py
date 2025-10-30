ANAMNESIS_QUESTIONS = {
    "dados_pessoais": [
        {"key": "nome", "question": "Qual é o seu nome completo?", "type": "text"},
        {"key": "data_nascimento", "question": "Qual é a sua data de nascimento? (DD/MM/AAAA)", "type": "date"},
        {"key": "peso", "question": "Qual é o seu peso atual? (em kg)", "type": "number"},
        {"key": "altura", "question": "Qual é a sua altura? (em cm)", "type": "number"},
        {"key": "sexo", "question": "Sexo: (1) Masculino (2) Feminino", "type": "choice", "options": ["Masculino", "Feminino"]},
    ],
    
    "historico_saude": [
        {"key": "doencas", "question": "Você possui alguma doença diagnosticada? (Diabetes, Hipertensão, Hipotireoidismo, Colesterol alto, etc.)", "type": "text"},
        {"key": "medicamentos", "question": "Faz uso de medicamentos? Se sim, quais?", "type": "text"},
        {"key": "alergias", "question": "Possui alergias ou intolerâncias alimentares? Se sim, quais?", "type": "text"},
        {"key": "cirurgias", "question": "Já realizou cirurgias? Se sim, quais?", "type": "text"},
    ],
    
    "habitos_alimentares": [
        {"key": "refeicoes_dia", "question": "Quantas refeições você faz por dia? (1) 1-2  (2) 3  (3) 4-5  (4) 6 ou mais", "type": "choice", "options": ["1-2", "3", "4-5", "6 ou mais"]},
        {"key": "apetite", "question": "Como é o seu apetite? (1) Baixo (2) Moderado (3) Alto (4) Variável", "type": "choice", "options": ["Baixo", "Moderado", "Alto", "Variável"]},
        {"key": "preferencias", "question": "Tem preferências alimentares? (Doces, Salgados, Frituras, Vegetais, Carnes, etc.)", "type": "text"},
        {"key": "alimentos_evita", "question": "Tem algum alimento que você evita?", "type": "text"},
    ],
    
    "hidratacao": [
        {"key": "agua_dia", "question": "Quantos litros de água você bebe por dia? (1) Menos de 1L (2) 1-2L (3) 2-3L (4) Mais de 3L", "type": "choice", "options": ["Menos de 1L", "1-2L", "2-3L", "Mais de 3L"]},
    ],
    
    "atividade_fisica": [
        {"key": "pratica_exercicio", "question": "Pratica atividade física regularmente? Se sim, qual tipo e frequência?", "type": "text"},
        {"key": "intensidade", "question": "Nível de intensidade do exercício? (1) Leve (2) Moderado (3) Intenso (4) Não pratico", "type": "choice", "options": ["Leve", "Moderado", "Intenso", "Não pratico"]},
    ],
    
    "objetivos": [
        {"key": "objetivo_principal", "question": "Qual é o seu principal objetivo? (1) Emagrecimento (2) Ganho de massa muscular (3) Reeducação alimentar (4) Controle de doenças (5) Outros", "type": "choice", "options": ["Emagrecimento", "Ganho de massa muscular", "Reeducação alimentar", "Controle de doenças", "Outros"]},
        {"key": "objetivo_detalhes", "question": "Descreva brevemente seus objetivos nutricionais:", "type": "text"},
    ],
    
    "medidas": [
        {"key": "circunferencia_cintura", "question": "Circunferência da cintura (em cm, aproximado):", "type": "number"},
        {"key": "circunferencia_quadril", "question": "Circunferência do quadril (em cm, aproximado):", "type": "number"},
    ]
}

SALES_METHODOLOGY = """
METODOLOGIA NUTRICIONAL PERSONALIZADA

Nossa metodologia exclusiva combina:

1. AVALIAÇÃO COMPLETA
- Anamnese nutricional detalhada
- Análise de histórico de saúde
- Avaliação de objetivos pessoais

2. PLANO HIPERPERSONALIZADO
- Dieta baseada em alimentos brasileiros (Tabela TACO)
- Adequação às suas preferências e restrições
- Ajustes conforme seu estilo de vida e rotina

3. ACOMPANHAMENTO CONTÍNUO
- Suporte via WhatsApp 24/7
- Ajustes periódicos no plano
- Orientações nutricionais personalizadas

4. RESULTADOS COMPROVADOS
- Planos baseados em ciência nutricional
- Sem dietas restritivas ou extremas
- Foco em saúde e bem-estar sustentável

ASSINATURA: R$ 47,00/mês
- Plano nutricional completo
- Acompanhamento personalizado
- Acesso ao nutricionista IA 24/7
- Ajustes ilimitados no plano
"""

BRAZILIAN_FOODS_SAMPLE = {
    "proteinas": [
        {"nome": "Frango grelhado", "calorias": 165, "proteinas": 31, "carboidratos": 0, "gorduras": 3.6},
        {"nome": "Peito de frango", "calorias": 165, "proteinas": 31, "carboidratos": 0, "gorduras": 3.6},
        {"nome": "Ovo cozido", "calorias": 155, "proteinas": 13, "carboidratos": 1.1, "gorduras": 11},
        {"nome": "Carne bovina magra", "calorias": 250, "proteinas": 26, "carboidratos": 0, "gorduras": 15},
        {"nome": "Peixe (tilápia)", "calorias": 96, "proteinas": 20, "carboidratos": 0, "gorduras": 1.7},
        {"nome": "Feijão carioca", "calorias": 76, "proteinas": 4.8, "carboidratos": 13.6, "gorduras": 0.5},
    ],
    "carboidratos": [
        {"nome": "Arroz branco cozido", "calorias": 130, "proteinas": 2.7, "carboidratos": 28.2, "gorduras": 0.2},
        {"nome": "Arroz integral", "calorias": 124, "proteinas": 2.6, "carboidratos": 25.8, "gorduras": 1},
        {"nome": "Batata doce", "calorias": 77, "proteinas": 0.6, "carboidratos": 18.4, "gorduras": 0.1},
        {"nome": "Macarrão integral", "calorias": 124, "proteinas": 5, "carboidratos": 26, "gorduras": 0.5},
        {"nome": "Pão integral", "calorias": 253, "proteinas": 9, "carboidratos": 49, "gorduras": 3.5},
        {"nome": "Tapioca", "calorias": 70, "proteinas": 0.2, "carboidratos": 17, "gorduras": 0},
    ],
    "vegetais": [
        {"nome": "Brócolis cozido", "calorias": 25, "proteinas": 1.9, "carboidratos": 4.4, "gorduras": 0.3},
        {"nome": "Alface", "calorias": 15, "proteinas": 1.4, "carboidratos": 2.9, "gorduras": 0.2},
        {"nome": "Tomate", "calorias": 18, "proteinas": 0.9, "carboidratos": 3.9, "gorduras": 0.2},
        {"nome": "Cenoura", "calorias": 34, "proteinas": 0.6, "carboidratos": 7.7, "gorduras": 0.2},
        {"nome": "Abobrinha", "calorias": 17, "proteinas": 1.2, "carboidratos": 3.1, "gorduras": 0.3},
    ],
    "frutas": [
        {"nome": "Banana", "calorias": 89, "proteinas": 1.1, "carboidratos": 22.8, "gorduras": 0.3},
        {"nome": "Maçã", "calorias": 52, "proteinas": 0.3, "carboidratos": 13.8, "gorduras": 0.2},
        {"nome": "Mamão", "calorias": 43, "proteinas": 0.5, "carboidratos": 10.8, "gorduras": 0.1},
        {"nome": "Laranja", "calorias": 47, "proteinas": 0.9, "carboidratos": 11.8, "gorduras": 0.1},
        {"nome": "Abacate", "calorias": 160, "proteinas": 2, "carboidratos": 8.5, "gorduras": 14.7},
    ],
    "gorduras_saudaveis": [
        {"nome": "Azeite de oliva", "calorias": 884, "proteinas": 0, "carboidratos": 0, "gorduras": 100},
        {"nome": "Castanha do Pará", "calorias": 656, "proteinas": 14, "carboidratos": 12, "gorduras": 67},
        {"nome": "Amendoim", "calorias": 567, "proteinas": 25.8, "carboidratos": 16.1, "gorduras": 49.2},
    ]
}

def get_all_anamnesis_questions():
    all_questions = []
    for category, questions in ANAMNESIS_QUESTIONS.items():
        all_questions.extend(questions)
    return all_questions
