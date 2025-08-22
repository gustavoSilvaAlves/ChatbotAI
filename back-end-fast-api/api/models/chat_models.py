# api/models/chat_models.py
from pydantic import BaseModel, EmailStr
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
import uuid



# Modelo para a resposta ao criar/buscar um usuário (não expõe dados sensíveis)
class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    departamento: Optional[str] = None
    data_criacao: datetime

    class Config:
        from_attributes = True

# --- Modelos para Chats ---

# Modelo para criar um novo chat
class ChatCreate(BaseModel):
    titulo: Optional[str] = "Nova Conversa"

# Modelo para a resposta ao criar/buscar um chat
class ChatDetailResponse(BaseModel):
    id: uuid.UUID
    usuario_id: uuid.UUID
    titulo: str
    data_criacao: datetime

    class Config:
        from_attributes = True

# --- Modelos para a Conversa em si ---

# Modelo para a requisição de uma nova mensagem no chat
class ChatRequest(BaseModel):
    chat_id: str
    question: str
    history: Optional[List[Tuple[str, str]]] = None


# Modelo para os documentos de origem (Qdrant)
class DocumentSource(BaseModel):
    page_content: str
    metadata: Dict[str, Any]

# Modelo para a resposta final do chat
class ChatResponse(BaseModel):
    answer: str
    source_documents: List[DocumentSource] = []
    soql_query: Optional[str] = None