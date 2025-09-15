import requests
import streamlit as st
import config
from auth import keycloak

def sync_user_with_backend():
    """Sincroniza o usuário logado com o banco de dados do back-end."""
    try:
        headers = keycloak.get_valid_auth_headers()
        response = requests.post(f"{config.API_BASE_URL}/users/sync", headers=headers)
        response.raise_for_status()
        st.session_state.user_synced = True

    except requests.RequestException as e:
        st.error(f"Falha ao sincronizar usuário com o back-end: {e}")
        st.stop()

def create_new_chat_session(title="Nova Conversa"):
    """Cria uma nova sessão de chat no back-end."""
    try:
        headers = keycloak.get_valid_auth_headers()
        payload = {"titulo": title}
        response = requests.post(f"{config.API_BASE_URL}/chats", headers=headers, json=payload)
        response.raise_for_status()
        chat_data = response.json()
        st.session_state.chat_id = chat_data["id"]

    except requests.RequestException as e:
        st.error(f"Não foi possível iniciar uma nova conversa: {e}")
        st.stop()

def post_question_to_backend(chat_id, question, history, endpoint_path):
    """Envia a pergunta do usuário para o endpoint correto da API."""
    try:
        headers = keycloak.get_valid_auth_headers()
        payload = {"chat_id": chat_id, "question": question, "history": history}
        full_url = f"{config.API_BASE_URL}{endpoint_path}"
        response = requests.post(full_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"answer": f"Ocorreu um erro ao contatar a API: {e}", "source_documents": []}