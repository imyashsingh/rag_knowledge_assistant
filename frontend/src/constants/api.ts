// API Configuration
export const API_BASE_URL = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000'
export const API_VERSION = 'v1'

// API Endpoints
export const API_ENDPOINTS = {
  // Auth
  AUTH: {
    LOGIN: `/api/${API_VERSION}/auth/login`,
    REGISTER: `/api/${API_VERSION}/auth/register`,
    REFRESH: `/api/${API_VERSION}/auth/refresh`,
    ME: `/api/${API_VERSION}/auth/me`,
  },
  
  // Chat
  CHAT: {
    QUERY: `/api/${API_VERSION}/chat/query`,
    HISTORY: `/api/${API_VERSION}/chat/history`,
    STATS: `/api/${API_VERSION}/chat/stats`,
    CLEAR_CACHE: `/api/${API_VERSION}/chat/clear-cache`,
    LEGACY: `/api/${API_VERSION}/chat/legacy`,
  },
  
  // Documents
  DOCUMENTS: {
    UPLOAD: `/api/${API_VERSION}/documents/upload`,
    LIST: `/api/${API_VERSION}/documents/`,
    DETAIL: (id: number) => `/api/${API_VERSION}/documents/${id}`,
    DELETE: (id: number) => `/api/${API_VERSION}/documents/${id}`,
  },
  
  // Workspaces
  WORKSPACES: {
    LIST: `/api/${API_VERSION}/workspaces/`,
    CREATE: `/api/${API_VERSION}/workspaces/`,
    DETAIL: (id: number) => `/api/${API_VERSION}/workspaces/${id}`,
    UPDATE: (id: number) => `/api/${API_VERSION}/workspaces/${id}`,
    DELETE: (id: number) => `/api/${API_VERSION}/workspaces/${id}`,
    STATS: (id: number) => `/api/${API_VERSION}/workspaces/${id}/stats`,
  },
  
  // Health
  HEALTH: `/api/${API_VERSION}/health`,
  ROOT: '/',
} as const

// Storage Keys
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'rag_access_token',
  REFRESH_TOKEN: 'rag_refresh_token',
  USER: 'rag_user',
  WORKSPACE: 'rag_workspace',
  THEME: 'rag_theme',
  CHAT_SESSION: 'rag_chat_session',
} as const

// File Upload Constants
export const UPLOAD_CONSTANTS = {
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  SUPPORTED_EXTENSIONS: ['.txt', '.pdf', '.docx', '.md', '.markdown'],
  CHUNK_SIZE: 1024 * 1024, // 1MB chunks
} as const

// JWT Constants
export const JWT_CONSTANTS = {
  ACCESS_TOKEN_EXPIRY: 15 * 60 * 1000, // 15 minutes in ms
  REFRESH_TOKEN_EXPIRY: 7 * 24 * 60 * 60 * 1000, // 7 days in ms
  REFRESH_THRESHOLD: 5 * 60 * 1000, // 5 minutes before expiry
} as const

// UI Constants
export const UI_CONSTANTS = {
  DEBOUNCE_DELAY: 300,
  TOAST_DURATION: 3000,
  SIDEBAR_WIDTH: 280,
  MOBILE_BREAKPOINT: 768,
} as const

// Query Keys for React Query
export const QUERY_KEYS = {
  USER: ['user'],
  WORKSPACES: ['workspaces'],
  WORKSPACE: (id: number) => ['workspaces', id],
  DOCUMENTS: (workspaceId: number) => ['documents', workspaceId],
  DOCUMENT: (id: number) => ['documents', id],
  CHAT_HISTORY: (workspaceId: number) => ['chat', 'history', workspaceId],
  CHAT_STATS: (workspaceId: number) => ['chat', 'stats', workspaceId],
} as const
