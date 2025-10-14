# paginas/retirada.py
import streamlit as st
from unidecode import unidecode
import conexao  # Importa o nosso novo arquivo central de conexão
from datetime import date # NOVO: Para obter a data atual

# NOVO: Imports necessários para o envio de e-mail
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# NOVO: Função para enviar o e-mail de confirmação
def enviar_email_retirada(aluno_nome, aluno_email, livro_titulo):
    """
    Função para montar e enviar um e-mail de confirmação usando uma conta Gmail.
    As credenciais são lidas de forma segura do arquivo secrets.toml.
    """
    try:
        # Pega as credenciais do arquivo de segredos
        remetente = st.secrets["email"]["username"]
        senha = st.secrets["email"]["password"]
        destinatario = aluno_email

        # Monta a estrutura do e-mail
        mensagem = MIMEMultipart("alternative")
        mensagem["Subject"] = f"Confirmação de Retirada de Livro - {st.secrets['empresa']['nome']}"
        mensagem["From"] = remetente
        mensagem["To"] = destinatario
        
        nome_empresa = st.secrets['empresa']['nome']
        chave_pix = st.secrets['empresa']['pix']
        data_hoje = date.today().strftime('%d/%m/%Y')
        
        # Cria um corpo de e-mail em HTML
        corpo_html = f"""
        <html>
        <body>
            <h2>Olá, {aluno_nome}!</h2>
            <p>Confirmamos a retirada do livro <strong>"{livro_titulo}"</strong> em {data_hoje}.</p>
            <p>Lembre-se de efetuar o pagamento de 5 reais do aluguel para concluir o processo.</p>
            <hr>
            <h3>Dados para Pagamento:</h3>
            <p><strong>PIX:</strong> {chave_pix}</p>
            <hr>
            <p>Atenciosamente,<br>{nome_empresa}</p>
        </body>
        </html>
        """
        parte_html = MIMEText(corpo_html, "html")
        mensagem.attach(parte_html)

        # Conecta ao servidor do Gmail e envia o e-mail
        contexto = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=contexto) as server:
            server.login(remetente, senha)
            server.sendmail(remetente, destinatario, mensagem.as_string())
        
        st.info(f"E-mail de confirmação enviado para {aluno_email}.")
        return True
    except Exception as e:
        st.error(f"Não foi possível enviar o e-mail de confirmação. Erro: {e}")
        return False


def render():
    st.title("📥 Retirar Livro")

    # --- Carrega os dados usando as funções centralizadas ---
    df_livros = conexao.carregar_livros()
    df_alunos = conexao.carregar_alunos()
    livros_disponiveis = df_livros[df_livros["status"].str.lower() == "disponível"]

    # --- Normalização para busca (código original) ---
    alunos_dict = {unidecode(nome).lower(): nome for nome in df_alunos["Nome"]}
    nomes_exibicao = sorted(set(df_alunos["Nome"]))

    # --- Seleção de aluno (código original) ---
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
            
            # --- NOVO: LÓGICA DE ENVIO DE E-MAIL ---
            try:
                # 1. Encontrar o e-mail do aluno na tabela de alunos
                # Assumindo que sua tabela de alunos tenha uma coluna chamada 'Email'
                info_aluno = df_alunos.loc[df_alunos['Nome'] == aluno_selecionado]
                if not info_aluno.empty and 'Email' in info_aluno.columns:
                    email_destinatario = info_aluno['Email'].iloc[0]
                    titulo_livro_apenas = livro_selecionado.split(" - ", 1)[1].split(" (")[0]

                    # 2. Chamar a função para enviar o e-mail
                    enviar_email_retirada(
                        aluno_nome=aluno_selecionado,
                        aluno_email=email_destinatario,
                        livro_titulo=titulo_livro_apenas
                    )
                else:
                    st.warning(f"Não foi possível encontrar um e-mail para o aluno {aluno_selecionado}.")

            except Exception as e:
                st.error(f"Ocorreu um erro ao tentar enviar o e-mail. Detalhes: {e}")
            
            st.balloons()
            st.rerun()

    # --- Tabela estilizada (código original) ---
    if not livros_disponiveis.empty:
        st.markdown("### Livros Disponíveis")
        def color_row(row):
            return ['background-color: #001f3f; color: #00ffff'] * len(row)
        st.dataframe(
            livros_disponiveis[["titulo", "autor", "status"]].style.apply(color_row, axis=1),
            use_container_width=True
        )
