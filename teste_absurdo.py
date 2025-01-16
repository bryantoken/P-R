import time
import streamlit as st
from pymongo import MongoClient
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(
    page_title="Golden Investimentos",
    page_icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTdhwlXGNiQQDGJMaguIQPWNdsWhZbiSwSSQg&s",
    layout="centered",
)

# Configuração do Banco de Dados MongoDB
def init_db():
    mongo_uri = st.secrets["mongo"]["MONGO_URI"]
    if not mongo_uri:
        st.error("A variável MONGO_URI não está definida no arquivo secrets.toml.")
        return None
    client = MongoClient(mongo_uri)
    db = client["golden"]
    collection = db["seguros_formulario"]
    return collection

# Salvar respostas no MongoDB
def save_response(collection, cliente, respostas, assessor):
    document = {
        "cliente": cliente,
        "assessor": assessor,
        "respostas": respostas
    }
    collection.insert_one(document)

# Processar dados para exibição
def process_data(data):
    processed_data = []
    for entry in data:
        processed_entry = {
            "cliente": entry.get("cliente", ""),
            "assessor": entry.get("assessor", "")
        }
        respostas = entry.get("respostas", {})
        for key, value in respostas.items():
            pergunta_col = f"Pergunta {key.split('_')[1]}"
            resposta_col = f"Resposta {key.split('_')[1]}"
            processed_entry[pergunta_col] = value.get("texto", "")
            processed_entry[resposta_col] = value.get("resposta", "")
        processed_data.append(processed_entry)
    return pd.DataFrame(processed_data)

# Inicializar a conexão com o banco de dados
collection = init_db()

# Lista de perguntas
perguntas = [
    "Qual o valor total de seus bens imóveis? (apartamento, loteamento, etc.)",
    "Quais bens móveis você possui (veículos, lanchas etc.) e qual o valor estimado de cada um?",
    "Qual o valor total de suas aplicações financeiras líquidas, incluindo a carteira XP?",
    "Você possui algum planejamento sucessório, como testamento ou doação em vida? Essa situação o preocupa?",
    "Há a intenção de realizar a retirada de recursos da carteira para a aquisição de imóveis nos próximos dois anos?",
    "Há a intenção de realizar a retirada de recursos da carteira para a aquisição de veículos nos próximos dois anos?",
    "Possui algum financiamento ativo? Em caso afirmativo, qual a taxa de juros contratada?",
    "Possui algum consórcio ativo? Em caso afirmativo, qual o valor da carta de crédito, o prazo e o objetivo do consórcio?"
]

# Obter o valor de "assessor"
assessor = st.query_params.get("assessor", "Desconhecido")

# Mostrar a imagem de fundo
st.image("background.jpeg", use_container_width=True)

def carrega_tabela():
    data = list(collection.find())
    if data:
        # Processar os dados para exibição
        df_respostas = process_data(data)
        st.dataframe(df_respostas)
    else:
        st.write("Nenhuma resposta encontrada.")  


# Verificar se é administrador
if assessor.lower() == "admin":
    st.title("Administrador - Controle")
    
    with st.form("formulario-admin"):
        login = st.text_input("Login")
        senha = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Enviar")
        if submit:
            if login == st.secrets["login"]["LOGIN"] and st.secrets["senha"]["SENHA"]:
                carrega_tabela()
            else:
                st.error("Login inválido.", icon="🚨")
        
else:
    # Formulário para clientes
    st.title("Formulário de Levantamento de Informações")
    st.write(f"Assessor responsável: {assessor}")

    with st.form("formulario"):
        cliente = st.text_input("Seu nome (cliente):")
        respostas = {}
        all_answered = True

        for i, pergunta in enumerate(perguntas, 1):
            resposta = st.text_input(f"Pergunta {i}: {pergunta}")
            if not resposta.strip():
                all_answered = False
            respostas[f"pergunta_{i}"] = {"texto": pergunta, "resposta": resposta}

        submit = st.form_submit_button("Enviar")

    if submit:
        with st.spinner('Processando...'):
            time.sleep(1)  # Simula o tempo de processamento
            if not cliente.strip():
                st.error("Por favor, insira seu nome.", icon="🚨")
            elif not all_answered:
                st.error("Por favor, responda todas as perguntas antes de enviar.", icon="🚨")
            else:
                save_response(collection, cliente, respostas, assessor)
                st.success("Respostas enviadas com sucesso!", icon="✅")
                
                
