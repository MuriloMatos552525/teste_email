
# Real Time Email Service - Backend

## 📧 Sobre o Projeto

O **Real Time Email Service** é uma aplicação que permite aos usuários enviar mensagens uns aos outros em tempo real, semelhante a um sistema de e-mail tradicional. Com notificações instantâneas, os usuários são informados imediatamente sobre novas mensagens recebidas, proporcionando uma experiência de comunicação ágil e eficiente.

## 🚀 Tecnologias Utilizadas

- **Python 3.12+**
- **FastAPI**: Framework web moderno e de alta performance para construir APIs com Python.
- **SQLAlchemy**: ORM (Object-Relational Mapping) para interagir com o banco de dados de forma eficiente.
- **PostgreSQL**: Banco de dados relacional robusto e escalável.
- **JWT (JSON Web Tokens)**: Para autenticação e autorização seguras.
- **WebSockets**: Para implementar notificações em tempo real.
- **Docker**: Para containerização e facilitar o deploy.
- **Azure**: Plataforma de nuvem utilizada para hospedar a aplicação.

## 🌐 Links Importantes

- **Frontend:** [https://realtime-email-frontend.vercel.app](https://realtime-email-frontend.vercel.app)
- **Documentação da API (Swagger):** [https://teste-balzani.azurewebsites.net/docs](https://teste-balzani.azurewebsites.net/docs)
- **Repositório do Backend:** [GitHub - Real Time Email Backend](https://github.com/seu-usuario/realtime-email-backend)

## 🛠️ Instalação e Configuração

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/realtime-email-backend.git
cd realtime-email-backend
```

### 2. Configure as Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
SECRET_KEY=uma_chave_secreta_segura_aqui
DB_SERVER=balzani-realtime-email-service.database.windows.net
DB_NAME=realtime_email_service
DB_USER=admin-balzani
DB_PASSWORD=Adm@2024
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DB_DRIVER=ODBC Driver 17 for SQL Server
```

> **⚠️ Atenção:** Nunca compartilhe ou exponha seu arquivo `.env`. Ele contém informações sensíveis que devem ser mantidas seguras.

### 3. Instale as Dependências

É recomendado utilizar um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure o Banco de Dados

Certifique-se de que o PostgreSQL esteja instalado e em execução. Atualize as configurações no `config.json` conforme necessário.

### 5. Execute as Migrações

Crie as tabelas no banco de dados:

```bash
python main.py
```

> A execução inicial do `main.py` criará as tabelas necessárias no banco de dados.

### 6. Inicie a Aplicação

```bash
uvicorn main:app --reload
```

A aplicação estará disponível em `http://localhost:8000`.

## 📝 Endpoints da API

A seguir, uma descrição detalhada das rotas e endpoints disponíveis na API.

### Autenticação

#### **POST** `/token`

Autentica um usuário e retorna um token JWT.

- **Parâmetros de Query:**
  - `username`: Nome de usuário.
  - `password`: Senha do usuário.

- **Resposta:**
  - `access_token`: Token JWT para autenticação.
  - `token_type`: Tipo de token (Bearer).

- **Exemplo de Requisição:**

  ```bash
  POST /token
  Content-Type: application/x-www-form-urlencoded

  username=seu_usuario&password=sua_senha
  ```

- **Exemplo de Resposta:**

  ```json
  {
    "access_token": "seu_token_jwt_aqui",
    "token_type": "bearer"
  }
  ```

### Usuários

#### **POST** `/users/`

Cria um novo usuário.

- **Corpo da Requisição:**

  ```json
  {
    "username": "novo_usuario",
    "password": "senha_segura"
  }
  ```

- **Resposta:**

  ```json
  {
    "id": 1,
    "username": "novo_usuario"
  }
  ```

#### **GET** `/users/`

Obtém a lista de usuários disponíveis (excluindo o usuário atual).

- **Cabeçalhos:**
  - `Authorization: Bearer <seu_token_jwt>`

- **Resposta:**

  ```json
  [
    {
      "id": 2,
      "username": "usuario_existente"
    },
    ...
  ]
  ```

### Mensagens

#### **POST** `/messages/`

Envia uma nova mensagem para um destinatário.

- **Cabeçalhos:**
  - `Authorization: Bearer <seu_token_jwt>`

- **Corpo da Requisição:**

  ```json
  {
    "recipient_id": 2,
    "title": "Assunto da Mensagem",
    "body": "Corpo da mensagem aqui..."
  }
  ```

- **Resposta:**

  ```json
  {
    "id": 1,
    "sender_id": 1,
    "recipient_id": 2,
    "title": "Assunto da Mensagem",
    "body": "Corpo da mensagem aqui...",
    "timestamp": "2024-04-27T12:34:56.789Z",
    "is_read": false,
    "sender_username": "remetente"
  }
  ```

#### **GET** `/messages/inbox/`

Obtém as mensagens recebidas pelo usuário autenticado.

- **Cabeçalhos:**
  - `Authorization: Bearer <seu_token_jwt>`

- **Resposta:**

  ```json
  [
    {
      "id": 1,
      "sender_id": 2,
      "recipient_id": 1,
      "title": "Re: Assunto da Mensagem",
      "body": "Resposta à sua mensagem...",
      "timestamp": "2024-04-27T13:00:00.000Z",
      "is_read": false,
      "sender_username": "destinatario"
    },
    ...
  ]
  ```

#### **GET** `/messages/outbox/`

Obtém as mensagens enviadas pelo usuário autenticado.

- **Cabeçalhos:**
  - `Authorization: Bearer <seu_token_jwt>`

- **Resposta:**

  ```json
  [
    {
      "id": 1,
      "sender_id": 1,
      "recipient_id": 2,
      "title": "Assunto da Mensagem",
      "body": "Corpo da mensagem aqui...",
      "timestamp": "2024-04-27T12:34:56.789Z",
      "is_read": false,
      "sender_username": "remetente"
    },
    ...
  ]
  ```

#### **PUT** `/messages/{message_id}/read`

Marca uma mensagem como lida.

- **Parâmetros de Path:**
  - `message_id`: ID da mensagem a ser marcada como lida.

- **Cabeçalhos:**
  - `Authorization: Bearer <seu_token_jwt>`

- **Resposta:**

  ```json
  {
    "message": "Mensagem marcada como lida"
  }
  ```

### WebSocket

#### **Conexão WebSocket** `/ws/`

Permite a comunicação em tempo real para notificações de novas mensagens e atualizações de contagem de mensagens não lidas.

- **URL de Conexão:**

  ```
  wss://teste-balzani.azurewebsites.net/ws/?token=<seu_token_jwt>
  ```

- **Eventos Enviados pelo Servidor:**
  
  - **`new_message`**
    - **Descrição:** Notifica o usuário sobre uma nova mensagem recebida.
    - **Dados:**
      ```json
      {
        "event": "new_message",
        "message": {
          "id": 2,
          "sender_id": 3,
          "sender_username": "outro_usuario",
          "title": "Nova Mensagem",
          "timestamp": "2024-04-27T14:00:00.000Z",
          "unread_count": 5
        }
      }
      ```

  - **`unread_count_updated`**
    - **Descrição:** Atualiza a contagem de mensagens não lidas.
    - **Dados:**
      ```json
      {
        "event": "unread_count_updated",
        "unread_count": 4
      }
      ```

## 🔒 Autenticação

A aplicação utiliza **JWT (JSON Web Tokens)** para autenticação e autorização. Ao realizar o login, o usuário recebe um token que deve ser enviado no cabeçalho `Authorization` com o prefixo `Bearer` em todas as requisições protegidas.

### Exemplo de Cabeçalho de Autorização

```http
Authorization: Bearer seu_token_jwt_aqui
```

## 🗂️ Estrutura do Projeto

```
realtime-email-backend/
├── auth.py
├── config.py
├── crud.py
├── database.py
├── main.py
├── models.py
├── schemas.py
├── requirements.txt
├── config.json
└── README.md
```

- **auth.py:** Contém funções relacionadas à autenticação, criação de tokens e obtenção do usuário atual.
- **config.py:** Carrega as configurações a partir do arquivo `config.json`.
- **crud.py:** Funções de CRUD (Create, Read, Update, Delete) para interagir com o banco de dados.
- **database.py:** Configuração do banco de dados e criação das sessões.
- **main.py:** Arquivo principal que inicializa a aplicação FastAPI, define as rotas e configura os WebSockets.
- **models.py:** Define os modelos do banco de dados usando SQLAlchemy.
- **schemas.py:** Define os schemas do Pydantic para validação de dados.
- **requirements.txt:** Lista das dependências do projeto.
- **config.json:** Arquivo de configuração contendo chaves e parâmetros sensíveis.
- **README.md:** Documentação deste arquivo.

## 🛡️ Segurança

- **JWT:** Utilizado para autenticação segura e controle de acesso.
- **CORS:** Configurado para permitir apenas origens confiáveis, garantindo que apenas o frontend autorizado possa interagir com a API.
- **Hash de Senhas:** As senhas dos usuários são armazenadas de forma segura utilizando hashing (bcrypt).

## ☁️ Deploy

A aplicação backend foi implementada na plataforma **Azure**, garantindo alta disponibilidade, escalabilidade e segurança. Está acessível via HTTPS no seguinte link:

- **Backend:** [https://teste-balzani.azurewebsites.net](https://teste-balzani.azurewebsites.net)

---

**Agradecimentos** por utilizar o Real Time Email Service! Se tiver alguma dúvida ou feedback, não hesite em entrar em contato.

```
