import { Link } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { AlertTriangle } from 'lucide-react'

interface WorkspaceRequiredRouteProps {
  children: React.ReactNode
}

const WorkspaceRequiredRoute: React.FC<WorkspaceRequiredRouteProps> = ({ children }) => {
  const { user } = useAuthStore()

  // Check if user is in default workspace (id 1 or name contains "Default")
  const isDefaultWorkspace = user?.workspace_id === 1

  if (isDefaultWorkspace) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6 text-center">
          <AlertTriangle className="h-12 w-12 text-amber-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Workspace Required
          </h2>
          <p className="text-gray-600 mb-4">
            You are currently in the default workspace. Please switch to a different workspace to access this feature.
          </p>
          <Link
            to="/workspaces"
            className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-primary/90"
          >
            Go to Workspaces
          </Link>
        </div>
      </div>
    )
  }

  return <>{children}</>
}

export default WorkspaceRequiredRoute
