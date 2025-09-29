import streamlit as st
from auth import keycloak
from services import api_client
from ui import chat_interface


st.set_page_config(page_title='Mbot - Bot da Mtec', page_icon='🤖', layout='wide')

# 1. Lida com autenticação
keycloak.handle_login()

# 2. Sincroniza o usuário com o back-end (só na primeira vez)
if "user_synced" not in st.session_state:
    api_client.sync_user_with_backend()

# 3. Inicializa o estado do chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Renderiza a UI
username = st.session_state.user_info.get("preferred_username", "usuário")
st.header(f'🤖 Olá, {username}! Eu sou o Mbot.')

assistant_type = chat_interface.setup_sidebar()
chat_interface.display_chat_messages()

# 5. Lógica do chat input
if prompt := st.chat_input("Em que posso te ajudar?"):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)


    if "chat_id" not in st.session_state:
        api_client.create_new_chat_session(title=prompt[:100])


    if "chat_id" in st.session_state:
        with st.spinner("Pensando..."):

            if assistant_type == "Base de Conhecimento":
                endpoint = "/chat/knowledge_base"
            elif assistant_type == "Salesforce":
                endpoint = "/chat/salesforce"
            else:
                # Opção padrão para segurança
                endpoint = "/chat/knowledge_base"
            history = chat_interface.get_chat_history_for_api()

            response_data = api_client.post_question_to_backend(
                chat_id=st.session_state.chat_id,
                question=prompt,
                history=history,
                endpoint_path=endpoint
            )

            answer = response_data.get("answer", "Não recebi uma resposta válida.")
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()
    else:
        st.error("Falha ao obter uma sessão de chat. Tente novamente.")