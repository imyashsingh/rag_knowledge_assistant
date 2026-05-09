# RAG Knowledge Assistant

A RAG (Retrieval-Augmented Generation) powered knowledge assistant that allows users to upload documents and query them using AI.

## Recent Changes (2026-05-10)

### 1. Chat UI Redesign
- **WhatsApp-style single-column layout**: Removed sidebar, implemented continuous message flow
- **Fixed layout issues**: Chat page now fits properly within layout without expanding
- **Conversation context**: Last 5 messages are sent to LLM for better context
- **Fixed ChatMessage type error**: Proper handling of Pydantic objects vs dictionaries

### 2. Workspace Management
- **Fixed workspace visibility**: All workspaces are now visible for switching
- **Fixed workspace deletion**: Proper cascade deletion of users, chat history, documents
- **Removed default workspace restrictions**: Users can access chat/workspaces from any workspace
- **Fixed foreign key constraints**: Proper deletion order to prevent database errors

### 3. Backend Improvements
- **Fixed ChatMessage object attribute error**: LLM now properly handles conversation history
- **Improved LLM prompting**: Better context handling, prioritizes document content
- **Fixed f-string syntax error**: Backend starts without syntax errors
- **Fixed vector search unpacking error**: Removed extra column from SQL query

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/switch-workspace` - Switch user workspace
- `GET /api/v1/auth/me` - Get current user info

### Workspaces
- `GET /api/v1/workspaces/` - List all workspaces
- `POST /api/v1/workspaces/` - Create new workspace
- `PUT /api/v1/workspaces/{id}` - Update workspace
- `DELETE /api/v1/workspaces/{id}` - Delete workspace
- `GET /api/v1/workspaces/{id}/stats` - Get workspace statistics

### Documents
- `GET /api/v1/documents/` - List documents
- `POST /api/v1/documents/` - Upload document
- `DELETE /api/v1/documents/{id}` - Delete document

### Chat
- `POST /api/v1/chat/query` - Query with conversation history support
- `GET /api/v1/chat/history` - Get chat history
- `GET /api/v1/chat/stats` - Get chat statistics
- `POST /api/v1/chat/clear-cache` - Clear RAG cache

## Frontend Components

### Pages
- **ChatPage**: WhatsApp-style chat interface with message history
- **WorkspacesPage**: Workspace management with create/edit/delete
- **DocumentsPage**: Document upload and management
- **DashboardPage**: Overview with workspace stats

### Key Features
- **Conversation History**: LLM receives last 5 messages for context
- **Document Processing**: Automatic chunking and embedding generation
- **Vector Search**: PostgreSQL pgvector for semantic search
- **Multi-workspace Support**: Users can create and switch between workspaces

## Tech Stack

### Backend
- **FastAPI**: Python web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Database with pgvector extension
- **Groq**: LLM API for responses
- **Redis**: Caching layer

### Frontend
- **React**: UI framework
- **TypeScript**: Type safety
- **TailwindCSS**: Styling
- **Zustand**: State management
- **React Query**: Server state management
- **Vite**: Build tool

## Development Setup

### Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm run dev
```

## Environment Variables

### Backend (.env)
```
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=postgresql://user:password@localhost/rag_assistant
REDIS_URL=redis://localhost:6379
```

### Common Issues & Solutions

### 1. Chat not working
- Check if documents are uploaded
- Verify backend is running
- Check conversation history is being sent

### 2. Workspace deletion error
- Fixed cascade deletion order
- Users and chat history deleted before workspace

### 3. Authentication issues
- Check token storage in localStorage
- Verify refresh token mechanism

### 4. Vector search errors
- Ensure pgvector extension is installed
- Check document embeddings are generated

## 🚀 Features

### Core Functionality
- **🔐 Secure Authentication**: JWT-based user management with workspace isolation
- **📄 Document Management**: Upload, organize, and process various document formats
- **🧠 RAG Chat System**: Intelligent conversations with source document citations
- **🏢 Workspace Management**: Multi-tenant workspace organization
- **🔍 Vector Search**: Advanced semantic search capabilities
- **🎨 Modern UI**: Responsive React frontend with dark/light themes
- **⚡ Real-time Processing**: Fast document indexing and retrieval

### Technical Stack

#### Backend
- **FastAPI**: Modern, high-performance Python web framework
- **PostgreSQL**: Robust relational database with pgvector extension
- **Redis**: High-performance caching and session storage
- **Sentence Transformers**: Advanced text embedding generation
- **Groq API**: Powerful LLM for intelligent responses
- **LangChain**: Document processing and text splitting

#### Frontend
- **React 18**: Modern frontend with hooks and concurrent features
- **TypeScript**: Full type safety and developer experience
- **Vite**: Lightning-fast development and optimized builds
- **Zustand**: Lightweight state management with persistence
- **React Query**: Intelligent server state caching
- **Tailwind CSS**: Utility-first styling with custom design system

## 🏗️ Architecture Overview

```mermaid
graph TB
    subgraph "Frontend (React)"
        A[User Interface] --> B[React Router]
        B --> C[Pages & Components]
        C --> D[Zustand Store]
        C --> E[React Query]
        D --> F[Axios Client]
        E --> F
        F --> G[Backend API]
    end
    
    subgraph "Backend (FastAPI)"
        G --> H[Authentication]
        G --> I[Document Processing]
        G --> J[RAG Chat System]
        H --> K[PostgreSQL]
        I --> L[Vector Database]
        J --> L
        J --> M[Groq LLM]
        I --> N[Redis Cache]
        J --> N
    end
```

## 🚀 Quick Start

### Prerequisites

#### System Requirements
- **Python**: 3.9 or higher
- **Node.js**: 18 or higher
- **PostgreSQL**: 13 or higher with pgvector extension
- **Redis**: 6 or higher
- **Git**: For version control

#### Required Accounts/APIs
- **Groq API Key**: For LLM functionality
- **Database**: PostgreSQL instance (local or cloud)

### One-Command Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd rag_knowledge_assistant

# Run the setup script
chmod +x setup.sh
./setup.sh

# Start the complete system
docker-compose up -d
```

### Manual Setup

#### Step 1: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your configuration

# Set up database
# Create PostgreSQL database with pgvector extension
createdb rag_knowledge_assistant
psql rag_knowledge_assistant -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Step 2: Frontend Setup

```bash
# Navigate to frontend directory (new terminal)
cd frontend

# Install dependencies
npm install

# Configure environment variables
echo "VITE_API_URL=http://localhost:8000" > .env

# Start development server
npm run dev
```

#### Step 3: Verify Setup

1. **Backend Health Check**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

2. **Frontend Access**
   - Open browser to `http://localhost:3000`
   - Should see login/register page

3. **Test Registration**
   - Create new account
   - Verify workspace creation
   - Test document upload

## 🔧 Detailed Setup Instructions

### Backend Configuration

#### Environment Variables (.env)

```bash
# Database Configuration
DB_URL=postgresql://username:password@localhost:5432/rag_knowledge_assistant

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production

# Groq API Configuration
GROQ_API_KEY=your-groq-api-key-here

# Redis Configuration
REDIS_HOST=localhost
REDIS_PASSWORD=your-redis-password

# Application Settings
APP_NAME=RAG Knowledge Assistant
DEBUG=false
ENVIRONMENT=development
```

#### Database Setup

```bash
# Install PostgreSQL with pgvector
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
sudo apt-get install postgresql-13-pgvector

# macOS (with Homebrew)
brew install postgresql@14
brew install pgvector

# Create database and user
sudo -u postgres psql
CREATE DATABASE rag_knowledge_assistant;
CREATE USER rag_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE rag_knowledge_assistant TO rag_user;
\c rag_knowledge_assistant
CREATE EXTENSION IF NOT EXISTS vector;
```

#### Redis Setup

```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Start Redis
redis-server

# Test Redis
redis-cli ping
# Should return: PONG
```

### Frontend Configuration

#### Environment Variables (.env)

```bash
# API Configuration
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=RAG Knowledge Assistant
VITE_APP_VERSION=1.0.0

# Development Settings
VITE_DEV_MODE=true
```

#### Node.js Setup

```bash
# Install Node.js (using nvm recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18

# Verify installation
node --version
npm --version
```

## 🏃‍♂️ Running the Application

### Development Mode

#### Option 1: Using Docker Compose (Recommended)

```bash
# From project root
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Option 2: Manual Development

```bash
# Terminal 1: Start Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Frontend
cd frontend
npm run dev

# Terminal 3: Start Redis (if not running as service)
redis-server
```

### Production Mode

#### Backend Production

```bash
# Build and run with Gunicorn
cd backend
source venv/bin/activate
pip install gunicorn

# Create production environment file
cp .env.example .env.production
# Update with production values

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Frontend Production

```bash
# Build for production
cd frontend
npm run build

# Serve with any web server
# Example with serve:
npm install -g serve
serve -s dist -l 3000
```

## 🧪 Testing & Verification

### Health Checks

```bash
# Backend Health
curl http://localhost:8000/api/v1/health

# Expected Response:
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000000",
  "version": "1.0.0",
  "components": {
    "database": {"status": "healthy"},
    "redis": {"status": "healthy"},
    "groq": {"status": "healthy"},
    "embeddings": {"status": "healthy"}
  }
}
```

### Integration Testing

1. **User Registration**
   - Navigate to `http://localhost:3000/register`
   - Fill registration form
   - Verify successful registration and redirect

2. **User Login**
   - Navigate to `http://localhost:3000/login`
   - Login with created credentials
   - Verify dashboard access

3. **Document Upload**
   - Go to Documents page
   - Upload a test document (.txt, .pdf, .docx, .md)
   - Verify upload success and document listing

4. **RAG Chat**
   - Go to Chat page
   - Ask a question about uploaded documents
   - Verify response with source citations

## 🐛 Troubleshooting

### Common Issues

#### Backend Issues

**Issue: Database Connection Failed**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check if pgvector is installed
psql -d your_db -c "SELECT * FROM pg_extension;"
```

**Issue: Redis Connection Failed**
```bash
# Check Redis status
redis-cli ping

# Check Redis configuration
redis-cli config get "*"
```

**Issue: Groq API Error**
```bash
# Test API key
curl -H "Authorization: Bearer $GROQ_API_KEY" \
     https://api.groq.com/openai/v1/models
```

#### Frontend Issues

**Issue: Build Fails**
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version  # Should be 18+
```

**Issue: API Connection Failed**
```bash
# Check backend is running
curl http://localhost:8000/api/v1/health

# Check environment variables
cat frontend/.env
```

### Debug Mode

#### Backend Debug
```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Run with detailed logs
uvicorn app.main:app --reload --log-level debug
```

#### Frontend Debug
```bash
# Enable verbose logging
VITE_LOG_LEVEL=debug npm run dev

# Check browser console for errors
# Chrome DevTools → Console tab
```

## 📁 Project Structure

```
rag_knowledge_assistant/
├── backend/                    # FastAPI backend application
│   ├── app/
│   │   ├── api/              # API routes and endpoints
│   │   ├── core/             # Core configuration and security
│   │   ├── models/            # Database models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   └── rag/              # RAG system components
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Backend tests
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example          # Environment template
│   └── Dockerfile            # Backend Docker configuration
├── frontend/                   # React frontend application
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/            # Route components
│   │   ├── services/         # API service layer
│   │   ├── stores/           # State management
│   │   ├── utils/            # Utility functions
│   │   └── types/            # TypeScript definitions
│   ├── public/               # Static assets
│   ├── package.json          # Node.js dependencies
│   └── vite.config.ts       # Vite configuration
├── docker-compose.yml          # Multi-service Docker setup
├── setup.sh                 # Automated setup script
└── README.md                # This file
```

## 🚀 Deployment

### Docker Deployment (Recommended)

```bash
# Build and start all services
docker-compose up -d --build

# Scale services
docker-compose up -d --scale backend=3

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Production Deployment

#### Backend Deployment

```bash
# Using Docker
docker build -t rag-backend ./backend
docker run -d -p 8000:8000 --env-file .env.production rag-backend

# Using systemd (Linux)
sudo cp backend/rag-backend.service /etc/systemd/system/
sudo systemctl enable rag-backend
sudo systemctl start rag-backend
```

#### Frontend Deployment

```bash
# Build and deploy to web server
cd frontend
npm run build
scp -r dist/* user@server:/var/www/html/

# Using Nginx configuration
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔐 Security Configuration

### Environment Security

```bash
# Generate secure JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Secure database connection
DB_URL=postgresql://user:password@host:5432/db?sslmode=require

# Redis with authentication
REDIS_PASSWORD=your-secure-redis-password
```

### API Security

- **CORS**: Configured for specific origins in production
- **Rate Limiting**: Implemented on all endpoints
- **Input Validation**: Pydantic schemas for all inputs
- **SQL Injection Prevention**: SQLAlchemy ORM protection
- **File Upload Security**: Type and size validation

## 📊 Monitoring & Maintenance

### Health Monitoring

```bash
# Backend health endpoint
curl http://localhost:8000/api/v1/health

# Database monitoring
psql -d your_db -c "SELECT count(*) FROM documents;"

# Redis monitoring
redis-cli info memory
redis-cli info stats
```

### Log Management

```bash
# Backend logs
tail -f backend/logs/app.log

# Frontend logs (development)
# Check browser console
# Check terminal output
```

## 🤝 Contributing

### Development Setup

1. **Fork repository**
2. **Create feature branch**
3. **Make changes**
4. **Run tests**
5. **Submit pull request**

### Code Standards

- **Python**: PEP 8 compliance, type hints
- **TypeScript**: Strict mode, comprehensive typing
- **Testing**: Unit and integration tests required
- **Documentation**: Update docs for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI Team**: For the excellent web framework
- **React Team**: For the amazing frontend library
- **OpenAI**: For Groq API access
- **Hugging Face**: For sentence transformers
- **PostgreSQL Team**: For the robust database with vector support

---

**Built with ❤️ for intelligent knowledge management**

## 🆘 Support

For issues and questions:
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check the `/docs` directory for detailed guides
- **Community**: Join discussions for community support
