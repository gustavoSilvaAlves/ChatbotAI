from pydantic import BaseModel, EmailStr
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
import uuid



class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    departamento: Optional[str] = None
    data_criacao: datetime

    class Config:
        from_attributes = True


class ChatCreate(BaseModel):
    titulo: Optional[str] = "Nova Conversa"


class ChatDetailResponse(BaseModel):
    id: uuid.UUID
    usuario_id: uuid.UUID
    titulo: str
    data_criacao: datetime

    class Config:
        from_attributes = True




class ChatRequest(BaseModel):
    chat_id: str
    question: str
    history: Optional[List[Tuple[str, str]]] = None



class DocumentSource(BaseModel):
    page_content: str
    metadata: Dict[str, Any]


class ChatResponse(BaseModel):
    answer: str
    source_documents: List[DocumentSource] = []
    soql_query: Optional[str] = None