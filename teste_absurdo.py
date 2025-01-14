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

# Capturar os parâmetros da URL
query_params = st.query_params  # `st.query_params` já retorna um dicionário

# Obter o valor de "assessor" com um valor padrão e corrigir para nome completo
assessor = " ".join(query_params.get("assessor", ["Desconhecido"])).replace("%20", " ").strip()

# Remover os espaços extras do nome do assessor (tanto para exibição quanto para o banco)
assessor_clean = assessor.replace(" ", "")

# Exibir o banner no topo
st.image("background.jpeg", use_container_width=True)

# Verificar se o usuário está logado (se a chave 'logged_in' está no session state)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False  # Inicializando a chave 'logged_in'

# Criar um botão para abrir a sidebar
with st.sidebar:
    st.button("Abrir Sidebar", key="open_sidebar")

# Mostrar painel de login apenas se o usuário abrir a sidebar
if not st.session_state.logged_in:
    with st.sidebar:
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
        save_response(cliente, pergunta, resposta, assessor_clean)
        st.success("Resposta enviada com sucesso!")
    else:
        st.error("Por favor, insira seu nome.")
