import { useState } from 'react'
import { useAuthStore } from '@/stores/authStore'
import { useUIStore } from '@/stores/uiStore'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Moon, Sun, LogOut, User as UserIcon } from 'lucide-react'
import { Theme } from '@/types'

const SettingsPage: React.FC = () => {
  const { user, logout } = useAuthStore()
  const { theme, setTheme } = useUIStore()
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPasswordForm, setShowPasswordForm] = useState(false)

  const handleLogout = () => {
    if (confirm('Are you sure you want to logout?')) {
      logout()
      window.location.href = '/login'
    }
  }

  const handlePasswordChange = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (newPassword !== confirmPassword) {
      alert('Passwords do not match')
      return
    }

    if (newPassword.length < 8) {
      alert('Password must be at least 8 characters')
      return
    }

    // TODO: Implement password change API call
    console.log('Password change not implemented yet')
    setShowPasswordForm(false)
    setCurrentPassword('')
    setNewPassword('')
    setConfirmPassword('')
  }

  const toggleTheme = (newTheme: Theme) => {
    setTheme(newTheme)
  }

  const getSystemTheme = (): Theme => {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark'
    }
    return 'light'
  }

  const getEffectiveTheme = (): Theme => {
    if (theme === 'system') {
      return getSystemTheme()
    }
    return theme
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Settings</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Profile Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <UserIcon className="h-5 w-5 mr-2" />
                Profile Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700">Email</label>
                <Input value={user?.email || ''} disabled />
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-700">User ID</label>
                <Input value={user?.id?.toString() || ''} disabled />
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-700">Workspace ID</label>
                <Input value={user?.workspace_id?.toString() || ''} disabled />
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-700">Member Since</label>
                <Input 
                  value={user?.created_at ? new Date(user.created_at).toLocaleDateString() : ''} 
                  disabled 
                />
              </div>
            </CardContent>
          </Card>

          {/* Appearance Settings */}
          <Card>
            <CardHeader>
              <CardTitle>Appearance</CardTitle>
              <CardDescription>
                Customize your interface theme
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700 mb-3 block">
                  Theme
                </label>
                <div className="grid grid-cols-3 gap-2">
                  <Button
                    variant={theme === 'light' ? 'default' : 'outline'}
                    onClick={() => toggleTheme('light')}
                    className="flex items-center space-x-2"
                  >
                    <Sun className="h-4 w-4" />
                    Light
                  </Button>
                  
                  <Button
                    variant={theme === 'dark' ? 'default' : 'outline'}
                    onClick={() => toggleTheme('dark')}
                    className="flex items-center space-x-2"
                  >
                    <Moon className="h-4 w-4" />
                    Dark
                  </Button>
                  
                  <Button
                    variant={theme === 'system' ? 'default' : 'outline'}
                    onClick={() => toggleTheme('system')}
                    className="flex items-center space-x-2"
                  >
                    <div className="h-4 w-4 flex items-center justify-center">
                      <Sun className="h-3 w-3" />
                    </div>
                    System
                  </Button>
                </div>
              </div>
              
              <div className="text-sm text-gray-600">
                Current theme: <span className="font-medium">{getEffectiveTheme()}</span>
                {theme === 'system' && (
                  <span> (detected: {getSystemTheme()})</span>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Password Change */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Security</CardTitle>
            <CardDescription>
              Change your password to keep your account secure
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!showPasswordForm ? (
              <Button onClick={() => setShowPasswordForm(true)}>
                Change Password
              </Button>
            ) : (
              <form onSubmit={handlePasswordChange} className="space-y-4">
                <div>
                  <label htmlFor="currentPassword" className="text-sm font-medium text-gray-700">
                    Current Password
                  </label>
                  <Input
                    id="currentPassword"
                    type="password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    placeholder="Enter current password"
                    required
                  />
                </div>
                
                <div>
                  <label htmlFor="newPassword" className="text-sm font-medium text-gray-700">
                    New Password
                  </label>
                  <Input
                    id="newPassword"
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Enter new password"
                    required
                  />
                </div>
                
                <div>
                  <label htmlFor="confirmPassword" className="text-sm font-medium text-gray-700">
                    Confirm New Password
                  </label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Confirm new password"
                    required
                  />
                </div>

                <div className="flex space-x-3">
                  <Button type="submit">
                    Update Password
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setShowPasswordForm(false)
                      setCurrentPassword('')
                      setNewPassword('')
                      setConfirmPassword('')
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            )}
          </CardContent>
        </Card>

        {/* Danger Zone */}
        <Card className="mt-8 border-red-200">
          <CardHeader>
            <CardTitle className="text-red-600">Danger Zone</CardTitle>
            <CardDescription>
              Irreversible actions that affect your account
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg">
                <div>
                  <h4 className="font-medium text-red-900">Logout</h4>
                  <p className="text-sm text-red-700">
                    Sign out of your current session
                  </p>
                </div>
                <Button
                  variant="destructive"
                  onClick={handleLogout}
                  className="flex items-center space-x-2"
                >
                  <LogOut className="h-4 w-4" />
                  Logout
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default SettingsPage
