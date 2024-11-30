# main.py
from collections import defaultdict
from datetime import timedelta
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware  # Import do CORS Middleware
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

import crud
import models
import schemas
from auth import get_current_user, create_access_token, get_db
from config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from database import engine

# Cria as tabelas no banco de dados
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configuração do CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://realtime-email-frontend.vercel.app"],  # Altere para a origem do seu front-end
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dicionário para armazenar conexões WebSocket ativas por nome de usuário
active_connections = defaultdict(list)

# Rota para criar um novo usuário
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Rota para criação de um novo usuário.
    """
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Nome de usuário já cadastrado")
    return crud.create_user(db=db, user=user)

# Rota para autenticação e obtenção do token JWT
@app.post("/token")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Rota para autenticação do usuário e geração de token de acesso.
    """
    print(f"Recebida requisição {request.method} em {request.url}")
    user = crud.authenticate_user(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Nome de usuário ou senha incorretos")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Rota para obter a lista de usuários (para seleção de destinatários)
@app.get("/users/", response_model=List[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Rota para obter a lista de usuários disponíveis, excluindo o usuário atual.
    """
    users = (
        db.query(models.User)
        .filter(models.User.id != current_user.id)  # Exclui o usuário atual
        .order_by(models.User.id)  # Adiciona ordenação por ID
        .offset(skip)
        .limit(limit)
        .all()
    )
    return users

# Rota para enviar uma nova mensagem
@app.post("/messages/", response_model=schemas.Message)
async def send_message(
    message: schemas.MessageCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Rota para envio de uma nova mensagem.
    """
    recipient = crud.get_user(db, user_id=message.recipient_id)
    if recipient is None:
        raise HTTPException(status_code=404, detail="Destinatário não encontrado")
    db_message = crud.create_message(db=db, message=message, sender_id=current_user.id)
    db_message.sender_username = current_user.username  # Adicionado

    # Enviar notificação se o destinatário estiver conectado
    if recipient.username in active_connections:
        unread_count = crud.get_unread_count(db, recipient.id)
        notification = {
            "event": "new_message",
            "message": {
                "id": db_message.id,
                "sender_id": db_message.sender_id,
                "sender_username": db_message.sender_username,  # Adicionado
                "title": db_message.title,
                "timestamp": db_message.timestamp.isoformat(),
                "unread_count": unread_count,
            },
        }
        for connection in active_connections[recipient.username]:
            await connection.send_json(notification)
    return db_message

# Rota para obter as mensagens recebidas (inbox)
@app.get("/messages/inbox/", response_model=List[schemas.Message])
def read_inbox(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Rota para obter as mensagens recebidas.
    """
    messages = crud.get_inbox(db=db, user_id=current_user.id)
    for message in messages:
        message.sender_username = message.sender.username  # Adicionado
    return messages

# Rota para obter as mensagens enviadas (outbox)
@app.get("/messages/outbox/", response_model=List[schemas.Message])
def read_outbox(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Rota para obter as mensagens enviadas.
    """
    messages = crud.get_outbox(db=db, user_id=current_user.id)
    for message in messages:
        message.sender_username = current_user.username  # Adicionado
    return messages

# Rota para marcar uma mensagem como lida
@app.put("/messages/{message_id}/read")
async def mark_as_read(
    message_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Rota para marcar uma mensagem como lida.
    """
    message = crud.mark_message_as_read(db=db, message_id=message_id, user_id=current_user.id)
    if not message:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada ou não autorizada")
    # Atualizar contagem de mensagens não lidas
    unread_count = crud.get_unread_count(db, current_user.id)
    notification = {
        "event": "unread_count_updated",
        "unread_count": unread_count,
    }
    if current_user.username in active_connections:
        for connection in active_connections[current_user.username]:
            await connection.send_json(notification)
    return {"message": "Mensagem marcada como lida"}

# Endpoint WebSocket para notificações em tempo real
@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    """
    Endpoint WebSocket com autenticação via token JWT.
    """
    await websocket.accept()
    token = websocket.query_params.get('token')
    if token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        # Autentica o usuário via token JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    active_connections[username].append(websocket)
    try:
        while True:
            # Mantém a conexão aberta
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections[username].remove(websocket)
