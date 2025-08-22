import time
import json
import uuid
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from api.db import models, crud
from api.db.database import SessionLocal, engine
from api.models.chat_models import ChatRequest, ChatResponse, UserResponse, ChatCreate, ChatDetailResponse
from api.services.qdrant_service import QdrantChatService, qdrant_chat_service
from api.services.salesforce_service import SalesforceChatService, salesforce_chat_service
from api.security import get_current_user

print("✅ [DEBUG] Tentando conectar ao BD e criar tabelas...") # <-- Adicione esta linha
models.Base.metadata.create_all(bind=engine)
print("✅ [DEBUG] Conexão com BD e criação de tabelas OK.") # <-- Adicione esta linha

# --- Instância e Configuração do FastAPI ---

app = FastAPI(
    title="Chatbot Mtec API v2",
    description="API com persistência de conversas e integração com Qdrant e Salesforce.",
    version="2.0.0"
)

# Configuração do CORS para permitir que o frontend se comunique com a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restrinja para o domínio do seu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Dependências da API ---

# Dependência para obter uma sessão do banco de dados por requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependência para injetar o serviço do Qdrant
def get_qdrant_service() -> QdrantChatService:
    return qdrant_chat_service


# Dependência para injetar o serviço do Salesforce
def get_salesforce_service() -> SalesforceChatService:
    return salesforce_chat_service


# --- Endpoints de Gerenciamento ---

@app.post("/users/sync", response_model=UserResponse, tags=["Gerenciamento"])
def sync_user(
        db: Session = Depends(get_db),
        user_claims: dict = Depends(get_current_user)
):
    keycloak_id = user_claims.get("sub")
    if not keycloak_id:
        raise HTTPException(status_code=400, detail="Token não contém um ID de usuário (sub).")

    # Busca o usuário pelo ID do Keycloak
    db_user = crud.get_user_by_keycloak_id(db, keycloak_id=keycloak_id)

    if db_user is None:
        db_user = crud.create_user(db=db, user_claims=user_claims)

    return db_user


@app.post("/chats", response_model=ChatDetailResponse, tags=["Gerenciamento"])
def create_chat(
        chat: ChatCreate,
        db: Session = Depends(get_db),
        user_claims: dict = Depends(get_current_user)
):
    keycloak_id = user_claims.get("sub")
    if not keycloak_id:
        raise HTTPException(status_code=400, detail="Token inválido: ID do usuário não encontrado.")

    # Busca o usuário local pelo ID do Keycloak para garantir que ele foi sincronizado
    db_user = crud.get_user_by_keycloak_id(db, keycloak_id=keycloak_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não sincronizado. Chame o endpoint /users/sync primeiro.")

    # Usa o ID do banco de dados local (db_user.id) para criar o chat
    return crud.create_chat(db=db, usuario_id=db_user.id, chat=chat)

# --- Endpoints de Chat ---
@app.post("/chat/knowledge_base", response_model=ChatResponse, tags=["Chat"])
async def chat_with_knowledge_base(
        request: ChatRequest,  # <-- Usa o novo ChatRequest simplificado
        db: Session = Depends(get_db),
        service: QdrantChatService = Depends(get_qdrant_service),
        user_claims: dict = Depends(get_current_user)
):
    # --- PRINT ADICIONADO PARA VERIFICAR O RECEBIMENTO ---
    print("\n--- [BACK-END API] Requisição Recebida ---")
    print(f"Chat ID: {request.chat_id}")
    print(f"Question: {request.question}")
    print(f"History: {request.history}")
    print("-----------------------------------------\n")
    # --- FIM DO PRINT ---
    # 1. Extrai o departamento DIRETAMENTE do token validado (fonte segura)
    groups = user_claims.get("groups", [])
    if not groups:
        # Retornamos uma resposta formatada como ChatResponse para consistência
        return ChatResponse(
            answer="O seu usuário não está vinculado a um departamento. Por gentileza, peça ao administrador do sistema para configurar o seu usuário.",
            source_documents=[]
        )

        # Remove a barra inicial do nome do grupo para a lógica a seguir
    departamento_usuario = groups[0].lstrip('/')

    # Regra 2: Se o usuário é 'admin', o filtro é nulo (acesso total).
    if departamento_usuario.lower() == 'admin':
        filtro_departamento = None
        print("INFO: Usuário Admin detectado. Realizando busca global.")
    else:
        # Regra 3: Para outros usuários, o filtro é o seu próprio departamento.
        filtro_departamento = departamento_usuario
        print(f"INFO: Usuário do departamento '{filtro_departamento}'. Aplicando filtro.")

    # 2. Verifica no BD se o chat existe e a quem pertence
    chat = crud.get_chat_owner(db, chat_id=request.chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat não encontrado.")

    # OPCIONAL: Verificação extra de segurança
    if chat.usuario.keycloak_id != user_claims.get("sub"):
        raise HTTPException(status_code=403, detail="Usuário não autorizado para este chat.")

    # 3. Salva a pergunta do usuário
    crud.create_message(db, chat_id=request.chat_id, autor="usuario", conteudo=request.question)

    # 4. Busca o histórico e chama o serviço
    history_from_request = request.history or []  # Linha nova

    # 👇 E PASSE O NOVO HISTÓRICO PARA O SERVIÇO
    result = await service.query(request.question, history_from_request, filtro_departamento)

    answer = result.get("answer")

    # 5. Salva a resposta da IA e retorna
    if answer:
        crud.create_message(db, chat_id=request.chat_id, autor="bot", conteudo=answer)
    return ChatResponse(
        answer=answer,
        source_documents=result.get("source_documents", [])
    )



@app.post("/chat/salesforce", response_model=ChatResponse, tags=["Chat"])
async def chat_with_salesforce(
        request: ChatRequest,
        db: Session = Depends(get_db),
        service: SalesforceChatService = Depends(get_salesforce_service),
        user_claims: dict = Depends(get_current_user)
):
    # --- INÍCIO DA VERIFICAÇÃO DE SEGURANÇA ---

    # 1. Busca o chat no banco de dados para encontrar o dono
    chat = crud.get_chat_owner(db, chat_id=request.chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat não encontrado.")

    # 2. Compara o 'keycloak_id' do dono do chat com o 'sub' do token
    if chat.usuario.keycloak_id != user_claims.get("sub"):
        raise HTTPException(status_code=403, detail="Usuário não autorizado para este chat.")

    # --- FIM DA VERIFICAÇÃO DE SEGURANÇA ---

    # A lógica original do endpoint continua daqui para baixo
    crud.create_message(db, chat_id=request.chat_id, autor="usuario", conteudo=request.question)

    result = await service.query(request)
    answer = result.get("answer")
    soql_query = result.get("soql_query")

    if answer:
        crud.create_message(db, chat_id=request.chat_id, autor="bot", conteudo=answer)

    return ChatResponse(
        answer=answer,
        soql_query=soql_query,
        source_documents=[]
    )