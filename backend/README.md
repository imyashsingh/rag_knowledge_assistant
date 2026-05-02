# DocuMind Backend - Production-Ready RAG API

A production-ready, fully deployable RAG (Retrieval-Augmented Generation) backend built with FastAPI, PostgreSQL + pgvector, Redis, and Groq API.

## 🚀 Features

- **Authentication**: JWT with refresh token rotation
- **Document Ingestion**: Multi-format support (PDF, TXT, DOCX, Markdown)
- **RAG Pipeline**: Vector search with reranking and source citations
- **Caching**: Redis-based caching for embeddings and responses
- **Workspace Isolation**: Multi-user safe data separation
- **Production Ready**: Docker, health checks, monitoring, error handling

## 📋 Requirements

- Python 3.10+
- PostgreSQL with pgvector extension
- Redis
- Groq API key

## 🛠️ Installation

### 1. Clone and Setup

```bash
git clone <repository-url>
cd backend
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
- `DB_URL`: PostgreSQL connection string
- `JWT_SECRET`: Secret key for JWT tokens
- `GROQ_API_KEY`: Your Groq API key
- `REDIS_HOST`: Redis server host
- `REDIS_PASSWORD`: Redis password

### 5. Database Setup

```bash
# Run database migrations
alembic upgrade head

# Or create tables automatically (for development)
python -c "from app.main import app; from app.db.base import Base; from app.db.session import engine; Base.metadata.create_all(bind=engine)"
```

## 🐳 Docker Deployment

### Development

```bash
docker-compose up -d
```

### Production

```bash
# Build and run
docker build -t documind-backend .
docker run -p 8000:8000 --env-file .env documind-backend
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔗 API Endpoints

### Authentication
- `POST /api/v1/register` - Register new user
- `POST /api/v1/login` - Login user
- `POST /api/v1/refresh` - Refresh access token
- `POST /api/v1/logout` - Logout user
- `GET /api/v1/auth/me` - Get current user info

### Documents
- `POST /api/v1/documents/upload` - Upload document
- `GET /api/v1/documents/` - List documents
- `GET /api/v1/documents/{id}` - Get document
- `DELETE /api/v1/documents/{id}` - Delete document

### Chat
- `POST /api/v1/chat/query` - Ask question
- `GET /api/v1/chat/stats` - Get workspace stats
- `POST /api/v1/chat/clear-cache` - Clear cache

### Health
- `GET /api/v1/health/` - Comprehensive health check
- `GET /api/v1/health/simple` - Simple health check
- `GET /api/v1/health/ready` - Readiness probe
- `GET /api/v1/health/live` - Liveness probe

## 🏗️ Architecture

```
Client (Frontend)
      ↓
FastAPI (API Layer)
      ↓
Services Layer
      ↓
RAG Pipeline
      ↓
Redis (Cache + Tokens)
      ↓
PostgreSQL (Supabase + pgvector)
      ↓
Groq (LLM)
```

## 🔧 Configuration

### Database (PostgreSQL + pgvector)

```sql
CREATE EXTENSION IF NOT EXISTS vector;

-- Optimized vector index
CREATE INDEX idx_chunks_embedding 
ON chunks USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);
```

### Redis Strategy

| Use Case | TTL |
|----------|-----|
| Refresh tokens | 7 days |
| Embeddings cache | 24 hours |
| RAG responses | 5 minutes |

### Authentication Flow

1. **Login**: Access token (15min) + Refresh token (7days)
2. **Request**: Use access token
3. **Refresh**: Call `/refresh` to rotate tokens
4. **Security**: Refresh tokens stored in Redis

## 🚀 Deployment

### Render (Recommended)

1. Connect your GitHub repository
2. Set environment variables
3. Deploy with Dockerfile

### Supabase (Database)

1. Create Supabase project
2. Enable pgvector extension
3. Get connection string
4. Set `DB_URL` environment variable

### Upstash (Redis)

1. Create Upstash Redis database
2. Get connection details
3. Set `REDIS_HOST` and `REDIS_PASSWORD`

### Groq (LLM)

1. Get Groq API key from https://groq.com
2. Set `GROQ_API_KEY` environment variable

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## 📊 Monitoring

The application includes comprehensive health checks and monitoring:

- **Health endpoints**: `/api/v1/health/`
- **Request logging**: Automatic request/response logging
- **Error handling**: Structured error responses
- **Performance metrics**: Response time headers

## 🔒 Security Features

- JWT with refresh token rotation
- Workspace-level data isolation
- Input validation with Pydantic
- SQL injection prevention (SQLAlchemy)
- CORS configuration
- Rate limiting ready

## 📈 Performance Optimizations

- **Vector search**: pgvector with IVFFLAT index
- **Caching**: Redis for embeddings and responses
- **Batch processing**: Efficient embedding generation
- **Connection pooling**: Database and Redis connections
- **Async operations**: FastAPI async endpoints

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make your changes
4. Add tests
5. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the health endpoint: `/api/v1/health/`
2. Review the logs
3. Check environment configuration
4. Verify database and Redis connections
