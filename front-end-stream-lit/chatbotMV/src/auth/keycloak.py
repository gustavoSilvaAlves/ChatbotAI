import streamlit as st
import requests
import time
from urllib.parse import urlencode
import config


def handle_login():
    """Gerencia todo o fluxo de login e obtenção de token."""
    if "token" in st.session_state:
        return True

    query_params = st.query_params
    if "code" not in query_params:
        auth_params = {
            "client_id": config.KEYCLOAK_CLIENT_ID,
            "response_type": "code",
            "scope": "openid profile email",
            "redirect_uri": config.KEYCLOAK_REDIRECT_URI,
        }
        auth_url = f"{config.AUTH_URL}?{urlencode(auth_params)}"
        st.markdown(f"<meta http-equiv='refresh' content='0; URL={auth_url}'>", unsafe_allow_html=True)
        st.stop()
    else:
        code = query_params.get("code")
        if isinstance(code, list):
            code = code[0]

        token_payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": config.KEYCLOAK_REDIRECT_URI,
            "client_id": config.KEYCLOAK_CLIENT_ID,
        }

        response = requests.post(
            config.TOKEN_URL,
            data=token_payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if response.status_code == 200:
            token_data = response.json()
            st.session_state.token = token_data["access_token"]
            st.session_state.refresh_token = token_data.get("refresh_token")
            st.session_state.token_exp_time = time.time() + token_data["expires_in"] - 30


            user_info_resp = requests.get(
                config.USERINFO_URL,
                headers={"Authorization": f"Bearer {st.session_state.token}"}
            )
            st.session_state.user_info = user_info_resp.json()
            st.query_params.clear()
            st.rerun()
        else:
            st.error("Falha ao obter o token de acesso do Keycloak.")
            st.json(response.json())
            st.stop()


def _refresh_access_token():
    """Usa o refresh_token para obter um novo access_token."""
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": st.session_state.get("refresh_token"),
        "client_id": config.KEYCLOAK_CLIENT_ID,
    }
    response = requests.post(config.TOKEN_URL, data=payload)

    if response.status_code == 200:
        token_data = response.json()
        st.session_state.token = token_data["access_token"]
        st.session_state.refresh_token = token_data.get("refresh_token")
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
    """Verifica se o token é válido, renova se necessário, e retorna o cabeçalho."""
    if 'token_exp_time' not in st.session_state:
        st.rerun()

    if time.time() > st.session_state.token_exp_time:
        if not _refresh_access_token():
            st.error("Sua sessão expirou. Por favor, recarregue a página.")
            st.stop()

    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"}