# back-end-fast-api/test_endpoints.py

import pytest
from httpx import AsyncClient
from api.main import app, get_db

# Amostra de 'claims' de um token JWT para simular um usuário logado
FAKE_USER_CLAIMS = {
    "sub": "12345678-1234-1234-1234-1234567890ab",
    "email": "test@example.com",
    "preferred_username": "testuser",
    "groups": ["/financeiro"]
}


# --- Mock de Autenticação ---
async def override_get_current_user():
    return FAKE_USER_CLAIMS


# Aplicamos a substituição no nosso app FastAPI
app.dependency_overrides['get_current_user'] = override_get_current_user


# ===================================================================
# FUNÇÃO DE TESTE REAL PARA O PYTEST ENCONTRAR
# ===================================================================
@pytest.mark.asyncio
async def test_chat_with_salesforce_v2_success(mocker):
    """
    Testa o endpoint /chat/salesforce_v2 em um cenário de sucesso.
    """
    # 1. Preparação (Mock do Serviço e do CRUD)
    mocked_query_result = {"answer": "Esta é uma resposta simulada pelo LangGraph."}
    mocker.patch(
        'api.main.salesforce_v2_chat_service.query',
        return_value=mocked_query_result
    )

    # Mock para get_chat_owner para simular que o chat existe e pertence ao usuário
    # Criamos um objeto simples com os atributos necessários para o teste passar
    class MockChat:
        class MockUser:
            keycloak_id = FAKE_USER_CLAIMS["sub"]

        usuario = MockUser()

    mocker.patch('api.main.crud.get_chat_owner', return_value=MockChat())
    mocker.patch('api.main.crud.create_message', return_value=True)
    mocker.patch('api.main.get_db', return_value=None)  # Mock da dependência do DB

    request_payload = {
        "chat_id": "some-uuid-1234",
        "question": "Qual o status da NF-123?",
        "history": []
    }

    # 2. Execução
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/chat/salesforce_v2", json=request_payload)

    # 3. Verificação (Asserts)
    assert response.status_code == 200

    response_json = response.json()
    assert response_json["answer"] == "Esta é uma resposta simulada pelo LangGraph."