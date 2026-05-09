import { api } from '@/utils/api'
import { User, UserCreate, UserLogin, TokenResponse, RefreshTokenRequest } from '@/types'
import { API_ENDPOINTS } from '@/constants/api'

export const authService = {
  // Login user
  login: async (credentials: UserLogin): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>(
      API_ENDPOINTS.AUTH.LOGIN,
      credentials
    )
    return response.data
  },

  // Register new user
  register: async (userData: UserCreate): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>(
      API_ENDPOINTS.AUTH.REGISTER,
      userData
    )
    return response.data
  },

  // Refresh access token
  refreshToken: async (refreshToken: string): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>(
      API_ENDPOINTS.AUTH.REFRESH,
      { refresh_token: refreshToken } as RefreshTokenRequest
    )
    return response.data
  },

  // Get current user info
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>(API_ENDPOINTS.AUTH.ME)
    return response.data
  },

  // Logout (client-side only, just clear tokens)
  logout: (): void => {
    // Tokens are cleared by the auth store
    // This method is for consistency and potential future server-side logout
  },
}
