import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import plotly.express as px

# --- Configuração da página ---
st.set_page_config(page_title="Biblioteca Jr", layout="wide", page_icon="📚")

# --- CSS ---
st.markdown("""
<style>
/* Barra superior fixa */
.top-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #001f3f;
    padding: 10px 30px;
    position: sticky;
    top: 0;
    z-index: 1000;
    border-bottom: 2px solid #0052cc;
}
.top-bar img {
    height: 55px;
}
.menu {
    display: flex;
    gap: 25px;
}
.menu button {
    background: none;
    border: none;
    color: white;
    font-weight: bold;
    font-size: 18px;
    cursor: pointer;
    transition: 0.3s;
}
.menu button:hover {
    color: #00ffff;
}
.menu .active {
    color: #00ffff;
    border-bottom: 2px solid #00ffff;
    padding-bottom: 2px;
}
body {
    background-color: #0a0f2c;
    color: white;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
h1, h2, h3 {
    color: #00ffff;
}
.stButton>button {
    background-color: #0052cc;
    color: white;
    border-radius: 8px;
    height: 40px;
    width: 160px;
    font-weight: bold;
}
.card {
    border: 1px solid #0052cc;
    padding: 15px;
    margin-bottom: 10px;
    border-radius: 10px;
    background-color: #001f3f;
    height: 120px;
}
.status-disponivel {
    background-color: #00cc66;
    color: white;
    padding: 5px;
    border-radius: 5px;
    font-weight: bold;
}
.status-alugado {
    background-color: #cc3300;
    color: white;
    padding: 5px;
    border-radius: 5px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# --- Estado da página ---
if "pagina" not in st.session_state:
    st.session_state.pagina = "inicial"
if "filtro_livro" not in st.session_state:
    st.session_state.filtro_livro = ""

# --- Barra superior ---
col1, col2 = st.columns([1, 4])
with col1:
    st.image("Logo_Superior.svg", use_container_width=False)
with col2:
    cols = st.columns(3)
    if cols[0].button("Página Inicial"):
        st.session_state.pagina = "inicial"
    if cols[1].button("Retirada"):
        st.session_state.pagina = "retirada"
    if cols[2].button("Devolução"):
        st.session_state.pagina = "devolucao"

# --- Conectar Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json", scope)
gc = gspread.authorize(creds)
planilha = gc.open("Dados_biblioteca_jr")
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

# --- Funções de atualização ---
def retirar_livro(id_livro, nome_pessoa):
    df_livros = carregar_livros()
    df_alugueis = carregar_alugueis()
    idx_livro = df_livros.index[df_livros["id_livro"] == id_livro][0]
    aba_livros.update_cell(idx_livro + 2, 4, "alugado")
    novo_id = len(df_alugueis) + 1
    aba_alugueis.append_row([novo_id, id_livro, nome_pessoa, datetime.now().strftime("%Y-%m-%d %H:%M"), ""])

def devolver_livro(id_aluguel):
    df_alugueis = carregar_alugueis()
    df_livros = carregar_livros()
    idx_aluguel = df_alugueis.index[df_alugueis["id_aluguel"] == id_aluguel][0]
    id_livro = df_alugueis.loc[idx_aluguel, "id_livro"]
    idx_livro = df_livros.index[df_livros["id_livro"] == id_livro][0]
    aba_livros.update_cell(idx_livro + 2, 4, "disponível")
    aba_alugueis.update_cell(idx_aluguel + 2, 5, datetime.now().strftime("%Y-%m-%d %H:%M"))

# --- Carregar dados ---
df_livros = carregar_livros()
df_alugueis = carregar_alugueis()

# --- Página Inicial ---
if st.session_state.pagina == "inicial":
    st.markdown(
        f"""
        <h1 style='display: flex; align-items: center;'>
            <img src='Logo_Itajr.png' style='height:50px; margin-right:10px;'/>
            Biblioteca Jr - Visão Geral
        </h1>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Livros Disponíveis", len(df_livros[df_livros["status"].str.lower() == "disponível"]))
    col2.metric("Livros Alugados", len(df_livros[df_livros["status"].str.lower() == "alugado"]))
    col3.metric("Total de Aluguéis", len(df_alugueis))

    # Pesquisa dinâmica
    def atualizar_filtro():
        st.session_state.filtro_livro = st.session_state.input_livro

    st.text_input("Digite o nome do livro", key="input_livro", on_change=atualizar_filtro)

    df_filtrado = df_livros.copy()
    if st.session_state.filtro_livro:
        df_filtrado = df_filtrado[df_filtrado["titulo"].str.contains(
            st.session_state.filtro_livro, case=False, na=False
        )]

    if not df_filtrado.empty:
        num_cols = 3
        for i in range(0, len(df_filtrado), num_cols):
            cols = st.columns(num_cols)
            for j, (_, row) in enumerate(df_filtrado.iloc[i:i+num_cols].iterrows()):
                cor_status = "status-disponivel" if row["status"].lower() == "disponível" else "status-alugado"
                with cols[j]:
                    st.markdown(f"""
                    <div class="card {cor_status}">
                    <b>{row['titulo']}</b><br>
                    <i>{row['autor']}</i><br>
                    <span>{row['status'].capitalize()}</span>
                    </div>
                    """, unsafe_allow_html=True)

    # Dashboards
    if not df_alugueis.empty:
        st.markdown("### 📊 Dashboards")
        col1, col2 = st.columns(2)

        with col1:
            df_alugueis["mes_retirada"] = df_alugueis["data_retirada"].dt.to_period("M").astype(str)
            alugueis_por_mes = df_alugueis.groupby("mes_retirada").size().reset_index(name="total")
            fig_mes = px.bar(alugueis_por_mes, x="mes_retirada", y="total", text="total",
                             labels={"mes_retirada": "Mês", "total": "Aluguéis"},
                             color_discrete_sequence=["#0052cc"])
            fig_mes.update_layout(paper_bgcolor="#0a0f2c", plot_bgcolor="#0a0f2c", font_color="white")
            st.plotly_chart(fig_mes, use_container_width=True)

        with col2:
            popularidade = df_alugueis.groupby("id_livro").size().reset_index(name="total")
            popularidade = popularidade.merge(df_livros[["id_livro", "titulo"]], on="id_livro")
            fig_pop = px.bar(popularidade, x="titulo", y="total", text="total",
                             color_discrete_sequence=["#003366"])
            fig_pop.update_layout(paper_bgcolor="#0a0f2c", plot_bgcolor="#0a0f2c", font_color="white")
            st.plotly_chart(fig_pop, use_container_width=True)

# --- Página Retirada ---
elif st.session_state.pagina == "retirada":
    st.title("📥 Retirar Livro")
    livros_disponiveis = df_livros[df_livros["status"].str.lower() == "disponível"]

    if livros_disponiveis.empty:
        st.info("Nenhum livro disponível no momento.")
    else:
        selecao = st.selectbox("Escolha o livro",
                               livros_disponiveis.apply(lambda x: f'{x["id_livro"]} - {x["titulo"]} ({x["autor"]})', axis=1))
        nome_pessoa = st.text_input("Seu nome")
        if st.button("Retirar"):
            id_livro = int(selecao.split(" - ")[0])
            if not nome_pessoa.strip():
                st.warning("Digite seu nome para retirar o livro.")
            else:
                retirar_livro(id_livro, nome_pessoa)
                st.success(f'Livro "{selecao}" retirado com sucesso!')
                st.experimental_rerun()

# --- Página Devolução ---
elif st.session_state.pagina == "devolucao":
    st.title("📤 Devolver Livro")
    pendentes = df_alugueis[df_alugueis["data_devolucao"].isna()]
    if pendentes.empty:
        st.info("Nenhum livro para devolver no momento.")
    else:
        pendentes = pendentes.merge(df_livros[["id_livro", "titulo"]], on="id_livro")
        selecao = st.selectbox("Escolha o aluguel para devolver",
                               pendentes.apply(lambda x: f'{x["id_aluguel"]} - {x["nome_pessoa"]} - {x["titulo"]}', axis=1))
        if st.button("Devolver"):
            id_aluguel = int(selecao.split(" - ")[0])
            devolver_livro(id_aluguel)
            st.success(f'Aluguel {id_aluguel} devolvido com sucesso!')
            st.experimental_rerun()
