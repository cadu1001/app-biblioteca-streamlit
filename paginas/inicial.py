# paginas/inicial.py
import streamlit as st
import pandas as pd
import plotly.express as px
import conexao  # Importa o nosso novo arquivo central de conexão

def render():
    # --- Carrega os dados usando as funções centralizadas ---
    df_livros = conexao.carregar_livros()
    df_alugueis = conexao.carregar_alugueis()

    # --- Título e logo (código original) ---
    import streamlit as st

    # Garante que a imagem está no mesmo diretório do script
    logo_path = 'Logo_Itajr.png'

    # Cria duas colunas: uma estreita para a imagem e uma larga para o título
    col1, col2 = st.columns([1, 6])

    with col1:
        # Adiciona a imagem
        st.image(logo_path, width=50)

    with col2:
        # Adiciona o título
        st.title("Biblioteca Jr - Visão Geral")

    # --- CSS personalizado (código original) ---
    st.markdown("""
        <style>
        .book-card {
            background-color: #0a0f2c;
            color: white;
            padding: 15px;
            border-radius: 15px;
            margin-bottom: 15px;
            box-shadow: 0 0 10px rgba(0,0,0,0.3);
            transition: all 0.3s ease-in-out;
            text-align: center;
            min-height: 180px;
        }
        .book-card:hover {
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(0, 204, 255, 0.7);
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Métricas (código original) ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Livros Disponíveis", len(df_livros[df_livros["status"].str.lower() == "disponível"]))
    col2.metric("Livros Alugados", len(df_livros[df_livros["status"].str.lower() == "alugado"]))
    col3.metric("Total de Aluguéis", len(df_alugueis))

    # --- Campo de busca (código original) ---
    st.text_input("🔎 Digite o nome do livro ou categoria", key="filtro_livro")
    filtro = st.session_state.filtro_livro.strip().lower() if "filtro_livro" in st.session_state else ""
    df_filtrado = df_livros.copy()
    if filtro:
        df_filtrado = df_livros[
            df_livros["titulo"].str.lower().str.contains(filtro, na=False) |
            df_livros["categoria"].str.lower().str.contains(filtro, na=False)
        ]

    # --- Exibição dos livros (código original) ---
    if not df_filtrado.empty:
        num_cols = 3
        for i in range(0, len(df_filtrado), num_cols):
            cols = st.columns(num_cols)
            for j, (_, row) in enumerate(df_filtrado.iloc[i:i+num_cols].iterrows()):
                titulo = str(row.get("titulo", "Sem título"))
                autor = str(row.get("autor", "Desconhecido"))
                categoria = str(row.get("categoria", ""))
                status = str(row.get("status", ""))
                sinopse = str(row.get("sinopse", "")).strip()

                cor_status = "#00ff99" if status.lower() == "disponível" else "#ff4d4d"

                with cols[j]:
                    st.markdown(f"""
                    <div class="book-card">
                        <b>{titulo}</b><br>
                        <i>{autor}</i><br>
                        <span style='color:#1ecbe1; font-weight:600;'>{categoria}</span><br>
                        <span style='color:{cor_status}'>{status.capitalize()}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    with st.expander(f"📖 Sinopse de {titulo}", expanded=False):
                        if sinopse:
                            st.markdown(f"<p style='text-align: justify;'>{sinopse}</p>", unsafe_allow_html=True)
                        else:
                            st.markdown("<i>Sinopse não disponível.</i>", unsafe_allow_html=True)
    else:
        st.info("Nenhum livro encontrado com esse filtro.")

    # --- Dashboards (código original) ---
    if not df_alugueis.empty:
        st.markdown("### 📊 Dashboards")
        c1, c2 = st.columns(2)

        with c1:
            df_alugueis["mes_retirada"] = df_alugueis["data_retirada"].dt.strftime('%Y-%m')
            alugueis_por_mes = df_alugueis.groupby("mes_retirada").size().reset_index(name="total")

            alugueis_por_mes['mes_retirada'] = alugueis_por_mes['mes_retirada'].astype(str)
            
            fig_mes = px.bar(
                alugueis_por_mes, x="mes_retirada", y="total", text="total",
                labels={"mes_retirada": "Mês", "total": "Aluguéis"},
                color_discrete_sequence=["#0052cc"]
            )
            fig_mes.update_layout(paper_bgcolor="#0a0f2c", plot_bgcolor="#0a0f2c", font_color="white")
            st.plotly_chart(fig_mes, use_container_width=True)

        with c2:
            pop = df_alugueis.groupby("id_livro").size().reset_index(name="total")
            pop = pop.merge(df_livros[["id_livro", "titulo"]], on="id_livro")
            fig_pop = px.bar(
                pop, x="titulo", y="total", text="total",
                color_discrete_sequence=["#003366"]
            )
            fig_pop.update_layout(paper_bgcolor="#0a0f2c", plot_bgcolor="#0a0f2c", font_color="white")
            st.plotly_chart(fig_pop, use_container_width=True)



