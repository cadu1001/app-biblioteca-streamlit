import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

def render():
    # --- Conexão e Funções de Dados ---
    conn = st.connection("gsheets", type=GSheetsConnection)

    @st.cache_data(ttl=60)
    def carregar_livros():
        return conn.read(worksheet="Livros")

    @st.cache_data(ttl=60)
    def carregar_alugueis():
        df = conn.read(worksheet="Alugueis")
        df["data_retirada"] = pd.to_datetime(df["data_retirada"], errors="coerce")
        df["data_devolucao"] = pd.to_datetime(df["data_devolucao"], errors="coerce")
        return df

    def devolver_livro(id_aluguel):
        df_livros = carregar_livros()
        df_alugueis = carregar_alugueis()

        aluguel_info = df_alugueis[df_alugueis["id_aluguel"] == id_aluguel].iloc[0]
        idx_aluguel_planilha = aluguel_info.name + 2
        id_livro = aluguel_info["id_livro"]
        idx_livro_planilha = df_livros.index[df_livros["id_livro"] == id_livro][0] + 2

        aba_livros = conn.client._open_spreadsheet().worksheet("Livros")
        aba_livros.update_cell(idx_livro_planilha, 4, "disponível")

        aba_alugueis = conn.client._open_spreadsheet().worksheet("Alugueis")
        aba_alugueis.update_cell(idx_aluguel_planilha, 5, datetime.now().strftime("%Y-%m-%d %H:%M"))
    
    st.title("📤 Devolver Livro")
    df_alugueis = carregar_alugueis()
    df_livros = carregar_livros()
    pendentes = df_alugueis[df_alugueis["data_devolucao"].isna()]

    if pendentes.empty:
        st.info("Nenhum livro para devolver no momento.")
    else:
        pendentes = pendentes.merge(df_livros[["id_livro", "titulo"]], on="id_livro")
        selecao = st.selectbox(
            "Escolha o aluguel para devolver",
            pendentes.apply(lambda x: f'{x["id_aluguel"]} - {x["nome_pessoa"]} - {x["titulo"]}', axis=1)
        )
        if st.button("Devolver"):
            id_aluguel = int(selecao.split(" - ")[0])
            devolver_livro(id_aluguel)
            st.success(f'Aluguel {id_aluguel} devolvido com sucesso!')
            st.rerun()

