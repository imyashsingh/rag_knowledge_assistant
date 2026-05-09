import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useAuthStore } from '@/stores/authStore'
import { chatService } from '@/services/chatService'
import { documentService } from '@/services/documentService'
import { ChatRequest, ConversationHistoryMessage } from '@/types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Send, Loader2, AlertTriangle } from 'lucide-react'
import { formatRelativeTime } from '@/utils/helpers'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: any[]
  timestamp: Date
}

const ChatPage: React.FC = () => {
  const { user } = useAuthStore()
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const queryClient = useQueryClient()

  // Fetch chat history
  const { data: chatHistory, isLoading: historyLoading } = useQuery({
    queryKey: ['chat-history', user?.workspace_id],
    queryFn: () => chatService.getHistory(),
    enabled: !!user?.workspace_id,
  })

  // Load existing chat history into messages state when data arrives
  useEffect(() => {
    if (chatHistory && chatHistory.length > 0) {
      const loadedMessages: Message[] = chatHistory.flatMap((chat) => [
        {
          id: `${chat.id}-query`,
          role: 'user' as const,
          content: chat.query,
          timestamp: new Date(chat.created_at)
        },
        {
          id: `${chat.id}-answer`,
          role: 'assistant' as const,
          content: chat.answer,
          sources: chat.sources,
          timestamp: new Date(chat.created_at)
        }
      ])
      setMessages(loadedMessages)
    }
  }, [chatHistory])

  // Fetch document count to warn if no documents uploaded
  const { data: documents } = useQuery({
    queryKey: ['documents', user?.workspace_id],
    queryFn: () => documentService.list(),
    enabled: !!user?.workspace_id,
  })

  const hasDocuments = documents && documents.length > 0

  // Chat mutation
  const chatMutation = useMutation({
    mutationFn: (request: ChatRequest) => {
      // Get last 5 messages for conversation context
      const last5Messages: ConversationHistoryMessage[] = messages.slice(-10).map(msg => ({
        role: msg.role,
        content: msg.content
      }))
      return chatService.queryWithHistory(request, last5Messages)
    },
    onSuccess: (response) => {
      // Add both user query and AI response to messages
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: response.query,
        timestamp: new Date()
      }
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, userMessage, assistantMessage])
      setQuery('')
      queryClient.invalidateQueries(['chat-history'])
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    chatMutation.mutate({
      query: query.trim(),
      max_sources: 5,
    })
  }

  return (
    <div className="h-[calc(100vh-4rem)] bg-gray-50 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="bg-white border-b px-4 py-3 flex-shrink-0">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-900">AI Assistant</h1>
          
          {/* No documents warning */}
          {!hasDocuments && (
            <div className="flex items-center gap-2 text-amber-600 text-sm">
              <AlertTriangle className="h-4 w-4" />
              <span>No documents - upload to enable AI responses</span>
            </div>
          )}
        </div>
      </div>

      {/* Chat Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6 min-h-0">
        <div className="max-w-4xl mx-auto space-y-4 pb-4">
          {historyLoading ? (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="h-6 w-6 animate-spin" />
            </div>
          ) : messages.length === 0 ? (
            <div className="flex items-center justify-center h-full min-h-[400px]">
              <div className="text-center">
                <div className="text-6xl mb-4">💬</div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Ask me anything about your documents
                </h3>
                <p className="text-gray-600">
                  I'll help you find answers using your knowledge base
                </p>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-4 ${
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-white border'
                  }`}
                >
                  {message.role === 'assistant' && (
                    <p className="text-xs text-gray-500 mb-2">AI Assistant</p>
                  )}
                  <p className="whitespace-pre-wrap">{message.content}</p>
                  
                  {/* Sources for assistant messages */}
                  {message.role === 'assistant' && message.sources && message.sources.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <p className="text-xs font-semibold text-gray-700 mb-2">Sources:</p>
                      <div className="space-y-2">
                        {message.sources.map((source, index) => (
                          <div
                            key={index}
                            className="p-2 bg-gray-50 rounded text-xs"
                          >
                            <p className="font-medium text-gray-900">
                              {source.document_title}
                            </p>
                            <p className="text-gray-600 mt-1 line-clamp-2">
                              {source.chunk_text}
                            </p>
                            {source.relevance_score && (
                              <p className="text-gray-500 mt-1">
                                Relevance: {(source.relevance_score * 100).toFixed(1)}%
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <p className="text-xs mt-2 opacity-70">
                    {formatRelativeTime(message.timestamp)}
                  </p>
                </div>
              </div>
            ))
          )}
          
          {/* Loading indicator */}
          {chatMutation.isLoading && (
            <div className="flex justify-start">
              <div className="bg-white border rounded-lg p-4">
                <div className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <p className="text-sm text-gray-600">Thinking...</p>
                </div>
              </div>
            </div>
          )}
          
          {/* Error indicator */}
          {chatMutation.isError && (
            <div className="flex justify-center">
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 max-w-md">
                <div className="flex items-center gap-2 text-red-800">
                  <AlertTriangle className="h-4 w-4" />
                  <p className="text-sm">
                    {(() => {
                      const err: any = chatMutation.error
                      const detail = err?.response?.data?.detail
                      if (typeof detail === 'string') return detail
                      if (detail?.message) return detail.message
                      return 'Failed to process your query. Please try again.'
                    })()}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Input Form - Fixed at bottom */}
      <div className="bg-white border-t px-4 py-4 flex-shrink-0">
        <div className="max-w-4xl mx-auto">
          {!hasDocuments && (
            <div className="mb-3 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
              <div className="flex items-start">
                <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5 mr-2" />
                <div className="text-sm text-yellow-800">
                  <p className="font-medium">No documents uploaded</p>
                  <p className="text-xs mt-1">Upload documents to enable AI-powered responses.</p>
                  <Link to="/documents" className="text-xs text-yellow-700 hover:underline mt-1 inline-block">
                    Go to Documents →
                  </Link>
                </div>
              </div>
            </div>
          )}
          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question about your documents..."
              disabled={chatMutation.isLoading}
              className="flex-1"
            />
            <Button
              type="submit"
              disabled={chatMutation.isLoading || !query.trim()}
            >
              {chatMutation.isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>
        </div>
      </div>
    </div>
  )
}

export default ChatPage
