# RAG Knowledge Assistant - Frontend

A modern React application for interacting with RAG (Retrieval-Augmented Generation) knowledge base, providing intelligent document search and conversational AI capabilities.

## 🚀 Features

### Core Functionality
- **🔐 Secure Authentication**: JWT-based login/register with automatic token refresh
- **📄 Document Management**: Upload, organize, and manage knowledge base documents
- **💬 Intelligent Chat**: RAG-powered conversations with source citations
- **🏢 Workspace Management**: Multi-tenant workspace organization
- **🎨 Modern UI**: Responsive design with dark/light theme support
- **⚡ Real-time Updates**: Live status updates and progress indicators

### Technical Features
- **TypeScript**: Full type safety throughout the application
- **Zustand**: Lightweight state management with persistence
- **React Query**: Intelligent server state caching and synchronization
- **Tailwind CSS**: Utility-first styling with custom design system
- **React Router**: Client-side routing with protected routes
- **Axios**: HTTP client with JWT interceptors
- **Vite**: Fast development and optimized builds

## 🛠️ Technology Stack

### Frontend Framework
- **React 18**: Modern hooks and concurrent features
- **TypeScript**: Static typing and IDE support
- **Vite**: Lightning-fast development and building

### State Management
- **Zustand**: Minimalist state management
- **React Query**: Server state and caching
- **Persist Middleware**: LocalStorage persistence

### Styling & UI
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Consistent icon system
- **Custom Components**: Reusable UI component library

### Development Tools
- **ESLint**: Code quality and consistency
- **PostCSS**: CSS processing and optimization
- **TypeScript**: Static analysis and compilation

## 📁 Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── ui/          # Base UI components (Button, Input, Card)
│   │   ├── auth/         # Authentication components
│   │   └── layout/       # Layout components
│   ├── pages/             # Route components
│   │   └── auth/         # Authentication pages
│   ├── services/           # API service layer
│   ├── stores/             # State management
│   ├── utils/              # Utility functions
│   ├── types/              # TypeScript type definitions
│   ├── constants/           # Application constants
│   ├── hooks/              # Custom React hooks
│   └── assets/             # Static assets
├── package.json            # Dependencies and scripts
├── vite.config.ts         # Vite configuration
├── tsconfig.json          # TypeScript configuration
├── tailwind.config.js     # Tailwind configuration
└── .eslintrc.cjs          # ESLint configuration
```

## 🚀 Quick Start

### Prerequisites
- **Node.js**: Version 18 or higher
- **npm**: Latest version
- **Backend**: RAG API server running on `http://localhost:8000`

### Installation

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Environment setup**
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Configure backend URL
   VITE_API_URL=http://localhost:8000
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Access application**
   - Open browser to `http://localhost:3000`
   - Register a new account or login with existing credentials

## 🔧 Development Workflow

### Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run type checking
npm run type-check

# Run linting
npm run lint

# Fix linting issues
npm run lint:fix
```

### Development Features

- **Hot Module Replacement**: Instant updates during development
- **TypeScript Integration**: Real-time type checking
- **ESLint**: Automated code quality checks
- **Source Maps**: Easy debugging in browser
- **Proxy Configuration**: Backend API proxy during development

## 🏗️ Architecture Overview

### Component Architecture

The application follows a **component-driven architecture** with clear separation of concerns:

```
┌─────────────────┐
│   App.tsx      │  # Root component with routing
├─────────────────┤
│   Layout.tsx    │  # Main application layout
├─────────────────┤
│   Pages          │  # Route components
│   ├── Dashboard   │  # Main dashboard
│   ├── Chat        │  # RAG chat interface
│   ├── Documents   │  # Document management
│   ├── Workspaces  │  # Workspace management
│   └── Settings    │  # User settings
├─────────────────┤
│   Components      │  # Reusable components
│   ├── UI          │  # Base components
│   ├── Auth        │  # Authentication
│   └── Layout      │  # Layout components
└─────────────────┘
```

### State Management Pattern

**Zustand** is used for client-side state with the following stores:

#### Auth Store
```typescript
interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}
```

#### UI Store
```typescript
interface UIState {
  theme: 'light' | 'dark' | 'system'
  sidebarOpen: boolean
  mobileMenuOpen: boolean
  notifications: Notification[]
}
```

### API Integration Pattern

**Service Layer** abstracts API interactions:

```typescript
// Example service pattern
class DocumentService {
  static async upload(file: File): Promise<Document> {
    // File validation and upload logic
  }
  
  static async list(): Promise<Document[]> {
    // Document retrieval with caching
  }
}
```

### Authentication Flow

1. **Login**: User credentials → JWT tokens → User state
2. **Token Storage**: Access + refresh tokens in localStorage
3. **Auto Refresh**: Background token refresh before expiry
4. **Protected Routes**: Authentication guards for sensitive pages
5. **Logout**: Token cleanup and state reset

## 🔐 Security Implementation

### JWT Token Management

- **Access Token**: 15-minute expiry for security
- **Refresh Token**: 7-day expiry for convenience
- **Automatic Refresh**: Background refresh 5 minutes before expiry
- **Secure Storage**: localStorage with HTTP-only consideration

### Request Interceptors

```typescript
// Request interceptor - Add auth headers
api.interceptors.request.use(config => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor - Handle token refresh
api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      await refreshAccessToken()
      return retryOriginalRequest(error.config)
    }
    return Promise.reject(error)
  }
)
```

### Data Validation

- **Input Validation**: Client-side form validation
- **Type Safety**: TypeScript for all data structures
- **API Response Validation**: Type checking for API responses
- **File Upload Validation**: Size and type restrictions

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Mobile Features
- **Collapsible Sidebar**: Space-efficient navigation
- **Touch-friendly**: Optimized tap targets
- **Responsive Grid**: Adaptive content layout
- **Mobile Menu**: Hamburger navigation

### Theme System
- **Light Theme**: Clean, bright interface
- **Dark Theme**: Easy-on-the-eyes dark mode
- **System Theme**: Respects OS preference
- **Theme Persistence**: Remembers user choice

## 🚀 Deployment

### Production Build

```bash
# Build optimized production bundle
npm run build

# Output in dist/ directory
# - index.html (460 B gzipped)
# - assets/index-*.js (362 kB gzipped)
# - assets/index-*.css (21 kB gzipped)
```

### Environment Variables

```bash
# Production
VITE_API_URL=https://your-api-domain.com
VITE_APP_NAME=RAG Knowledge Assistant
VITE_APP_VERSION=1.0.0

# Development
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=RAG Assistant (Dev)
```

### Deployment Options

#### Static Hosting (Vercel, Netlify)
```bash
# Deploy static build
npm run build
# Upload dist/ folder to hosting provider
```

#### Docker Deployment
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY dist ./dist
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## 🧪 Testing Strategy

### Unit Testing
- **React Testing Library**: Component testing
- **Jest**: Test runner and mocking
- **TypeScript**: Type checking in tests

### Integration Testing
- **Cypress**: End-to-end testing
- **MSW**: API mocking for tests
- **Storybook**: Component documentation and testing

### Manual Testing Checklist

- [ ] Authentication flow (register → login → logout)
- [ ] Document upload and management
- [ ] Chat functionality with RAG responses
- [ ] Workspace operations
- [ ] Responsive design on all devices
- [ ] Error handling and edge cases
- [ ] Performance benchmarks

## 🔧 Configuration

### Vite Configuration
- **React Plugin**: Optimized React support
- **Path Aliases**: Clean import statements
- **Development Proxy**: Backend API proxy
- **Build Optimization**: Code splitting and minification

### TypeScript Configuration
- **Strict Mode**: Maximum type safety
- **Path Mapping**: Import resolution
- **JSX Support**: React JSX transformation
- **Target**: Modern browser support

### Tailwind Configuration
- **Custom Theme**: Brand colors and design tokens
- **Animations**: Smooth transitions and micro-interactions
- **Responsive Utilities**: Mobile-first design approach
- **Component Variants**: Consistent styling patterns

## 🐛 Troubleshooting

### Common Issues

#### Build Errors
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check TypeScript configuration
npx tsc --noEmit
```

#### Development Issues
```bash
# Check backend connectivity
curl http://localhost:8000/api/v1/health

# Clear browser storage
localStorage.clear()
```

#### Performance Issues
- **Bundle Size**: Use `npm run build` to analyze
- **Network**: Check browser DevTools Network tab
- **Memory**: Use React DevTools Profiler

### Debug Mode

```bash
# Enable verbose logging
VITE_LOG_LEVEL=debug npm run dev

# Source maps in development
# Chrome DevTools → Sources → .map files
```

## 📚 API Integration

### Backend Endpoints

```typescript
// Authentication
POST /api/v1/auth/register    # User registration
POST /api/v1/auth/login       # User login
POST /api/v1/auth/refresh     # Token refresh
GET  /api/v1/auth/me          # User info

// Documents
POST /api/v1/documents/upload  # File upload
GET  /api/v1/documents/        # List documents
GET  /api/v1/documents/{id}    # Get document
DELETE /api/v1/documents/{id}  # Delete document

// Chat
POST /api/v1/chat/query       # RAG query
GET  /api/v1/chat/history      # Chat history
GET  /api/v1/chat/stats        # Chat statistics

// Workspaces
GET  /api/v1/workspaces/       # List workspaces
POST /api/v1/workspaces/       # Create workspace
GET  /api/v1/workspaces/{id}  # Get workspace
PUT  /api/v1/workspaces/{id}  # Update workspace
DELETE /api/v1/workspaces/{id}  # Delete workspace
```

### Request Patterns

```typescript
// Authenticated requests
const response = await api.get('/api/v1/documents/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
})

// File uploads
const formData = new FormData()
formData.append('file', file)
formData.append('title', title)
const response = await api.post('/api/v1/documents/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Install dependencies: `npm install`
4. Make changes following code style
5. Run tests: `npm test`
6. Submit pull request

### Code Style
- **TypeScript**: Strict typing throughout
- **ESLint**: Follow configured rules
- **Components**: Functional components with hooks
- **Imports**: Use path aliases (@/prefix)
- **Naming**: PascalCase for components, camelCase for functions

### Git Workflow
```bash
# Feature branch
git checkout -b feature/new-feature

# Commit changes
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/new-feature
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **React Team**: For the amazing React framework
- **Vite Team**: For the lightning-fast build tool
- **Tailwind CSS**: For the utility-first CSS framework
- **Zustand Team**: For the minimalist state management
- **Lucide**: For the beautiful icon set

---

**Built with ❤️ for the RAG Knowledge Assistant project**
