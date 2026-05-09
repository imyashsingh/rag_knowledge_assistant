import { api } from '@/utils/api'
import { 
  Workspace, 
  WorkspaceCreate, 
  WorkspaceUpdate, 
  WorkspaceWithUsers, 
  WorkspaceStats 
} from '@/types'
import { API_ENDPOINTS } from '@/constants/api'

export const workspaceService = {
  // Create new workspace
  create: async (workspaceData: WorkspaceCreate): Promise<Workspace> => {
    const response = await api.post<Workspace>(
      API_ENDPOINTS.WORKSPACES.CREATE,
      workspaceData
    )
    return response.data
  },

  // List user workspaces
  list: async (): Promise<Workspace[]> => {
    const response = await api.get<Workspace[]>(
      API_ENDPOINTS.WORKSPACES.LIST
    )
    return response.data
  },

  // Get workspace details with users
  getById: async (id: number): Promise<WorkspaceWithUsers> => {
    const response = await api.get<WorkspaceWithUsers>(
      API_ENDPOINTS.WORKSPACES.DETAIL(id)
    )
    return response.data
  },

  // Update workspace
  update: async (id: number, workspaceData: WorkspaceUpdate): Promise<Workspace> => {
    const response = await api.put<Workspace>(
      API_ENDPOINTS.WORKSPACES.UPDATE(id),
      workspaceData
    )
    return response.data
  },

  // Delete workspace
  delete: async (id: number): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(
      API_ENDPOINTS.WORKSPACES.DELETE(id)
    )
    return response.data
  },

  // Get workspace statistics
  getStats: async (id: number): Promise<WorkspaceStats> => {
    const response = await api.get<WorkspaceStats>(
      API_ENDPOINTS.WORKSPACES.STATS(id)
    )
    return response.data
  },
}
