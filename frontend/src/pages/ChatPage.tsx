import { useState, useEffect, useRef, useCallback } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useAuthStore } from '@/stores/authStore'
import { chatService } from '@/services/chatService'
import { documentService } from '@/services/documentService'
import { ChatRequest, ConversationHistoryMessage, SourceDocument } from '@/types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Loader2, Plus, Send, AlertTriangle, MessageSquare, Trash2, Edit3 } from 'lucide-react'
import { formatRelativeTime } from '@/utils/helpers'

// ─── Types ────────────────────────────────────────────────────────────────────

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
  timestamp: Date
}

// Use SourceDocument from types instead of custom interface
type Source = SourceDocument

// ─── Helper Functions ────────────────────────────────────────────────────────────

const generateSessionDisplayName = (session: any): string => {
  if (session.name) {
    return session.name
  }
  
  // Generate a better default name using session ID
  const sessionId = session.session_id.replace('session-', '')
  const shortId = sessionId.slice(0, 8).toUpperCase()
  
  // Use message count to create a more descriptive name
  const messageCount = session.message_count || 0
  if (messageCount === 0) {
    return `New Chat ${shortId}`
  } else if (messageCount === 1) {
    return `Chat ${shortId} (1 message)`
  } else {
    return `Chat ${shortId} (${messageCount} messages)`
  }
}

// ─── Constants ─────────────────────────────────────────────────────────────────

const SESSION_STORAGE_KEY = 'currentChatSession'
const MAX_CONTEXT_MESSAGES = 10
const MAX_SOURCES_VISIBLE = 2
const MAX_SOURCES = 5

const SUGGESTED_PROMPTS = [
  { emoji: '📄', label: 'What documents do I have?' },
  { emoji: '�', label: 'Summarize my recent documents' },
  { emoji: '💡', label: 'What are the key insights from my data?' },
] as const

// ─── Sub-components ────────────────────────────────────────────────────────────

interface SessionItemProps {
  label: string
  sublabel: string
  avatarContent: string
  avatarClass: string
  isActive: boolean
  dateLabel?: string
  sessionId: string
  onClick: () => void
  onDelete?: (sessionId: string) => void
  onRename?: (sessionId: string, currentName: string) => void
}

const SessionItem = ({
  label,
  sublabel,
  avatarContent,
  avatarClass,
  isActive,
  dateLabel,
  sessionId,
  onClick,
  onDelete,
  onRename,
}: SessionItemProps) => (
  <div className={`w-full text-left px-3 py-2 my-1 rounded-lg transition-colors duration-150 group ${
    isActive ? 'bg-gray-100 text-gray-900' : 'hover:bg-gray-50 text-gray-700'
  }`}>
    <div className="flex items-center justify-between">
      <button
        type="button"
        onClick={onClick}
        className="flex items-center gap-3 min-w-0 flex-1"
      >
        <div
          className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${avatarClass}`}
        >
          <span className="text-xs font-medium">{avatarContent}</span>
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium truncate">{label}</p>
          <p className="text-xs text-gray-500 truncate">{sublabel}</p>
        </div>
      </button>
      
      <div className="flex items-center gap-1 ml-2">
        {dateLabel && <span className="text-xs text-gray-400 flex-shrink-0">{dateLabel}</span>}
        <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-150 flex gap-1">
          {onRename && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation()
                onRename(sessionId, label)
              }}
              className="p-1 rounded hover:bg-gray-200 text-gray-500 hover:text-gray-700 transition-colors"
              title="Rename session"
            >
              <Edit3 className="h-3 w-3" />
            </button>
          )}
          {onDelete && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation()
                onDelete(sessionId)
              }}
              className="p-1 rounded hover:bg-red-100 text-gray-500 hover:text-red-600 transition-colors"
              title="Delete session"
            >
              <Trash2 className="h-3 w-3" />
            </button>
          )}
        </div>
      </div>
    </div>
  </div>
)

interface MessageBubbleProps {
  message: Message
  onToggleSources?: (messageId: string) => void
  expandedSources?: Set<string>
}

const MessageBubble = ({ message, onToggleSources, expandedSources }: MessageBubbleProps) => {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`flex items-end gap-2 max-w-[75%] ${isUser ? 'flex-row-reverse' : ''}`}
      >
        {/* Avatar */}
        <div
          className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${
            isUser
              ? 'bg-blue-600'
              : 'bg-gradient-to-br from-blue-500 to-purple-600'
          }`}
        >
          <span className="text-xs font-medium text-white">{isUser ? 'U' : 'AI'}</span>
        </div>

        {/* Bubble */}
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? 'bg-blue-600 text-white'
              : 'bg-white border border-gray-200 text-gray-900 shadow-sm'
          }`}
        >
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>

          {/* Sources */}
          {!isUser && message.sources && message.sources.length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-100">
              <p className="text-xs font-semibold text-gray-600 mb-2">📚 Sources</p>
              <div className="space-y-2">
                {message.sources.slice(0, MAX_SOURCES_VISIBLE).map((source, index) => (
                  <div key={index} className="p-2 bg-gray-50 rounded-lg text-xs">
                    <p className="font-medium text-gray-900">{source.document_title}</p>
                    <p className="text-gray-600 mt-1 line-clamp-2">{source.chunk_text}</p>
                    {source.relevance_score != null && (
                      <p className="text-gray-500 mt-1">
                        Relevance: {(source.relevance_score * 100).toFixed(1)}%
                      </p>
                    )}
                  </div>
                ))}
                {message.sources.length > MAX_SOURCES_VISIBLE && (
                  <button
                    onClick={() => onToggleSources?.(message.id)}
                    className="text-xs text-blue-600 hover:text-blue-800 cursor-pointer transition-colors"
                  >
                    {expandedSources?.has(message.id) 
                      ? 'Show less' 
                      : `+${message.sources.length - MAX_SOURCES_VISIBLE} more sources`
                    }
                  </button>
                )}
                {expandedSources?.has(message.id) && message.sources.length > MAX_SOURCES_VISIBLE && (
                  <div className="space-y-2 mt-2">
                    {message.sources.slice(MAX_SOURCES_VISIBLE).map((source, index) => (
                      <div key={index} className="p-2 bg-gray-50 rounded-lg text-xs">
                        <p className="font-medium text-gray-900">{source.document_title}</p>
                        <p className="text-gray-600 mt-1 line-clamp-2">{source.chunk_text}</p>
                        {source.relevance_score != null && (
                          <p className="text-gray-500 mt-1">
                            Relevance: {(source.relevance_score * 100).toFixed(1)}%
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          <p className="text-xs mt-2 opacity-60">{formatRelativeTime(message.timestamp)}</p>
        </div>
      </div>
    </div>
  )
}

interface TypingIndicatorProps {}

const TypingIndicator = (_: TypingIndicatorProps) => (
  <div className="flex justify-start">
    <div className="flex items-end gap-2">
      <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0">
        <span className="text-xs font-medium text-white">AI</span>
      </div>
      <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3 shadow-sm">
        <div className="flex items-center gap-2">
          <Loader2 className="h-4 w-4 animate-spin text-gray-400" />
          <p className="text-sm text-gray-500">Thinking…</p>
        </div>
      </div>
    </div>
  </div>
)

// ─── Custom hook: session storage ──────────────────────────────────────────────

function usePersistentSession() {
  const [sessionId, setSessionIdState] = useState<string | null>(() => {
    try {
      return localStorage.getItem(SESSION_STORAGE_KEY)
    } catch {
      return null
    }
  })

  const setSessionId = useCallback((id: string | null) => {
    setSessionIdState(id)
    try {
      if (id) {
        localStorage.setItem(SESSION_STORAGE_KEY, id)
      } else {
        localStorage.removeItem(SESSION_STORAGE_KEY)
      }
    } catch {
      // localStorage unavailable — continue without persistence
    }
  }, [])

  return [sessionId, setSessionId] as const
}

// ─── Main component ────────────────────────────────────────────────────────────

const ChatPage: React.FC = () => {
  const { user } = useAuthStore()
  const queryClient = useQueryClient()

  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [currentSessionId, setCurrentSessionId] = usePersistentSession()
  const [showNewSessionDialog, setShowNewSessionDialog] = useState(false)
  const [newSessionName, setNewSessionName] = useState('')
  const [expandedSources, setExpandedSources] = useState<Set<string>>(new Set())
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [showRenameDialog, setShowRenameDialog] = useState(false)
  const [sessionToDelete, setSessionToDelete] = useState<string | null>(null)
  const [sessionToRename, setSessionToRename] = useState<{ id: string; name: string } | null>(null)
  const [renameSessionName, setRenameSessionName] = useState('')

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // ── Scroll to bottom on new messages ──
  useEffect(() => {
    // Use a timeout to ensure the DOM has updated before scrolling
    const timeoutId = setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, 100)
    
    return () => clearTimeout(timeoutId)
  }, [messages])

  // ── Queries ──
  const { data: sessions } = useQuery({
    queryKey: ['chat-sessions', user?.workspace_id],
    queryFn: () => chatService.getSessions(),
    enabled: !!user?.workspace_id,
  })

  const { data: documents, isLoading: documentsLoading } = useQuery({
    queryKey: ['documents', user?.workspace_id],
    queryFn: () => documentService.list(),
    enabled: !!user?.workspace_id,
  })

  const { data: chatHistory, isLoading: historyLoading } = useQuery({
    queryKey: ['chat-history', user?.workspace_id, currentSessionId],
    queryFn: () => chatService.getHistory(),
    enabled: !!user?.workspace_id,
  })

  // ── Invalidate history when session changes ──
  useEffect(() => {
    if (user?.workspace_id) {
      queryClient.invalidateQueries({
        queryKey: ['chat-history', user.workspace_id, currentSessionId],
      })
    }
  }, [currentSessionId, user?.workspace_id, queryClient])

  // ── Sync messages from server history ──
  useEffect(() => {
    if (!chatHistory) return

    const filtered = chatHistory.filter((chat) => {
      // If we have a current session, only show messages for that session
      if (currentSessionId) {
        return chat.session_id === currentSessionId
      }
      // If no current session, don't show any messages (no default session)
      return false
    })

    const allMessages = filtered.flatMap((chat) => [
      {
        id: `${chat.id}-query`,
        role: 'user' as const,
        content: chat.query,
        timestamp: new Date(chat.created_at),
      },
      {
        id: `${chat.id}-answer`,
        role: 'assistant' as const,
        content: chat.answer,
        sources: chat.sources,
        timestamp: new Date(chat.created_at),
      },
    ])

    // Sort messages by timestamp to ensure chronological order
    const sortedMessages = allMessages.sort((a, b) => 
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    )

    setMessages(sortedMessages)
  }, [chatHistory, currentSessionId])

  // ── Chat mutation ──
  const chatMutation = useMutation({
    mutationFn: (request: ChatRequest) => {
      const history: ConversationHistoryMessage[] = messages
        .slice(-MAX_CONTEXT_MESSAGES)
        .map(({ role, content }) => ({ role, content }))

      return chatService.queryWithHistory(
        { ...request, session_id: currentSessionId ?? undefined },
        history
      )
    },
    onSuccess: (response) => {
      const now = new Date()
      setMessages((prev) => [
        ...prev,
        {
          id: `user-${response.query}-${now.getTime()}`,
          role: 'user',
          content: response.query,
          timestamp: now,
        },
        {
          id: `assistant-${now.getTime()}`,
          role: 'assistant',
          content: response.answer,
          sources: response.sources,
          timestamp: now,
        },
      ])
      setQuery('')
      queryClient.invalidateQueries({ queryKey: ['chat-history'] })
      queryClient.invalidateQueries({ queryKey: ['chat-sessions'] })
    },
    onError: (error) => {
      console.error('Chat query failed:', error)
      // You could add toast notifications or other error handling here
    },
  })

  // ── Delete session mutation ──
  const deleteSessionMutation = useMutation({
    mutationFn: (sessionId: string) => chatService.deleteSession(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chat-sessions'] })
      queryClient.invalidateQueries({ queryKey: ['chat-history'] })
      
      // If current session was deleted, switch to another session or null
      if (sessionToDelete === currentSessionId) {
        setCurrentSessionId(null)
        setMessages([])
      }
      
      setShowDeleteDialog(false)
      setSessionToDelete(null)
    },
    onError: (error) => {
      console.error('Failed to delete session:', error)
      // You could add toast notifications here
    },
  })

  // ── Update session name mutation ──
  const updateSessionNameMutation = useMutation({
    mutationFn: ({ sessionId, name }: { sessionId: string; name: string }) => 
      chatService.updateSessionName(sessionId, name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chat-sessions'] })
      setShowRenameDialog(false)
      setSessionToRename(null)
      setRenameSessionName('')
    },
    onError: (error) => {
      console.error('Failed to update session name:', error)
      // You could add toast notifications here
    },
  })

  // ── Handlers ──
  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault()
      const trimmed = query.trim()
      if (!trimmed || chatMutation.isPending) return
      chatMutation.mutate({ query: trimmed, max_sources: MAX_SOURCES })
      
      // Focus back to input after submission
      setTimeout(() => {
        inputRef.current?.focus()
      }, 100)
    },
    [query, chatMutation]
  )

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        handleSubmit(e as unknown as React.FormEvent)
      }
    },
    [handleSubmit]
  )

  const handleSuggestedPrompt = useCallback((label: string) => {
    setQuery(label)
    inputRef.current?.focus()
  }, [])

  const toggleSources = useCallback((messageId: string) => {
    setExpandedSources(prev => {
      const newSet = new Set(prev)
      if (newSet.has(messageId)) {
        newSet.delete(messageId)
      } else {
        newSet.add(messageId)
      }
      return newSet
    })
  }, [])

  const handleDeleteSession = useCallback((sessionId: string) => {
    setSessionToDelete(sessionId)
    setShowDeleteDialog(true)
  }, [])

  const handleRenameSession = useCallback((sessionId: string, currentName: string) => {
    setSessionToRename({ id: sessionId, name: currentName })
    setRenameSessionName(currentName)
    setShowRenameDialog(true)
  }, [])

  const handleSwitchSession = useCallback(
    (id: string) => {
      setCurrentSessionId(id || null)
      setMessages([]) // Clear messages immediately
      
      // Invalidate queries to force refetch for the new session
      queryClient.invalidateQueries({ queryKey: ['chat-history'] })
      
      // Also invalidate sessions to get updated session list
      queryClient.invalidateQueries({ queryKey: ['chat-sessions'] })
    },
    [setCurrentSessionId, queryClient]
  )

  const handleCreateSession = useCallback(async () => {
    try {
      // Generate a unique session ID
      const sessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      
      // Create session with name via API
      await chatService.createSession(sessionId, newSessionName || undefined)
      
      // Set new session immediately
      setCurrentSessionId(sessionId)
      setMessages([])
      setShowNewSessionDialog(false)
      setNewSessionName('')
      
      // Invalidate queries to refresh the session list
      queryClient.invalidateQueries({ queryKey: ['chat-sessions'] })
      queryClient.invalidateQueries({ queryKey: ['chat-history'] })
    } catch (err) {
      console.error('Failed to create session:', err)
    }
  }, [newSessionName, queryClient, setCurrentSessionId])

  // ── Derived state ──
  const hasDocuments = Boolean(documents?.length)
  const isLoading = chatMutation.isPending

  const activeSessionName = currentSessionId
    ? generateSessionDisplayName(sessions?.find((s) => s.session_id === currentSessionId) || { session_id: currentSessionId, message_count: 0 })
    : null

  // ── Render ──
  return (
    <div className="h-full flex overflow-hidden">
      {/* ── Main Chat Area ── */}
      <div className="flex-1 flex flex-col min-w-0">

        {/* Header */}
        <header className="border-b border-gray-200 px-6 py-4 bg-white flex-shrink-0">
          <div className="max-w-5xl mx-auto px-4">
            <div className="flex items-center justify-center">
              <div className="flex items-center gap-3 text-center">
                {currentSessionId ? (
                  <>
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                      <span className="text-xs font-medium text-white">
                        {currentSessionId.replace('session-', '').charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <div>
                      <h1 className="text-lg font-semibold text-gray-900">{activeSessionName}</h1>
                      <p className="text-sm text-gray-500">
                        AI Assistant · {new Date().toLocaleDateString()}
                      </p>
                    </div>
                  </>
                ) : (
                  <div className="text-center">
                    <h1 className="text-lg font-semibold text-gray-900">Select a Chat Session</h1>
                    <p className="text-sm text-gray-500">
                      Choose a conversation from the right panel
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Documents Status */}
            <div className="mt-3">
              {!documentsLoading && !hasDocuments && (
                <div className="flex items-center gap-2 text-sm text-amber-700 bg-amber-50 px-3 py-2 rounded-lg">
                  <AlertTriangle className="h-4 w-4 flex-shrink-0" />
                  <div>
                    <p className="font-medium">No documents uploaded yet</p>
                    <p className="text-xs text-amber-600 mt-0.5">
                      Upload documents to enable AI-powered responses.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Messages */}
        <main className="flex-1 overflow-y-auto bg-gray-50">
          <div className="max-w-4xl mx-auto px-6 py-6">

            {historyLoading ? (
              <div className="flex flex-col items-center justify-center h-64 gap-3">
                <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
                <p className="text-sm text-gray-500">Loading conversation…</p>
              </div>
            ) : !currentSessionId ? (
              <div className="flex flex-col items-center justify-center min-h-[400px] text-center">
                <div className="mb-4 w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
                  <MessageSquare className="h-8 w-8 text-gray-400" />
                </div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  Select or create a chat session
                </h2>
                <p className="text-gray-500 max-w-md text-sm mb-6">
                  Choose an existing conversation from the sidebar or create a new one to start chatting.
                </p>
                <Button
                  onClick={() => setShowNewSessionDialog(true)}
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Create New Chat
                </Button>
              </div>
            ) : messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center min-h-[400px] text-center">
                <div className="mb-4 w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                  <span className="text-2xl">💬</span>
                </div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  How can I help you today?
                </h2>
                <p className="text-gray-500 max-w-md text-sm">
                  Ask me anything about your documents and I'll help you find the answers you need.
                </p>
                <div className="mt-6 flex flex-wrap gap-2 justify-center">
                  {SUGGESTED_PROMPTS.map(({ emoji, label }) => (
                    <Button
                      key={label}
                      variant="outline"
                      size="sm"
                      className="text-xs"
                      onClick={() => handleSuggestedPrompt(label)}
                    >
                      {emoji} {label}
                    </Button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((msg) => (
                  <MessageBubble 
                    key={msg.id} 
                    message={msg} 
                    onToggleSources={toggleSources}
                    expandedSources={expandedSources}
                  />
                ))}
              </div>
            )}

            {isLoading && <TypingIndicator />}

            {/* Scroll anchor */}
            <div ref={messagesEndRef} />
          </div>
        </main>

        {/* Input */}
        <footer className="border-t border-gray-200 bg-white px-6 py-4 flex-shrink-0">
          {currentSessionId ? (
            <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
              <div className="flex items-center gap-3 bg-gray-50 rounded-xl border border-gray-200 px-4 py-3 focus-within:border-blue-400 focus-within:ring-2 focus-within:ring-blue-100 transition-all duration-150">
                <Input
                  ref={inputRef}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type your message…"
                  aria-label="Chat message"
                  className="flex-1 bg-transparent border-none shadow-none focus-visible:ring-0 text-base"
                  disabled={isLoading}
                />
                <Button
                  type="submit"
                  disabled={!query.trim() || isLoading}
                  aria-label="Send message"
                  className="bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-3 py-2 transition-colors duration-150 disabled:opacity-50"
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </div>
              <p className="mt-2 text-xs text-center text-gray-400">
                Press Enter to send · Shift+Enter for a new line
              </p>
            </form>
          ) : (
            <div className="max-w-3xl mx-auto text-center">
              <p className="text-gray-500 text-sm">
                Select a chat session to start messaging
              </p>
            </div>
          )}
        </footer>
      </div>

      {/* ── Right: Session Sidebar ── */}
      <aside className="w-64 h-full bg-white border-l border-gray-200 flex flex-col shadow-sm flex-shrink-0">
        <div className="p-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Sessions</h2>
          <Button
            variant="ghost"
            size="sm"
            aria-label="New chat session"
            onClick={() => setShowNewSessionDialog(true)}
            className="text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg p-2"
          >
            <Plus className="h-4 w-4" />
          </Button>
        </div>

        <nav className="flex-1 overflow-y-auto py-2">
          {/* Session list */}
          {sessions?.map((session) => {
            const displayName = generateSessionDisplayName(session)
            return (
              <SessionItem
                key={session.session_id}
                label={displayName}
                sublabel={session.name ? `${session.message_count} ${session.message_count === 1 ? 'message' : 'messages'}` : 'Click to rename'}
                avatarContent={displayName.charAt(0).toUpperCase()}
                avatarClass="bg-gradient-to-br from-blue-500 to-purple-600 text-white"
                isActive={currentSessionId === session.session_id}
                sessionId={session.session_id}
                dateLabel={new Date(session.last_message_at).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                })}
                onClick={() => handleSwitchSession(session.session_id)}
                onDelete={handleDeleteSession}
                onRename={handleRenameSession}
              />
            )
          })}

          {sessions?.length === 0 && (
            <div className="text-center text-gray-500 text-sm py-8 px-4">
              <div className="mb-3 w-12 h-12 mx-auto bg-gray-100 rounded-full flex items-center justify-center">
                <MessageSquare className="h-5 w-5 text-gray-400" />
              </div>
              <p className="font-medium mb-1">No conversations yet</p>
              <p className="text-xs text-gray-400 mb-3">Create your first chat session to get started</p>
              <Button
                size="sm"
                onClick={() => setShowNewSessionDialog(true)}
                className="text-xs"
              >
                <Plus className="h-3 w-3 mr-1" />
                Create Chat
              </Button>
            </div>
          )}
        </nav>
      </aside>

      {/* ── New session dialog ── */}
      {showNewSessionDialog && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="dialog-title"
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
        >
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4 shadow-xl">
            <h2 id="dialog-title" className="text-lg font-semibold text-gray-900 mb-4">
              Create New Chat Session
            </h2>
            <div className="space-y-4">
              <div>
                <label htmlFor="session-name" className="block text-sm font-medium text-gray-700 mb-1">
                  Session Name (optional)
                </label>
                <Input
                  id="session-name"
                  value={newSessionName}
                  onChange={(e) => setNewSessionName(e.target.value)}
                  placeholder="Enter a name for this chat session"
                  className="w-full"
                  maxLength={50}
                />
              </div>
              <div className="flex gap-3 justify-end">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowNewSessionDialog(false)
                    setNewSessionName('')
                  }}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleCreateSession}
                  disabled={chatMutation.isPending}
                >
                  Create Session
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Delete session dialog ── */}
      {showDeleteDialog && sessionToDelete && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="delete-dialog-title"
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
        >
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4 shadow-xl">
            <h2 id="delete-dialog-title" className="text-lg font-semibold text-gray-900 mb-4">
              Delete Chat Session
            </h2>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete this chat session? This action cannot be undone and all messages in this session will be permanently removed.
            </p>
            <div className="flex gap-3 justify-end">
              <Button
                variant="outline"
                onClick={() => {
                  setShowDeleteDialog(false)
                  setSessionToDelete(null)
                }}
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={() => deleteSessionMutation.mutate(sessionToDelete)}
                disabled={deleteSessionMutation.isPending}
              >
                {deleteSessionMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    Deleting...
                  </>
                ) : (
                  'Delete Session'
                )}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* ── Rename session dialog ── */}
      {showRenameDialog && sessionToRename && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="rename-dialog-title"
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
        >
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4 shadow-xl">
            <h2 id="rename-dialog-title" className="text-lg font-semibold text-gray-900 mb-4">
              Rename Chat Session
            </h2>
            <div className="space-y-4">
              <div>
                <label htmlFor="rename-session-name" className="block text-sm font-medium text-gray-700 mb-1">
                  Session Name
                </label>
                <Input
                  id="rename-session-name"
                  value={renameSessionName}
                  onChange={(e) => setRenameSessionName(e.target.value)}
                  placeholder="Enter a new name for this chat session"
                  className="w-full"
                  maxLength={50}
                  autoFocus
                />
              </div>
              <div className="flex gap-3 justify-end">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowRenameDialog(false)
                    setSessionToRename(null)
                    setRenameSessionName('')
                  }}
                >
                  Cancel
                </Button>
                <Button
                  onClick={() => updateSessionNameMutation.mutate({ 
                    sessionId: sessionToRename.id, 
                    name: renameSessionName.trim() 
                  })}
                  disabled={updateSessionNameMutation.isPending || !renameSessionName.trim()}
                >
                  {updateSessionNameMutation.isPending ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      Updating...
                    </>
                  ) : (
                    'Rename'
                  )}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ChatPage