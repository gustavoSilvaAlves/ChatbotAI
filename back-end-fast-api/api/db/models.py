from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from .database import Base


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    keycloak_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(Text)
    email = Column(Text, unique=True, index=True)
    departamento = Column(Text, nullable=True)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())

    chats = relationship("Chat", back_populates="usuario")


class Chat(Base):
    __tablename__ = "chats"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    titulo = Column(Text, default="Nova Conversa")
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("Usuario", back_populates="chats")
    mensagens = relationship("Mensagem", back_populates="chat", cascade="all, delete-orphan")


class Mensagem(Base):
    __tablename__ = "mensagens"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.id"), nullable=False)
    autor = Column(Text, nullable=False)
    conteudo = Column(Text, nullable=False)
    data_envio = Column(DateTime(timezone=True), server_default=func.now())

    chat = relationship("Chat", back_populates="mensagens")

