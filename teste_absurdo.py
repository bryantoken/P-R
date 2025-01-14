import streamlit as st
import sqlite3
import pandas as pd
import re  # Para facilitar a extração do nome entre aspas

# Configuração do Banco de Dados SQLite
def init_db():
    conn = sqlite3.connect("respostas.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS respostas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT NOT NULL,
        pergunta TEXT NOT NULL,
        resposta TEXT NOT NULL,
        assessor TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def save_response(cliente, pergunta, resposta, assessor):
    conn = sqlite3.connect("respostas.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO respostas (cliente, pergunta, resposta, assessor)
    VALUES (?, ?, ?, ?)
    """, (cliente, pergunta, resposta, assessor))
    conn.commit()
    conn.close()

# Função para autenticar o login
def autenticar_usuario(login, senha):
    return login == "goldenbi" and senha == "GOLD22lock"

# Inicializar o banco de dados
init_db()

# Capturar os parâmetros da URL
query_params = st.experimental_get_query_params()  # `st.query_params` já retorna um dicionário

# Obter o valor de "assessor" entre aspas
assessor = query_params.get("assessor", ["Desconhecido"])[0]
match = re.match(r'"(.*?)"', assessor)  # Extrai tudo que está entre aspas
if match:
    assessor = match.group(1)  # Extrai o nome entre aspas

# Exibir o banner no topo
st.image("background.jpeg", use_container_width=True)

# Verificar se o usuário está logado (se a chave 'logged_in' está no session state)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False  # Inicializando a chave 'logged_in'

# Criar o layout com a coluna esquerda para o botão
col1, col2 = st.columns([1, 4])  # Dividindo a página em 2 colunas, sendo a primeira mais estreita

with col1:
    # Criar um botão para abrir a sidebar apenas quando clicado
    if st.button("Configurações", key="open_sidebar_button"):
        st.session_state.sidebar_open = True

# Mostrar painel de login apenas se o usuário abrir a sidebar
if st.session_state.get("sidebar_open", False):
    with st.sidebar:
        # Login
        if not st.session_state.logged_in:
            st.header("Login de Administrador")
            login = st.text_input("Login", placeholder="Digite seu login")
            senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            if st.button("Login"):
                if autenticar_usuario(login, senha):
                    st.session_state.logged_in = True
                    st.sidebar.success("Login bem-sucedido!")
                else:
                    st.sidebar.error("Login ou senha incorretos!")
        else:
            # Exibir título e opções da página de admin
            st.sidebar.success("Você está logado como administrador!")

            # Exibir respostas como tabela
            st.title("Admin - Respostas de Interesse em Seguros")

            conn = sqlite3.connect("respostas.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM respostas")
            dados = cursor.fetchall()
            conn.close()

            # Criar um DataFrame com as respostas
            df_respostas = pd.DataFrame(dados, columns=["ID", "Cliente", "Pergunta", "Resposta", "Assessor"])

            # Exibir a tabela de respostas no site
            st.dataframe(df_respostas)

# Formulário de cliente em outras páginas
st.title("Formulário de Interesse em Seguros")
st.write(f"Assessor responsável: {assessor}")

# Formulário
with st.form("formulario"):
    cliente = st.text_input("Seu nome (cliente):")
    pergunta = "Você pretende fechar seguro nos próximos 2 anos?"
    resposta = st.radio(pergunta, ["Sim", "Não"])
    submit = st.form_submit_button("Enviar")

if submit:
    if cliente.strip():
        # Salvar no banco com o nome do assessor limpo
        save_response(cliente, pergunta, resposta, assessor)
        st.success("Resposta enviada com sucesso!")
    else:
        st.error("Por favor, insira seu nome.")
