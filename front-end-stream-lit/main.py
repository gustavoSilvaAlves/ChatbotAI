import streamlit as st
import requests
from urllib.parse import urlencode
import os
from dotenv import load_dotenv
import time


load_dotenv()


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
KEYCLOAK_BASE_URL = os.getenv("KEYCLOAK_BASE_URL")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
KEYCLOAK_REDIRECT_URI = os.getenv("KEYCLOAK_REDIRECT_URI")


AUTH_URL = f"{KEYCLOAK_BASE_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/auth"
TOKEN_URL = f"{KEYCLOAK_BASE_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"


st.set_page_config(page_title='Mbot - Bot da Mtec', page_icon='🤖', layout='wide')


# =============================================================================
# FUNÇÕES DE AUTENTICAÇÃO E RENOVAÇÃO DE TOKEN
# =============================================================================

def refresh_access_token():
    """Usa o refresh_token para obter um novo access_token."""
    print("Token de acesso expirado. Tentando renovar...")
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": st.session_state.get("refresh_token"),
        "client_id": KEYCLOAK_CLIENT_ID,
    }
    response = requests.post(TOKEN_URL, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})

    if response.status_code == 200:
        token_data = response.json()
        # Atualiza todos os dados do token na sessão
        st.session_state.token = token_data["access_token"]
        st.session_state.refresh_token = token_data.get("refresh_token")
        # Calcula o novo tempo de expiração (com uma margem de segurança de 30s)
        st.session_state.token_exp_time = time.time() + token_data["expires_in"] - 30
        print("Token renovado com sucesso!")
        return True
    else:
        print("Falha ao renovar o token. Forçando novo login.")
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
        return False


def get_valid_auth_headers():
    """
    Verifica se o token é válido, renova se necessário, e retorna o cabeçalho.
    """

    if 'token_exp_time' not in st.session_state:
        print("Tempo de expiração do token não encontrado. Forçando novo login.")
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


    if time.time() > st.session_state.token_exp_time:
        if not refresh_access_token():
            st.error("Sua sessão expirou. Por favor, recarregue a página para fazer login novamente.")
            st.stop()

    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"}


# =============================================================================
# FUNÇÕES DE INTERAÇÃO COM A API BACK-END
# =============================================================================

def sync_user_with_backend():
    try:
        headers = get_valid_auth_headers()
        response = requests.post(f"{API_BASE_URL}/users/sync", headers=headers)
        response.raise_for_status()
        st.session_state.user_synced = True
        print("Usuário sincronizado com o back-end com sucesso.")
    except requests.RequestException as e:
        st.error(f"Falha ao sincronizar usuário com o back-end: {e}")
        st.stop()


def create_new_chat_session(title="Nova Conversa"):
    try:
        headers = get_valid_auth_headers()
        payload = {"titulo": title}
        response = requests.post(f"{API_BASE_URL}/chats", headers=headers, json=payload)
        response.raise_for_status()
        chat_data = response.json()
        st.session_state.chat_id = chat_data["id"]
        print(f"Nova sessão de chat criada com ID: {st.session_state.chat_id} e Título: '{title}'")
    except requests.RequestException as e:
        st.error(f"Não foi possível iniciar uma nova conversa: {e}")
        st.stop()


def post_question_to_backend(chat_id, question, history, endpoint_path):
    try:
        headers = get_valid_auth_headers()
        payload = {"chat_id": chat_id, "question": question, "history": history}
        print(f"\n--- [FRONT-END] Enviando para a API ---\nPayload: {payload}\n-------------------------------------\n")
        full_url = f"{API_BASE_URL}{endpoint_path}"
        response = requests.post(full_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"answer": f"Ocorreu um erro ao contatar a API: {e}", "source_documents": []}


# =============================================================================
# LÓGICA DE AUTENTICAÇÃO E INICIALIZAÇÃO
# =============================================================================

if "token" not in st.session_state:
    query_params = st.query_params
    if "code" not in query_params:
        auth_params = {"client_id": KEYCLOAK_CLIENT_ID, "response_type": "code", "scope": "openid profile email",
                       "redirect_uri": KEYCLOAK_REDIRECT_URI}
        auth_url = f"{AUTH_URL}?{urlencode(auth_params)}"
        st.markdown(f"<meta http-equiv='refresh' content='0; URL={auth_url}'>", unsafe_allow_html=True)
        st.stop()
    else:
        code = query_params.get("code")
        if isinstance(code, list): code = code[0]
        token_payload = {"grant_type": "authorization_code", "code": code, "redirect_uri": KEYCLOAK_REDIRECT_URI,
                         "client_id": KEYCLOAK_CLIENT_ID}
        response = requests.post(TOKEN_URL, data=token_payload,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
        if response.status_code == 200:
            token_data = response.json()
            st.session_state.token = token_data["access_token"]
            st.session_state.refresh_token = token_data.get("refresh_token")
            st.session_state.token_exp_time = time.time() + token_data[
                "expires_in"] - 30
            st.session_state.user_info = requests.get(
                f"{KEYCLOAK_BASE_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/userinfo",
                headers={"Authorization": f"Bearer {st.session_state.token}"}).json()
            st.query_params.clear()
            st.rerun()
        else:
            st.error("Falha ao obter o token de acesso do Keycloak.")
            st.json(response.json())
            st.stop()

if "user_synced" not in st.session_state:
    sync_user_with_backend()

if "messages" not in st.session_state:
    st.session_state.messages = []

# =============================================================================
# INTERFACE DO CHAT
# =============================================================================

username = st.session_state.user_info.get("preferred_username", "usuário")
st.header(f'🤖 Olá, {username}! Eu sou o Mbot.')

with st.sidebar:
    st.header("Opções")
    aba = st.radio("Escolha o tipo de assistente:", ["Base de Conhecimento", "Salesforce"], key="assistant_choice")
    st.markdown("---")
    if st.button("Nova Conversa"):
        st.session_state.messages = []
        if "chat_id" in st.session_state:
            del st.session_state.chat_id
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Em que posso te ajudar?")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if "chat_id" not in st.session_state:
        chat_title = prompt[:100]
        create_new_chat_session(title=chat_title)

    endpoint = "/chat/knowledge_base" if aba == "Base de Conhecimento" else "/chat/salesforce"

    with st.spinner("Pensando..."):
        chat_id = st.session_state.get("chat_id")
        if chat_id:

            recent_messages = st.session_state.messages[-7:-1]


            recent_messages = st.session_state.messages[-5:-1]


            history_for_api = []
            for i in range(0, len(recent_messages), 2):
                user_msg = recent_messages[i]

                if i + 1 < len(recent_messages):
                    ai_msg = recent_messages[i + 1]
                    if user_msg['role'] == 'user' and ai_msg['role'] == 'assistant':
                        history_for_api.append((user_msg['content'], ai_msg['content']))


            response_data = post_question_to_backend(chat_id, prompt, history_for_api, endpoint)
            answer = response_data.get("answer", "Não recebi uma resposta válida.")
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()
        else:
            st.error("Falha ao criar a sessão de chat. Tente enviar a mensagem novamente.")
            st.session_state.messages.pop()
            st.rerun()
