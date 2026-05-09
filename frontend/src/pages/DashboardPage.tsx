import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { chatService } from '@/services/chatService'
import { documentService } from '@/services/documentService'
import { workspaceService } from '@/services/workspaceService'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { formatRelativeTime } from '@/utils/helpers'
import { FileText, MessageSquare, Users, Plus } from 'lucide-react'

const DashboardPage: React.FC = () => {
  const { user } = useAuthStore()

  // Fetch workspace stats
  const { data: workspaceStats, isLoading: statsLoading } = useQuery({
    queryKey: ['workspace-stats', user?.workspace_id],
    queryFn: () => workspaceService.getStats(user?.workspace_id || 1),
    enabled: !!user?.workspace_id,
  })

  // Fetch recent documents
  const { data: documents, isLoading: docsLoading } = useQuery({
    queryKey: ['recent-documents', user?.workspace_id],
    queryFn: () => documentService.list({ limit: 5 }),
    enabled: !!user?.workspace_id,
  })

  // Fetch recent chat history
  const { data: chatHistory, isLoading: chatLoading } = useQuery({
    queryKey: ['recent-chat', user?.workspace_id],
    queryFn: () => chatService.getHistory({ limit: 5 }),
    enabled: !!user?.workspace_id,
  })

  const quickActions = [
    {
      title: 'New Chat',
      description: 'Start a conversation with your knowledge base',
      icon: MessageSquare,
      href: '/chat',
      color: 'bg-blue-500',
    },
    {
      title: 'Upload Document',
      description: 'Add new documents to your knowledge base',
      icon: FileText,
      href: '/documents',
      color: 'bg-green-500',
    },
    {
      title: 'Manage Workspace',
      description: 'Configure workspace settings and users',
      icon: Users,
      href: '/workspaces',
      color: 'bg-purple-500',
    },
  ]

  if (statsLoading || docsLoading || chatLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.email?.split('@')[0]}!
          </h1>
          <p className="text-gray-600 mt-2">
            Here's what's happening in your workspace today.
          </p>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {quickActions.map((action) => {
              const Icon = action.icon
              return (
                <Link key={action.title} to={action.href}>
                  <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                    <CardContent className="p-6">
                      <div className="flex items-center space-x-4">
                        <div className={`${action.color} p-3 rounded-lg`}>
                          <Icon className="h-6 w-6 text-white" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900">{action.title}</h3>
                          <p className="text-sm text-gray-600">{action.description}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              )
            })}
          </div>
        </div>

        {/* Stats Overview */}
        {workspaceStats && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Workspace Overview</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <FileText className="h-8 w-8 text-blue-600" />
                    <div className="ml-4">
                      <p className="text-2xl font-bold text-gray-900">
                        {workspaceStats.document_count}
                      </p>
                      <p className="text-sm text-gray-600">Documents</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <MessageSquare className="h-8 w-8 text-green-600" />
                    <div className="ml-4">
                      <p className="text-2xl font-bold text-gray-900">
                        {workspaceStats.chat_count}
                      </p>
                      <p className="text-sm text-gray-600">Chats</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <Users className="h-8 w-8 text-purple-600" />
                    <div className="ml-4">
                      <p className="text-2xl font-bold text-gray-900">
                        {workspaceStats.user_count}
                      </p>
                      <p className="text-sm text-gray-600">Users</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <Plus className="h-8 w-8 text-orange-600" />
                    <div className="ml-4">
                      <p className="text-2xl font-bold text-gray-900">
                        {workspaceStats.name}
                      </p>
                      <p className="text-sm text-gray-600">Workspace</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Documents */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Documents</CardTitle>
              <CardDescription>
                Latest documents uploaded to your workspace
              </CardDescription>
            </CardHeader>
            <CardContent>
              {documents && documents.length > 0 ? (
                <div className="space-y-4">
                  {documents.slice(0, 5).map((doc: any) => (
                    <div key={doc.id} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <FileText className="h-5 w-5 text-gray-400" />
                        <div>
                          <p className="font-medium text-gray-900">{doc.title}</p>
                          <p className="text-sm text-gray-500">
                            {formatRelativeTime(doc.created_at)}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-500">
                          {documentService.getFileTypeLabel(doc.filename)}
                        </p>
                      </div>
                    </div>
                  ))}
                  <Link to="/documents">
                    <Button variant="outline" className="w-full mt-4">
                      View All Documents
                    </Button>
                  </Link>
                </div>
              ) : (
                <div className="text-center py-8">
                  <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 mb-4">No documents yet</p>
                  <Link to="/documents">
                    <Button>Upload First Document</Button>
                  </Link>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recent Chats */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Chats</CardTitle>
              <CardDescription>
                Your latest conversations with the AI assistant
              </CardDescription>
            </CardHeader>
            <CardContent>
              {chatHistory && chatHistory.length > 0 ? (
                <div className="space-y-4">
                  {chatHistory.slice(0, 5).map((chat: any) => (
                    <div key={chat.id} className="border-b pb-4 last:border-b-0">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <p className="font-medium text-gray-900 line-clamp-2">
                            {chat.query}
                          </p>
                          <p className="text-sm text-gray-500 mt-1">
                            {formatRelativeTime(chat.created_at)}
                          </p>
                        </div>
                        <MessageSquare className="h-4 w-4 text-gray-400 ml-2" />
                      </div>
                    </div>
                  ))}
                  <Link to="/chat">
                    <Button variant="outline" className="w-full mt-4">
                      View All Chats
                    </Button>
                  </Link>
                </div>
              ) : (
                <div className="text-center py-8">
                  <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 mb-4">No chats yet</p>
                  <Link to="/chat">
                    <Button>Start First Chat</Button>
                  </Link>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
