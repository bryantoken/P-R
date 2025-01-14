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

# Inicializar o banco de dados
init_db()

# Obter o valor de "assessor"
assessor = st.query_params["assessor"] if "assessor" in st.query_params else "Desconhecido"

# Mostrar a imagem de fundo
st.image("background.jpeg", use_container_width=True)

# Verificar se é administrador
if assessor.lower() == "admin":
    # Exibir conteúdo de administração
    st.title("Administrador - Controle")
    conn = sqlite3.connect("respostas.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM respostas")
    dados = cursor.fetchall()
    conn.close()

    # Criar um DataFrame com as respostas
    df_respostas = pd.DataFrame(dados, columns=["ID", "Cliente", "Pergunta", "Resposta", "Assessor"])

    # Exibir a tabela de respostas
    st.dataframe(df_respostas)
else:
    # Formulário para clientes
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
