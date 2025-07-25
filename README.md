# Fitness Tracking App Backend

A modular FastAPI backend for a comprehensive fitness tracking application.

## Project Structure

```
fit-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config/              # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── api/                 # API endpoints
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── users.py
│   │   └── dependencies.py  # Shared dependencies
│   ├── core/                # Core functionality
│   │   ├── __init__.py
│   │   ├── security.py      # Password hashing, JWT
│   │   └── exceptions.py
│   ├── models/              # Database models
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── user.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── user.py
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── user.py
│   ├── db/                  # Database configuration
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── session.py
│   └── utils/               # Utility functions
│       ├── __init__.py
│       └── validators.py
├── migrations/              # Alembic migrations
├── tests/                   # Test files
├── .env.example
├── .gitignore
├── requirements.txt
├── docker-compose.yml       # For local PostgreSQL
└── README.md
```

## Features

- JWT-based authentication
- User registration and login
- Password hashing with bcrypt
- PostgreSQL database with SQLAlchemy ORM
- Alembic for database migrations
- Modular architecture for easy scaling
- Docker Compose for local development

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up PostgreSQL:
   ```bash
   docker-compose up -d
   ```

5. Copy `.env.example` to `.env` and update values

6. Run migrations:
   ```bash
   alembic upgrade head
   ```

7. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Future Integrations

The modular structure supports easy integration of:
- AI/ML models (separate `ml/` module)
- Event systems (WebSocket support)
- Music player APIs
- External device SDKs
- Real-time data processing
- Notification systems
