import streamlit as st
from pymongo import MongoClient
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(
    page_title="Golden Investimentos",  # Título do site
    page_icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTdhwlXGNiQQDGJMaguIQPWNdsWhZbiSwSSQg&s",  # Ícone do site (emoji ou URL para uma imagem)
    layout="centered",  # Layout: 'centered' ou 'wide'
)

# Configuração do Banco de Dados MongoDB
def init_db():
    mongo_uri = os.getenv("MONGO_URI")  # Lê a string de conexão do .env
    if not mongo_uri:
        st.error("A variável MONGO_URI não está definida no arquivo .env.")
        return None

    client = MongoClient(mongo_uri)
    db = client["golden"]  # Nome do banco de dados
    collection = db["seguros_formulario"]  # Nome da coleção
    return collection

# Salvar respostas no MongoDB
def save_response(collection, cliente, respostas, assessor):
    document = {
        "cliente": cliente,
        "assessor": assessor,
        "respostas": respostas  # Salva todas as perguntas e respostas em uma única estrutura
    }
    collection.insert_one(document)

# Inicializar a conexão com o banco de dados
collection = init_db()

# Lista de perguntas
perguntas = [
    "Qual o valor total de seus bens imóveis? (apartamento, loteamento, etc.)",
    "Quais bens móveis você possui (veículos, lanchas etc.) e qual o valor estimado de cada um?",
    "Qual o valor total de suas aplicações financeiras líquidas, incluindo a carteira XP?",
    "Existe algum planejamento sucessório, como testamento ou doação em vida? Essa situação o preocupa?",
    "Há a intenção de realizar a retirada de recursos da carteira para a aquisição de imóveis nos próximos dois anos?",
    "Há a intenção de realizar a retirada de recursos da carteira para a aquisição de veículos nos próximos dois anos?",
    "Possui algum financiamento ativo? Em caso afirmativo, qual a taxa de juros contratada?",
    "Possui algum consórcio ativo? Em caso afirmativo, qual o valor da carta de crédito, o prazo e o objetivo do consórcio?"
]

# Obter o valor de "assessor"
assessor = st.query_params["assessor"] if "assessor" in st.query_params else "Desconhecido"
# Mostrar a imagem de fundo
st.image("background.jpeg", use_column_width=True)

# Verificar se é administrador
if assessor.lower() == "admin":
    # Exibir conteúdo de administração
    st.title("Administrador - Controle")
    data = list(collection.find())  # Obter os documentos do MongoDB

    # Criar um DataFrame com as respostas
    if data:
        df_respostas = pd.DataFrame(data)
        df_respostas.drop("_id", axis=1, inplace=True)  # Remover a coluna _id gerada pelo MongoDB
        # Exibir a tabela de respostas
        st.dataframe(df_respostas)
    else:
        st.write("Nenhuma resposta encontrada.")
else:
    # Formulário para clientes
    st.title("Formulário de Levantamento de Informações")
    st.write(f"Assessor responsável: {assessor}")

    # Formulário
    with st.form("formulario"):
        cliente = st.text_input("Seu nome (cliente):")
        respostas = {}
        
        # Gerar perguntas dinamicamente
        for i, pergunta in enumerate(perguntas, 1):
            resposta = st.text_input(f"Pergunta {i}: {pergunta}")
            respostas[f"pergunta_{i}"] = {"texto": pergunta, "resposta": resposta}

        submit = st.form_submit_button("Enviar")

    if submit:
        if cliente.strip():
            # Salvar no banco com o nome do assessor e respostas
            save_response(collection, cliente, respostas, assessor)
            st.success("Respostas enviadas com sucesso!")
        else:
            st.error("Por favor, insira seu nome.")
