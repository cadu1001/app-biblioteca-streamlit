import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

def render():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json", scope)
    gc = gspread.authorize(creds)
    planilha = gc.open_by_url(
        "https://docs.google.com/spreadsheets/d/1wcRYkBqU6qMV_Cb1DLuN2yvxBWgdaevcNunFSYwQZsM/edit"
    )
    aba_livros = planilha.worksheet("Livros")
    aba_alugueis = planilha.worksheet("Alugueis")

    @st.cache_data(ttl=10)
    def carregar_livros():
        return pd.DataFrame(aba_livros.get_all_records())

    @st.cache_data(ttl=10)
    def carregar_alugueis():
        df = pd.DataFrame(aba_alugueis.get_all_records())
        df["data_retirada"] = pd.to_datetime(df["data_retirada"], errors="coerce")
        df["data_devolucao"] = pd.to_datetime(df["data_devolucao"], errors="coerce")
        return df

    def devolver_livro(id_aluguel):
        df_alugueis = carregar_alugueis()
        df_livros = carregar_livros()
        idx_aluguel = df_alugueis.index[df_alugueis["id_aluguel"] == id_aluguel][0]
        id_livro = df_alugueis.loc[idx_aluguel, "id_livro"]
        idx_livro = df_livros.index[df_livros["id_livro"] == id_livro][0]
        aba_livros.update_cell(idx_livro + 2, 4, "disponível")
        aba_alugueis.update_cell(idx_aluguel + 2, 5, datetime.now().strftime("%Y-%m-%d %H:%M"))

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
