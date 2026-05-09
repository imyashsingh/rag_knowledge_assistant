# Frontend Token Management Guide

This guide explains how to handle JWT tokens in the frontend for the RAG Knowledge Assistant API.

## Token Types

### Access Token
- **Purpose**: Authenticate API requests
- **Lifetime**: 15 minutes
- **Storage**: Memory or sessionStorage
- **Usage**: Send in `Authorization: Bearer <token>` header

### Refresh Token
- **Purpose**: Get new access tokens when expired
- **Lifetime**: 7 days
- **Storage**: Secure storage (localStorage or httpOnly cookie)
- **Usage**: Send to `/api/v1/auth/refresh` endpoint

## Storage Strategy

### Recommended Approach
```javascript
// Access token - short lived, stored in memory
let accessToken = null;

// Refresh token - long lived, stored securely
const refreshToken = localStorage.getItem('refreshToken');
```

### Alternative: httpOnly Cookies
```javascript
// Set refresh token as httpOnly cookie from backend
// Access token still in memory
```

## Token Flow

### 1. Login
```javascript
const response = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});

const { access_token, refresh_token } = await response.json();

// Store tokens
accessToken = access_token;
localStorage.setItem('refreshToken', refresh_token);
```

### 2. API Requests
```javascript
async function apiRequest(url, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`,
    ...options.headers
  };

  try {
    const response = await fetch(url, { ...options, headers });
    
    if (response.status === 401) {
      // Try to refresh token
      const newToken = await refreshAccessToken();
      if (newToken) {
        headers['Authorization'] = `Bearer ${newToken}`;
        return fetch(url, { ...options, headers });
      }
    }
    
    return response;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}
```

### 3. Token Refresh
```javascript
async function refreshAccessToken() {
  const refreshToken = localStorage.getItem('refreshToken');
  
  if (!refreshToken) {
    redirectToLogin();
    return null;
  }

  try {
    const response = await fetch('/api/v1/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken })
    });

    if (response.ok) {
      const { access_token, refresh_token } = await response.json();
      accessToken = access_token;
      localStorage.setItem('refreshToken', refresh_token);
      return access_token;
    } else {
      // Refresh token invalid/expired
      logout();
      return null;
    }
  } catch (error) {
    console.error('Token refresh failed:', error);
    logout();
    return null;
  }
}
```

### 4. Logout
```javascript
function logout() {
  accessToken = null;
  localStorage.removeItem('refreshToken');
  redirectToLogin();
}
```

## Security Best Practices

### Access Token
- Store in memory (not localStorage) for XSS protection
- Automatically refresh when expired
- Clear on page reload if using sessionStorage

### Refresh Token
- Store in localStorage with XSS protection
- Consider httpOnly cookies for maximum security
- Clear on logout
- Handle expiration gracefully

### Request Interceptor
```javascript
// Example with axios
axios.interceptors.request.use(config => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      const newToken = await refreshAccessToken();
      if (newToken) {
        error.config.headers.Authorization = `Bearer ${newToken}`;
        return axios.request(error.config);
      }
    }
    return Promise.reject(error);
  }
);
```

## Error Handling

### Token Expired
- HTTP 401 responses trigger automatic refresh
- If refresh fails, redirect to login
- Show user-friendly error messages

### Network Issues
- Retry failed requests after successful refresh
- Handle offline scenarios gracefully
- Provide fallback authentication methods

## Implementation Notes

- **Pure Stateless**: Backend stores no tokens
- **Single Refresh Token**: Same token works across all devices
- **Automatic Rotation**: New refresh token issued on each refresh
- **No Backend Logout**: Logout is client-side only (clear tokens)

This approach provides maximum scalability and security while following industry best practices for JWT authentication.
