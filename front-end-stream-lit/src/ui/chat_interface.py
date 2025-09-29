import streamlit as st


def setup_sidebar():
    """Configura e exibe a barra lateral com as opções."""
    with st.sidebar:
        st.header("Opções")
        assistant_choice = st.radio(
            "Escolha o tipo de assistente:",
            ["Base de Conhecimento", "Salesforce"],
            key="assistant_choice"
        )

        st.markdown("---")

        if st.button("Nova Conversa"):
            st.session_state.messages = []
            if "chat_id" in st.session_state:
                del st.session_state.chat_id
            st.rerun()

    return assistant_choice


def display_chat_messages():
    """Exibe o histórico de mensagens do chat na tela."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def get_chat_history_for_api():
    """Prepara o histórico recente de mensagens para ser enviado à API."""

    recent_messages = st.session_state.messages[-7:-1]
    history = []

    for i in range(0, len(recent_messages), 2):
        if i + 1 < len(recent_messages) and \
                recent_messages[i]['role'] == 'user' and \
                recent_messages[i + 1]['role'] == 'assistant':
            user_msg = recent_messages[i]['content']
            ai_msg = recent_messages[i + 1]['content']
            history.append((user_msg, ai_msg))

    return history