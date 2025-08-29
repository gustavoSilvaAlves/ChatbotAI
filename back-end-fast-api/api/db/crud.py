from sqlalchemy.orm import Session
from . import models
from api.models.chat_models import ChatCreate
import uuid




def get_user_by_keycloak_id(db: Session, keycloak_id: str):
    return db.query(models.Usuario).filter(models.Usuario.keycloak_id == keycloak_id).first()



def create_user(db: Session, user_claims: dict):
    groups = user_claims.get("groups", [])
    departamento = groups[0].lstrip('/') if groups else None

    db_user = models.Usuario(

        keycloak_id=user_claims.get("sub"),
        email=user_claims.get("email"),
        username=user_claims.get("preferred_username"),
        departamento=departamento
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



def create_chat(db: Session, usuario_id: str, chat: ChatCreate):
    db_chat = models.Chat(
        id=uuid.uuid4(),
        usuario_id=usuario_id,
        titulo=chat.titulo
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat




def get_chat_history(db: Session, chat_id: str) -> list[tuple[str, str]]:
    """Busca o histórico de mensagens de um chat específico."""
    history = []
    mensagens = db.query(models.Mensagem).filter(models.Mensagem.chat_id == chat_id).order_by(
        models.Mensagem.data_envio).all()

    user_msg = None
    for msg in mensagens:
        if msg.autor == 'user':
            user_msg = msg.conteudo
        elif msg.autor == 'ai' and user_msg:
            history.append((user_msg, msg.conteudo))
            user_msg = None
    return history


def create_message(db: Session, chat_id: str, autor: str, conteudo: str):
    """Cria e salva uma nova mensagem no banco de dados."""
    db_message = models.Mensagem(
        id=uuid.uuid4(),
        chat_id=chat_id,
        autor=autor,
        conteudo=conteudo
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_chat_owner(db: Session, chat_id: str) -> models.Chat:
    """Busca um chat pelo seu ID e retorna o objeto completo."""
    return db.query(models.Chat).filter(models.Chat.id == chat_id).first()