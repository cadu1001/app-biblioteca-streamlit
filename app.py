import streamlit as st
from paginas import inicial, retirada, devolucao

# --- Configuração da página ---
st.set_page_config(page_title="Biblioteca Jr", layout="wide", page_icon="📚")

# --- CSS Global (cores e estilos originais) ---
st.markdown("""
<style>
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
/* Barra superior */
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
</style>
""", unsafe_allow_html=True)

# --- Estado ---
if "pagina" not in st.session_state:
    st.session_state.pagina = "inicial"

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

# --- Roteamento de páginas ---
if st.session_state.pagina == "inicial":
    inicial.render()
elif st.session_state.pagina == "retirada":
    retirada.render()
elif st.session_state.pagina == "devolucao":
    devolucao.render()
