# paginas/retirada.py
import streamlit as st
from unidecode import unidecode
import conexao  # Importa o nosso novo arquivo central de conexão

def render():
    st.title("📥 Retirar Livro")

    # --- Carrega os dados usando as funções centralizadas ---
    df_livros = conexao.carregar_livros()
    df_alunos = conexao.carregar_alunos()
    livros_disponiveis = df_livros[df_livros["status"].str.lower() == "disponível"]

    # --- Normalização para busca sem acento (código original) ---
    alunos_dict = {unidecode(nome).lower(): nome for nome in df_alunos["Nome"]}
    nomes_exibicao = sorted(set(df_alunos["Nome"]))

    # --- Caixa única de seleção para aluno (código original) ---
    aluno_selecionado = st.selectbox(
        "Selecione ou pesquise o aluno",
        nomes_exibicao,
        index=None,
        placeholder="Digite para pesquisar..."
    )

    # --- Seleção de livro (código original) ---
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
            # --- Usa a função de retirar centralizada ---
            conexao.retirar_livro(id_livro, aluno_selecionado)
            st.success(f'Livro "{livro_selecionado}" retirado por "{aluno_selecionado}" com sucesso!')
            st.rerun()

    # --- Tabela estilizada de livros disponíveis (código original) ---
    if not livros_disponiveis.empty:
        st.markdown("### Livros Disponíveis")
        def color_row(row):
            return ['background-color: #001f3f; color: #00ffff'] * len(row)
        st.dataframe(
            livros_disponiveis[["titulo", "autor", "status"]].style.apply(color_row, axis=1),
            use_container_width=True
        )
