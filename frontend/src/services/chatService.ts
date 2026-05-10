import { api } from '@/utils/api'
import { ChatRequest, ChatResponse, ChatMessage, ChatStats, ConversationHistoryMessage } from '@/types'
import { API_ENDPOINTS } from '@/constants/api'

export const chatService = {
  // Send chat query
  query: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>(
      API_ENDPOINTS.CHAT.QUERY,
      request
    )
    return response.data
  },

  // Send chat query with conversation history
  queryWithHistory: async (request: ChatRequest, conversationHistory: ConversationHistoryMessage[]): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>(
      API_ENDPOINTS.CHAT.QUERY,
      {
        ...request,
        conversation_history: conversationHistory
      }
    )
    return response.data
  },

  // Get chat history
  getHistory: async (params?: {
    limit?: number
    offset?: number
  }): Promise<ChatMessage[]> => {
    const response = await api.get<ChatMessage[]>(
      API_ENDPOINTS.CHAT.HISTORY,
      { params }
    )
    return response.data
  },

  // Get chat statistics
  getStats: async (): Promise<ChatStats> => {
    const response = await api.get<ChatStats>(API_ENDPOINTS.CHAT.STATS)
    return response.data
  },

  // Clear RAG cache
  clearCache: async (): Promise<{ message: string }> => {
    const response = await api.post<{ message: string }>(
      API_ENDPOINTS.CHAT.CLEAR_CACHE
    )
    return response.data
  },

  // Get chat sessions
  getSessions: async (): Promise<any[]> => {
    const response = await api.get('/api/v1/chat/sessions')
    return response.data as any[]
  },

  // Search chat history
  search: async (query: string, sessionId?: string): Promise<any[]> => {
    const params: any = { q: query }
    if (sessionId) {
      params.session_id = sessionId
    }
    const response = await api.get('/api/v1/chat/search', { params })
    return response.data as any[]
  },

  // Delete session
  deleteSession: async (sessionId: string): Promise<void> => {
    await api.delete(`/api/v1/chat/sessions/${sessionId}`)
  },

  // Update session name
  updateSessionName: async (sessionId: string, name: string): Promise<any> => {
    const response = await api.patch(`/api/v1/chat/sessions/${sessionId}`, { name })
    return response.data
  },

  // Create session
  createSession: async (sessionId: string, name?: string): Promise<any> => {
    const response = await api.post('/api/v1/chat/sessions', {
      session_id: sessionId,
      name: name
    })
    return response.data
  },

  // Legacy query endpoint (for backward compatibility)
  legacyQuery: async (query: string, workspace: string): Promise<any> => {
    const response = await api.post(
      API_ENDPOINTS.CHAT.LEGACY,
      {},
      {
        params: { q: query, ws: workspace }
      }
    )
    return response.data
  },
}
