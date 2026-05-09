import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useAuthStore } from '@/stores/authStore'
import { workspaceService } from '@/services/workspaceService'
import { api } from '@/utils/api'
import { Workspace, WorkspaceCreate, User } from '@/types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Building, Plus, Edit, Trash2, Users, FileText, MessageSquare, Check } from 'lucide-react'
import { formatRelativeTime } from '@/utils/helpers'

const WorkspacesPage: React.FC = () => {
  const { user } = useAuthStore()
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [editingWorkspace, setEditingWorkspace] = useState<Workspace | null>(null)
  const [switchingId, setSwitchingId] = useState<number | null>(null)
  const queryClient = useQueryClient()

  // Fetch workspaces
  const { data: workspaces, isLoading } = useQuery({
    queryKey: ['workspaces'],
    queryFn: () => workspaceService.list(),
    enabled: !!user,
  })

  // Fetch current workspace stats
  const { data: currentStats } = useQuery({
    queryKey: ['workspace-stats', user?.workspace_id],
    queryFn: () => workspaceService.getStats(user?.workspace_id || 1),
    enabled: !!user?.workspace_id,
  })

  // Create workspace mutation
  const createMutation = useMutation({
    mutationFn: async (data: WorkspaceCreate) => {
      const workspace = await workspaceService.create(data)
      // Auto-switch into the newly created workspace
      const { switchWorkspace } = useAuthStore.getState()
      await switchWorkspace(workspace.id)
      // Refresh user data from server
      const userRes = await api.get<User>('/api/v1/auth/me')
      useAuthStore.setState({ user: userRes.data })
      return workspace
    },
    onSuccess: () => {
      setShowCreateForm(false)
      queryClient.invalidateQueries(['workspaces'])
      queryClient.invalidateQueries(['workspace-stats'])
    },
  })

  // Update workspace mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: WorkspaceCreate }) =>
      workspaceService.update(id, data),
    onSuccess: () => {
      setEditingWorkspace(null)
      queryClient.invalidateQueries(['workspaces'])
    },
  })

  // Delete workspace mutation
  const deleteMutation = useMutation({
    mutationFn: workspaceService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['workspaces'])
    },
  })

  const handleCreate = (data: WorkspaceCreate) => {
    createMutation.mutate(data)
  }

  const handleEdit = (workspace: Workspace) => {
    setEditingWorkspace(workspace)
  }

  const handleUpdate = (data: WorkspaceCreate) => {
    if (editingWorkspace) {
      updateMutation.mutate({ id: editingWorkspace.id, data })
    }
  }

  const handleDelete = (workspace: Workspace) => {
    if (workspace.id === user?.workspace_id) {
      alert('Cannot delete your current workspace')
      return
    }
    if (confirm(`Are you sure you want to delete "${workspace.name}"?`)) {
      deleteMutation.mutate(workspace.id)
    }
  }

  const handleSwitchWorkspace = async (workspace: Workspace) => {
    if (workspace.id === user?.workspace_id) return
    if (!confirm(`Switch to workspace "${workspace.name}"?`)) return

    setSwitchingId(workspace.id)
    try {
      const { switchWorkspace } = useAuthStore.getState()
      const success = await switchWorkspace(workspace.id)

      if (success) {
        // Refresh user from server to get updated workspace_id
        const userRes = await api.get<User>('/api/v1/auth/me')
        useAuthStore.setState({ user: userRes.data })
        queryClient.invalidateQueries(['workspaces'])
        queryClient.invalidateQueries(['workspace-stats'])
      } else {
        alert('Failed to switch workspace. Please try again.')
      }
    } finally {
      setSwitchingId(null)
    }
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Please log in to view workspaces
          </h1>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Workspaces</h1>
            <p className="text-gray-600 mt-2">
              Manage your workspaces and collaboration spaces
            </p>
          </div>
          
          <Button onClick={() => setShowCreateForm(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Create Workspace
          </Button>
        </div>

        {/* Current Workspace Stats */}
        {currentStats && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Current Workspace: {currentStats.name}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <FileText className="h-8 w-8 text-blue-600" />
                    <div className="ml-4">
                      <p className="text-2xl font-bold text-gray-900">
                        {currentStats.document_count}
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
                        {currentStats.chat_count}
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
                        {currentStats.user_count}
                      </p>
                      <p className="text-sm text-gray-600">Users</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* Workspaces Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {isLoading ? (
            <div className="col-span-full flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : workspaces && workspaces.length > 0 ? (
            workspaces.map((workspace) => (
              <Card key={workspace.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-2">
                      <Building className="h-5 w-5 text-gray-400" />
                      <div>
                        <CardTitle className="text-lg">{workspace.name}</CardTitle>
                        <CardDescription>
                          Created {formatRelativeTime(workspace.created_at)}
                        </CardDescription>
                      </div>
                    </div>
                    
                    <div className="flex space-x-2">
                      {workspace.id !== user?.workspace_id && (
                        <Button
                          variant="outline"
                          size="icon"
                          onClick={() => handleEdit(workspace)}
                          disabled={updateMutation.isLoading}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                      )}
                      
                      <Button
                        variant={workspace.id === user?.workspace_id ? 'secondary' : 'default'}
                        size="sm"
                        onClick={() => handleSwitchWorkspace(workspace)}
                        disabled={workspace.id === user?.workspace_id || switchingId === workspace.id}
                      >
                        {switchingId === workspace.id ? (
                          <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-1" />
                        ) : workspace.id === user?.workspace_id ? (
                          <Check className="h-3 w-3 mr-1" />
                        ) : (
                          <Users className="h-3 w-3 mr-1" />
                        )}
                        {workspace.id === user?.workspace_id
                          ? 'Current'
                          : switchingId === workspace.id
                          ? 'Switching...'
                          : 'Switch'}
                      </Button>
                      
                      {workspace.id !== user?.workspace_id && (
                        <Button
                          variant="outline"
                          size="icon"
                          onClick={() => handleDelete(workspace)}
                          disabled={deleteMutation.isLoading}
                          className="text-destructive hover:text-destructive"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-sm text-gray-600">
                    {workspace.id === user?.workspace_id ? (
                      <span className="text-green-600 font-medium">Current workspace</span>
                    ) : (
                      <span>Switch to this workspace to manage its settings</span>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            <div className="col-span-full text-center py-12">
              <Building className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                No workspaces yet
              </h3>
              <p className="text-gray-600 mb-6">
                Create your first workspace to get started
              </p>
              <Button onClick={() => setShowCreateForm(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Create First Workspace
              </Button>
            </div>
          )}
        </div>

        {/* Create/Edit Workspace Modal */}
        {(showCreateForm || editingWorkspace) && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                {editingWorkspace ? 'Edit Workspace' : 'Create New Workspace'}
              </h3>
              
              <form
                onSubmit={(e) => {
                  e.preventDefault()
                  const formData = new FormData(e.currentTarget)
                  const data = {
                    name: formData.get('name') as string,
                  }
                  
                  if (editingWorkspace) {
                    handleUpdate(data)
                  } else {
                    handleCreate(data)
                  }
                }}
                className="space-y-4"
              >
                <div>
                  <label htmlFor="name" className="text-sm font-medium text-gray-700">
                    Workspace Name
                  </label>
                  <Input
                    id="name"
                    name="name"
                    defaultValue={editingWorkspace?.name || ''}
                    placeholder="My Workspace"
                    required
                    disabled={createMutation.isLoading || updateMutation.isLoading}
                  />
                  {/* Show API error (e.g. duplicate name) */}
                  {(createMutation.isError || updateMutation.isError) && (
                    <p className="mt-2 text-sm text-red-600">
                      {(() => {
                        const err: any = createMutation.error || updateMutation.error
                        const detail = err?.response?.data?.detail
                        if (typeof detail === 'string') return detail
                        if (detail?.message) return detail.message
                        if (detail?.error === 'WORKSPACE_EXISTS') return detail.message
                        if (detail?.error === 'WORKSPACE_NAME_CONFLICT') return detail.message
                        return 'Something went wrong. Please try again.'
                      })()}
                    </p>
                  )}
                </div>

                <div className="flex justify-end space-x-3">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setShowCreateForm(false)
                      setEditingWorkspace(null)
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    disabled={createMutation.isLoading || updateMutation.isLoading}
                  >
                    {createMutation.isLoading || updateMutation.isLoading
                      ? 'Saving...'
                      : editingWorkspace
                      ? 'Update Workspace'
                      : 'Create Workspace'
                    }
                  </Button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default WorkspacesPage
