# AI Waiter Order System 🍽️

An enterprise-grade AI-powered restaurant ordering system built with Django, PostgreSQL, and Groq AI.

## Features

- 🤖 Real AI waiter powered by Groq (Llama 3)
- 🛒 Smart cart management with state machine
- 📋 Full menu management
- 🔒 Enterprise security with rate limiting
- 🧪 Full test coverage
- 🐳 Docker ready

## Tech Stack

| Technology | Purpose |
|---|---|
| Django 6.0 | Web framework |
| PostgreSQL | Database |
| Groq AI | LLM provider |
| Django REST Framework | API |
| Docker | Containerization |
| pytest | Testing |

## Project Structure
AI_Waiter_Order/
├── django_ai_waiter/
│   ├── models.py          # Database models
│   ├── views.py           # API views
│   ├── serializers.py     # Request/response
│   ├── llm_client.py      # Groq AI client
│   ├── mcp_client.py      # MCP client
│   ├── mcp_server.py      # MCP server
│   ├── prompt_builder.py  # AI prompts
│   ├── cart_service.py    # Cart management
│   ├── state_machine.py   # Order state machine
│   ├── orchestrator.py    # Tool orchestrator
│   ├── chatbot_service.py # Full chatbot
│   ├── order_tools.py     # Order creation
│   ├── adapters.py        # Data adapters
│   ├── audit_logger.py    # Audit logging
│   ├── security.py        # Security middleware
│   └── app_settings.py    # Settings loader
├── example_project/
│   ├── settings.py        # Django settings
│   └── urls.py            # URL routing
├── Dockerfile             # Docker config
├── docker-compose.yml     # Docker compose
├── requirements.txt       # Dependencies
└── README.md              # This file
## Quick Start

### 1. Clone and setup

```bash
git clone <your-repo>
cd AI_Waiter_Order
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

Create `.env` file:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=ai_waiter_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
GROQ_API_KEY=your-groq-api-key
```

### 3. Run migrations

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run server

```bash
python manage.py runserver
```

### 5. Run with Docker

```bash
docker-compose up --build
```

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| /api/health/ | GET | Health check |
| /api/chat/ | POST | Chat with AI waiter |
| /admin/ | GET | Admin dashboard |

## Chat API Example

```json
POST /api/chat/
{
    "message": "Hello! What do you have on the menu?",
    "session_key": "optional-session-id",
    "table_number": "5"
}
```

Response:
```json
{
    "reply": "Welcome! Here is our menu...",
    "session_key": "uuid-here",
    "cart_context": "Cart is empty",
    "mock": false
}
```

## Running Tests

```bash
pytest
```

## Milestones Completed

- ✅ Milestone 1 — Local skeleton
- ✅ Milestone 2 — Mock chatbot
- ✅ Milestone 3 — Cart and state machine
- ✅ Milestone 4 — Real MCP + LLM
- ✅ Milestone 5 — Real order creation
- ✅ Milestone 6 — Enterprise hardening

## License

MIT License