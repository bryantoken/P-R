import streamlit as st
import sqlite3
import pandas as pd

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

# Obter o valor de "assessor"
assessor = st.query_params["assessor"] if "assessor" in st.query_params else "Desconhecido"

# Verificar se o assessor é "admin", caso contrário, a sidebar não será exibida
if assessor == "admin":
    st.session_state.sidebar_open = True
else:
    st.session_state.sidebar_open = False

# Inicializando o estado de login, se necessário
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Se o assessor for "admin", exibir somente o painel de controle (tabela)
if assessor == "admin" and st.session_state.get("sidebar_open", False):
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

            # Exibir título e tabela de respostas
            st.title("Administrador - Controle")

            conn = sqlite3.connect("respostas.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM respostas")
            dados = cursor.fetchall()
            conn.close()

            # Criar um DataFrame com as respostas
            df_respostas = pd.DataFrame(dados, columns=["ID", "Cliente", "Pergunta", "Resposta", "Assessor"])

            # Exibir a tabela de respostas no site
            st.dataframe(df_respostas)

# Caso contrário (quando não for admin), exibir o formulário e imagem
else:
    # Exibir o banner no topo
    st.image("background.jpeg", use_container_width=True)

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
            # Salvar no banco com o nome do assessor
            save_response(cliente, pergunta, resposta, assessor)
            st.success("Resposta enviada com sucesso!")
        else:
            st.error("Por favor, insira seu nome.")
