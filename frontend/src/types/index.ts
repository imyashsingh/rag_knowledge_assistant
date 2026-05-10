// User Types
export interface User {
  id: number
  email: string
  workspace_id: number
  workspace_name?: string
  created_at: string
}

export interface UserCreate {
  name: string
  email: string
  password: string
  workspace_name?: string
}

export interface UserLogin {
  email: string
  password: string
}

// Auth Types
export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface RefreshTokenRequest {
  refresh_token: string
}

// Workspace Types
export interface Workspace {
  id: number
  name: string
  created_at: string
}

export interface WorkspaceCreate {
  name: string
}

export interface WorkspaceUpdate {
  name?: string
}

export interface WorkspaceWithUsers {
  id: number
  name: string
  created_at: string
  users: Array<{
    id: number
    email: string
    created_at: string
  }>
}

export interface WorkspaceStats {
  id: number
  name: string
  document_count: number
  user_count: number
  chat_count: number
  created_at: string
}

// Document Types
export interface Document {
  id: number
  title: string
  filename: string
  content_type: string
  workspace_id: number
  created_at: string
  updated_at?: string
}

export interface DocumentCreate {
  title: string
  filename: string
  content_type: string
}

// Chat Types
export interface SourceDocument {
  document_id: number
  document_title: string
  chunk_text: string
  relevance_score?: number
}

export interface ChatRequest {
  query: string
  max_sources?: number
  session_id?: string
  conversation_history?: ConversationHistoryMessage[]
}

export interface ChatResponse {
  answer: string
  sources: SourceDocument[]
  query: string
  confidence?: number
  is_grounded?: boolean
  external_knowledge_detected?: boolean
  quality_assured?: boolean
  generation_attempts?: number
  retrieval_method?: string
  context_count?: number
}

export interface ChatMessage {
  id: string
  query: string
  answer: string
  sources: SourceDocument[]
  created_at: string
  user_id: number
  workspace_id: number
}

export interface ConversationHistoryMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatStats {
  total_chats: number
  average_confidence: number
  grounding_rate: number
}

// API Response Types
export interface ApiResponse<T> {
  data: T
  message?: string
  error?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
  has_next: boolean
  has_prev: boolean
}

// UI State Types
export interface LoadingState {
  isLoading: boolean
  error?: string
}

export interface UploadProgress {
  loaded: number
  total: number
  percentage: number
}

// Form Types
export interface FormErrors {
  [key: string]: string | undefined
}

// Theme Types
export type Theme = 'light' | 'dark' | 'system'
