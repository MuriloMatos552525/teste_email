# crud.py
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models import User, Message
import schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    """
    Obtém um usuário pelo nome de usuário.
    """
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    """
    Cria um novo usuário com senha criptografada.
    """
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    """
    Autentica um usuário verificando a senha.
    """
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not pwd_context.verify(password, user.password_hash):
        return False
    return user

def get_user(db: Session, user_id: int):
    """
    Obtém um usuário pelo ID.
    """
    return db.query(User).filter(User.id == user_id).first()

def create_message(db: Session, message: schemas.MessageCreate, sender_id: int):
    """
    Cria uma nova mensagem.
    """
    db_message = Message(**message.dict(), sender_id=sender_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_inbox(db: Session, user_id: int):
    """
    Obtém a caixa de entrada de um usuário.
    """
    return db.query(Message).filter(Message.recipient_id == user_id).all()

def get_outbox(db: Session, user_id: int):
    """
    Obtém a caixa de saída de um usuário.
    """
    return db.query(Message).filter(Message.sender_id == user_id).all()

def mark_message_as_read(db: Session, message_id: int, user_id: int):
    """
    Marca uma mensagem como lida.
    """
    message = db.query(Message).filter(Message.id == message_id, Message.recipient_id == user_id).first()
    if message:
        message.is_read = True
        db.commit()
        db.refresh(message)
    return message

def get_unread_count(db: Session, user_id: int):
    """
    Obtém a contagem de mensagens não lidas.
    """
    return db.query(Message).filter(Message.recipient_id == user_id, Message.is_read == False).count()
