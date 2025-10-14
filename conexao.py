import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- Conexão Segura com Google Sheets (Método Original e Robusto) ---
@st.cache_resource(ttl=3600) # Cacheia a conexão por 1 hora
def conectar_gsheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["google_sheets_credentials"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    gc = gspread.authorize(creds)
    return gc

gc = conectar_gsheets()

# --- Acesso às Planilhas ---
@st.cache_resource(ttl=60) # Cacheia a planilha por 1 minuto
def abrir_planilha():
    return gc.open_by_url(
        "https://docs.google.com/spreadsheets/d/1wcRYkBqU6qMV_Cb1DLuN2yvxBWgdaevcNunFSYwQZsM/edit"
    )

planilha = abrir_planilha()
aba_livros = planilha.worksheet("Livros")
aba_alugueis = planilha.worksheet("Alugueis")
aba_alunos = planilha.worksheet("Alunos")


# --- Funções de Leitura e Escrita ---
@st.cache_data(ttl=10)
def carregar_livros():
    return pd.DataFrame(aba_livros.get_all_records())

@st.cache_data(ttl=10)
def carregar_alugueis():
    df = pd.DataFrame(aba_alugueis.get_all_records())
    df["data_retirada"] = pd.to_datetime(df["data_retirada"], errors="coerce")
    df["data_devolucao"] = pd.to_datetime(df["data_devolucao"], errors="coerce")
    return df

@st.cache_data(ttl=10)
def carregar_alunos():
    return pd.DataFrame(aba_alunos.get_all_records())


def retirar_livro(id_livro, nome_pessoa):
    df_livros = carregar_livros()
    df_alugueis = carregar_alugueis()
    idx_livro_planilha = df_livros.index[df_livros["id_livro"] == id_livro][0] + 2
    aba_livros.update_cell(idx_livro_planilha, 4, "alugado")
    novo_id = len(df_alugueis) + 1
    nova_linha = [novo_id, id_livro, nome_pessoa, datetime.now().strftime("%Y-%m-%d %H:%M"), ""]
    aba_alugueis.append_row(nova_linha)

def devolver_livro(id_aluguel):
    df_livros = carregar_livros()
    df_alugueis = carregar_alugueis()
    aluguel_info = df_alugueis[df_alugueis["id_aluguel"] == id_aluguel].iloc[0]
    idx_aluguel_planilha = aluguel_info.name + 2
    id_livro = aluguel_info["id_livro"]
    idx_livro_planilha = df_livros.index[df_livros["id_livro"] == id_livro][0] + 2
    aba_livros.update_cell(idx_livro_planilha, 4, "disponível")
    aba_alugueis.update_cell(idx_aluguel_planilha, 5, datetime.now().strftime("%Y-%m-%d %H:%M"))
