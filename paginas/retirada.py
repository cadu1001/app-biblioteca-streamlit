# paginas/retirada.py
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from unidecode import unidecode

def render():
    st.title("📥 Retirar Livro")

    # --- Conexão com Google Sheets ---
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json", scope)
    gc = gspread.authorize(creds)
    planilha = gc.open_by_url(
        "https://docs.google.com/spreadsheets/d/1wcRYkBqU6qMV_Cb1DLuN2yvxBWgdaevcNunFSYwQZsM/edit"
    )
    aba_livros = planilha.worksheet("Livros")
    aba_alugueis = planilha.worksheet("Alugueis")
    aba_alunos = planilha.worksheet("Alunos")

    @st.cache_data(ttl=10)
    def carregar_livros():
        return pd.DataFrame(aba_livros.get_all_records())

    @st.cache_data(ttl=10)
    def carregar_alunos():
        return pd.DataFrame(aba_alunos.get_all_records())

    def retirar_livro(id_livro, nome_pessoa):
        df_livros = carregar_livros()
        df_alugueis = pd.DataFrame(aba_alugueis.get_all_records())
        idx_livro = df_livros.index[df_livros["id_livro"] == id_livro][0]
        aba_livros.update_cell(idx_livro + 2, 4, "alugado")
        novo_id = len(df_alugueis) + 1
        aba_alugueis.append_row([novo_id, id_livro, nome_pessoa,
                                 datetime.now().strftime("%Y-%m-%d %H:%M"), ""])

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
