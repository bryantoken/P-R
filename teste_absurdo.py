import streamlit as st
import sqlite3
from urllib.parse import parse_qs

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

# Capturar os parâmetros da URL
query_params = st.experimental_get_query_params()
assessor = query_params.get("assessor", ["Desconhecido"])[0]  # Nome do parâmetro deve ser "assessor"

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

# Exibir respostas (opcional, apenas para admin)
if st.checkbox("Mostrar respostas (apenas para administradores)"):
    conn = sqlite3.connect("respostas.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM respostas")
    dados = cursor.fetchall()
    conn.close()

    st.write("### Respostas Coletadas")
    for row in dados:
        st.write(f"Cliente: {row[1]}, Pergunta: {row[2]}, Resposta: {row[3]}, Assessor: {row[4]}")
