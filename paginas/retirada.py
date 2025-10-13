# paginas/retirada.py
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from unidecode import unidecode
from streamlit_gsheets import GSheetsConnection

def render():
    st.title("📥 Retirar Livro")

    # --- Conexão e Funções de Dados ---
    conn = st.connection("gsheets", type=GSheetsConnection)

    @st.cache_data(ttl=60)
    def carregar_livros():
        return conn.read(worksheet="Livros")

    @st.cache_data(ttl=60)
    def carregar_alunos():
        return conn.read(worksheet="Alunos")

    def retirar_livro(id_livro, nome_pessoa):
        df_livros = carregar_livros()
        df_alugueis = conn.read(worksheet="Alugueis")
        idx_livro_planilha = df_livros.index[df_livros["id_livro"] == id_livro][0] + 2

        aba_livros = conn.client._open_spreadsheet().worksheet("Livros")
        aba_livros.update_cell(idx_livro_planilha, 4, "alugado")

        aba_alugueis = conn.client._open_spreadsheet().worksheet("Alugueis")
        novo_id = len(df_alugueis) + 1
        nova_linha = [novo_id, id_livro, nome_pessoa, datetime.now().strftime("%Y-%m-%d %H:%M"), ""]
        aba_alugueis.append_row(nova_linha)

    # --- Dados ---
    df_livros = carregar_livros()
    df_alunos = carregar_alunos()
    livros_disponiveis = df_livros[df_livros["status"].str.lower() == "disponível"]

    # --- Normalização para busca sem acento ---
    alunos_dict = {unidecode(nome).lower(): nome for nome in df_alunos["Nome"]}
    nomes_exibicao = sorted(set(df_alunos["Nome"]))

    # --- Caixa única de seleção para aluno ---
    aluno_selecionado = st.selectbox(
        "Selecione ou pesquise o aluno",
        nomes_exibicao,
        index=None,
        placeholder="Digite para pesquisar..."
    )

    # --- Seleção de livro ---
    if livros_disponiveis.empty:
        st.info("Nenhum livro disponível no momento.")
        return

    livro_selecionado = st.selectbox(
        "Escolha o livro",
        livros_disponiveis.apply(
            lambda x: f'{x["id_livro"]} - {x["titulo"]} ({x["autor"]})', axis=1
        )
    )

    if st.button("Retirar"):
        if not aluno_selecionado:
            st.warning("Por favor, selecione um aluno válido.")
        else:
            id_livro = int(livro_selecionado.split(" - ")[0])
            retirar_livro(id_livro, aluno_selecionado)
            st.success(f'Livro "{livro_selecionado}" retirado por "{aluno_selecionado}" com sucesso!')
            st.rerun()

    # --- Tabela estilizada de livros disponíveis ---
    if not livros_disponiveis.empty:
        st.markdown("### Livros Disponíveis")
        def color_row(row):
            return ['background-color: #001f3f; color: #00ffff'] * len(row)
        st.dataframe(
            livros_disponiveis[["titulo", "autor", "status"]].style.apply(color_row, axis=1),
            use_container_width=True
        )

