import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { User, TokenResponse } from '@/types'
import { STORAGE_KEYS } from '@/constants/api'
import { api } from '@/utils/api'

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

interface AuthActions {
  login: (email: string, password: string) => Promise<void>
  register: (userData: { name: string; email: string; password: string; workspace_name?: string }) => Promise<void>
  logout: () => void
  refreshAccessToken: () => Promise<void>
  initializeAuth: () => void
  clearError: () => void
  setLoading: (loading: boolean) => void
  switchWorkspace: (workspaceId: number) => Promise<boolean>
}

export const useAuthStore = create<AuthState & AuthActions>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null })
        
        try {
          const response = await api.post<TokenResponse>('/api/v1/auth/login', {
            email,
            password,
          })

          const { access_token, refresh_token } = response.data

          // Store tokens in localStorage immediately for axios interceptors
          localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, access_token)
          localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, refresh_token)

          // Get user info (now the token is available for the interceptor)
          const userResponse = await api.get<User>('/api/v1/auth/me')
          const user = userResponse.data

          set({
            user,
            accessToken: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          })
        } catch (error: any) {
          let errorMessage = 'Login failed'
          
          // Handle structured error responses from backend
          if (error.response?.data?.detail) {
            const errorDetail = error.response.data.detail
            
            if (typeof errorDetail === 'string') {
              errorMessage = errorDetail
            } else if (errorDetail?.error) {
              switch (errorDetail.error) {
                case 'USER_NOT_FOUND':
                  errorMessage = errorDetail.message || 'No account found with this email'
                  break
                case 'INVALID_CREDENTIALS':
                  errorMessage = errorDetail.message || 'Incorrect email or password'
                  break
                case 'INVALID_EMAIL':
                  errorMessage = errorDetail.message || 'Invalid email format'
                  break
                case 'LOGIN_FAILED':
                  errorMessage = errorDetail.message || 'Login failed. Please try again.'
                  break
                default:
                  errorMessage = errorDetail.message || 'Login failed'
              }
            }
          } else if (error.response?.data?.message) {
            errorMessage = error.response.data.message
          } else if (error.message) {
            errorMessage = error.message
          }
          
          set({
            isLoading: false,
            error: errorMessage,
            isAuthenticated: false,
            user: null,
            accessToken: null,
            refreshToken: null,
          })
          throw error
        }
      },

      register: async (userData) => {
        set({ isLoading: true, error: null })
        
        try {
          const response = await api.post<TokenResponse>('/api/v1/auth/register', userData)
          const { access_token, refresh_token } = response.data

          // Store tokens in localStorage FIRST
          localStorage.setItem('rag_access_token', access_token)
          localStorage.setItem('rag_refresh_token', refresh_token)

          // Get user info AFTER tokens are stored
          const userResponse = await api.get<User>('/api/v1/auth/me')
          const user = userResponse.data

          set({
            user,
            accessToken: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          })

        } catch (error: any) {
          let errorMessage = 'Registration failed'
          
          // Handle structured error responses from backend
          if (error.response?.data?.detail) {
            const errorDetail = error.response.data.detail
            
            if (typeof errorDetail === 'string') {
              errorMessage = errorDetail
            } else if (errorDetail?.error) {
              switch (errorDetail.error) {
                case 'USER_EXISTS':
                  errorMessage = errorDetail.message || 'User already exists in this workspace'
                  break
                case 'INVALID_EMAIL':
                  errorMessage = errorDetail.message || 'Invalid email address format'
                  break
                case 'INVALID_PASSWORD':
                  errorMessage = errorDetail.message || 'Password does not meet requirements'
                  break
                case 'VALIDATION_ERROR':
                  errorMessage = errorDetail.message || 'Validation failed'
                  break
                default:
                  errorMessage = errorDetail.message || 'Registration failed'
              }
            }
          } else if (error.response?.data?.message) {
            errorMessage = error.response.data.message
          } else if (error.message) {
            errorMessage = error.message
          }
          
          set({
            isLoading: false,
            error: errorMessage,
            isAuthenticated: false,
            user: null,
            accessToken: null,
            refreshToken: null,
          })
          throw error
        }
      },

      logout: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          error: null,
          isLoading: false,
        })

        // Clear localStorage
        localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN)
        localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN)
        localStorage.removeItem(STORAGE_KEYS.USER)
        localStorage.removeItem(STORAGE_KEYS.WORKSPACE)
      },

      switchWorkspace: async (workspaceId: number) => {
        try {
          // Update current workspace in backend
          const response = await api.post<any>(`/api/v1/auth/switch-workspace`, { workspace_id: workspaceId })
          
          if (response.data) {
            const { access_token, refresh_token } = response.data;
            
            // Update user state with new workspace
            const currentUser = get().user
            if (currentUser) {
              set({
                user: { ...currentUser, workspace_id: workspaceId },
                accessToken: access_token || get().accessToken,
                refreshToken: refresh_token || get().refreshToken,
                isAuthenticated: true,
              })
            }
            
            // Update localStorage
            if (access_token) localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, access_token)
            if (refresh_token) localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, refresh_token)
            localStorage.setItem(STORAGE_KEYS.WORKSPACE, workspaceId.toString())
            
            return true
          }
          
          return false
        } catch (error: any) {
          console.error('Failed to switch workspace:', error)
          return false
        }
      },

      refreshAccessToken: async () => {
        const { refreshToken: currentRefreshToken } = get()
        if (!currentRefreshToken) {
          get().logout()
          return
        }

        try {
          const response = await api.post<TokenResponse>('/api/v1/auth/refresh', {
            refresh_token: currentRefreshToken,
          })

          const { access_token, refresh_token } = response.data

          set({
            accessToken: access_token,
            refreshToken: refresh_token,
          })

          // Update localStorage
          localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, access_token)
          localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, refresh_token)
        } catch (error) {
          // Refresh failed, logout
          get().logout()
          throw error
        }
      },

      initializeAuth: () => {
        const accessToken = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)
        const refreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN)
        const storedUser = localStorage.getItem(STORAGE_KEYS.USER)

        if (accessToken && refreshToken && storedUser) {
          try {
            const user = JSON.parse(storedUser)
            set({
              user,
              accessToken,
              refreshToken,
              isAuthenticated: true,
            })
          } catch {
            // Invalid stored user data, clear everything
            localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN)
            localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN)
            localStorage.removeItem(STORAGE_KEYS.USER)
          }
        }
      },

      clearError: () => set({ error: null }),

      setLoading: (loading: boolean) => set({ isLoading: loading }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
