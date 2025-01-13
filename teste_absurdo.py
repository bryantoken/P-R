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

# Capturar os parâmetros da URL (atualizado)
query_params = st.experimental_get_query_params()
assessor = query_params.get("assessor", ["Desconhecido"])[0]
is_admin_page = query_params.get("page", [""])[0] == "admin"

# Exibir o banner no topo
st.image("background.jpeg", use_column_width=True)

# Painel de login (inicialmente oculto)
if 'show_login_panel' not in st.session_state:
    st.session_state.show_login_panel = False

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False  # Inicializando a chave 'logged_in'

if is_admin_page:
    # Painel de login só será exibido na rota /admin
    if not st.session_state.logged_in:
        with st.sidebar:
            st.header("Login de Administrador")
            login = st.text_input("Login", type="password")
            senha = st.text_input("Senha", type="password")
            if st.button("Login"):
                if autenticar_usuario(login, senha):
                    st.session_state.logged_in = True
                    st.success("Login bem-sucedido!")
                else:
                    st.session_state.logged_in = False
                    st.error("Login ou senha incorretos!")
    else:
        # Exibir título e opções da página de admin
        st.title("Admin - Respostas de Interesse em Seguros")

        # Exibir respostas como tabela
        conn = sqlite3.connect("respostas.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM respostas")
        dados = cursor.fetchall()
        conn.close()

        # Criar um DataFrame com as respostas
        df_respostas = pd.DataFrame(dados, columns=["ID", "Cliente", "Pergunta", "Resposta", "Assessor"])

        # Exibir a tabela de respostas no site
        st.dataframe(df_respostas)
else:
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
            save_response(cliente, pergunta, resposta, assessor)
            st.success("Resposta enviada com sucesso!")
        else:
            st.error("Por favor, insira seu nome.")
