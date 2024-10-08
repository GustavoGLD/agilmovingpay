import streamlit as st
import toml
import os
import streamlit_authenticator as stauth
from sqlalchemy import create_engine
from streamlit_authenticator import Authenticate

st.set_page_config(page_title="Portal do Administrador", page_icon="🛠️", layout="wide")


# Funções para carregar e salvar credenciais
def load_credentials(file_path):
    with open(file_path, 'r') as file:
        data = toml.load(file)
        return data


def save_credentials(file_path, data):
    with open(file_path, 'w') as file:
        toml.dump(data, file)


# Função para carregar o caminho da pasta do projeto
def load_project_path():
    if os.path.exists('project_path.txt'):
        with open('project_path.txt', 'r') as file:
            return file.read().strip()
    return ""


# Função para salvar o caminho da pasta do projeto
def save_project_path(path):
    with open('project_path.txt', 'w') as file:
        file.write(path)


# Função para adicionar usuário
def add_user(username, password, file_path):
    try:
        data = load_credentials(file_path)
        if username in data['credentials']['usernames']:
            return "Usuário já existe. ❌"
        data['credentials']['usernames'][username] = {'name': username,
                                                      'password': str(stauth.Hasher([password]).generate()[0])}
        save_credentials(file_path, data)
        return "Usuário adicionado com sucesso! 🎉"
    except Exception as e:
        return f"Erro ao adicionar usuário: {e}"


# Função para remover usuário
def remove_user(username, file_path):
    try:
        data = load_credentials(file_path)
        if username in data['credentials']['usernames']:
            del data['credentials']['usernames'][username]
            save_credentials(file_path, data)
            return "Usuário removido com sucesso! 🗑️"
        else:
            return "Usuário não encontrado. ❌"
    except Exception as e:
        return f"Erro ao remover usuário: {e}"


# Função para listar usuários
def list_users(file_path):
    data = load_credentials(file_path)
    return list(data['credentials']['usernames'].keys())


# Função para atualizar configurações do banco de dados
def update_database_config(file_path, schema, servername, odbc_driver):
    try:
        data = load_credentials(file_path)
        data['database']['schema'] = schema
        data['database']['servername'] = servername
        data['database']['odbc_driver'] = odbc_driver
        save_credentials(file_path, data)
        return "Configurações do banco de dados atualizadas com sucesso! 🎉"
    except Exception as e:
        return f"Erro ao atualizar configurações do banco de dados: {e}"


# Função para gerar a URL de conexão e testar a conexão
def generate_connection_url(schema, servername, odbc_driver):
    url = f'mssql+pyodbc://{servername}/DbAgilMovingPay?TrustServerCertificate=yes&driver=ODBC+Driver+{odbc_driver}+for+SQL+Server'
    return url


def test_connection(url):
    try:
        engine = create_engine(url, echo=True)
        with engine.connect() as connection:
            return "Conexão bem-sucedida! 🎉"
    except Exception as e:
        return f"Erro ao conectar ao banco de dados: {e}"


def main():
    # Interface do Streamlit
    st.title("Portal do Administrador 🛠️")

    # Carregar o caminho da pasta do projeto
    project_folder = load_project_path()
    project_folder = st.text_input("Digite o caminho da pasta do projeto:", value=project_folder)
    file_path = os.path.join(project_folder, '.streamlit', 'secrets.toml')
    save_project_path(project_folder)


    if project_folder:
        st.write(f"Arquivo de credenciais localizado em: {file_path}")

        # Carregar dados do banco de dados do arquivo secrets.toml
        if os.path.exists(file_path):
            data = load_credentials(file_path)
            schema = data['database'].get('schema', 'dbo')
            servername = data['database'].get('servername', '')
            odbc_driver = data['database'].get('odbc_driver', '18')
        else:
            schema = 'dbo'
            servername = 'ATLAS-70I9J6T8U\\MSSQLSERVER02'
            odbc_driver = '18'

        # Criação das abas
        tab1, tab2 = st.tabs(["👤 Configurações de Usuários", "💾 Opções do Banco de Dados"])

        # Aba para configurações de usuários
        with tab1:
            st.header("Adicionar Usuário ➕")
            with st.form(key='add_user_form'):
                username = st.text_input("Nome de usuário:")
                password = st.text_input("Senha:", type="password")
                add_button = st.form_submit_button("Adicionar Usuário")
                if add_button:
                    if username and password:
                        result = add_user(username, password, file_path)
                        if 'sucesso' in result:
                            st.success(result)
                        else:
                            st.error(result)
                    else:
                        st.error("Por favor, preencha todos os campos.")

            st.header("Remover Usuário ➖")
            users = list_users(file_path)
            with st.form(key='remove_user_form'):
                remove_username = st.selectbox("Selecione o usuário para remover:", users)
                remove_button = st.form_submit_button("Remover Usuário")
                if remove_button:
                    if remove_username:
                        result = remove_user(remove_username, file_path)
                        if "sucesso" in result:
                            st.success(result)
                        else:
                            st.error(result)
                    else:
                        st.error("Por favor, selecione um usuário.")

            st.header("Lista de Usuários 📜")
            if st.button("Atualizar Lista"):
                users = list_users(file_path)
                if users:
                    st.write(users)
                else:
                    st.info("Nenhum usuário encontrado.")

        # Aba para opções do banco de dados
        with tab2:
            st.header("Configurações do Banco de Dados 💾")
            with st.form(key='db_config_form'):
                schema = st.text_input("Schema:", value=schema)
                servername = st.text_input("Nome do Servidor:", value=servername)
                odbc_driver = st.text_input("ODBC Driver:", value=odbc_driver)
                update_db_button = st.form_submit_button("Atualizar Configurações")
                if update_db_button:
                    if schema and servername and odbc_driver:
                        result = update_database_config(file_path, schema, servername, odbc_driver)
                        if "sucesso" in result:
                            st.success(result)
                        else:
                            st.error(result)
                    else:
                        st.error("Por favor, preencha todos os campos.")

            # Mostrar a URL gerada
            st.header("URL de Conexão 🌐")
            connection_url = generate_connection_url(schema, servername, odbc_driver)
            st.write("URL de Conexão Gerada:")
            st.code(connection_url, language="python")

            # Botão para testar a conexão
            test_connection_button = st.button("Testar Conexão")
            if test_connection_button:
                result = test_connection(connection_url)
                if "Conexão bem-sucedida" in result:
                    st.success(result)
                else:
                    st.error(result)

    # Rodapé
    st.markdown("---")
    st.markdown("Desenvolvido por SISCOF")


authenticator = Authenticate(
    st.secrets['credentials'].to_dict(),
    st.secrets['cookie']['name'],
    st.secrets['cookie']['key'],
    st.secrets['cookie']['expiry_days'],
)

name, authentication_status, username = authenticator.login()

if authentication_status:
    st.success(f'👋🙋‍♂️ Bem vindo *{name}*! Login feito com Successo!')
    st.divider()
    main()
    authenticator.logout(location='sidebar')
elif authentication_status is False:
    st.error('❌🔄 Username ou password errado! Tente novamente.')
elif authentication_status is None:
    st.warning('🔑🔒 Escreva seu usuário e senha!')
