# paginas/devolucao.py
import streamlit as st
import conexao  # Importa o nosso novo arquivo central de conexão

def render():
    st.title("📤 Devolver Livro")

    # --- Carrega os dados usando as funções centralizadas ---
    df_alugueis = conexao.carregar_alugueis()
    df_livros = conexao.carregar_livros()
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
            # --- Usa a função de devolver centralizada ---
            conexao.devolver_livro(id_aluguel)
            st.success(f'Aluguel {id_aluguel} devolvido com sucesso!')
            st.rerun()
