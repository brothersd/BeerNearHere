import { createContext, useContext, useState, useCallback, useEffect } from 'react'
import api from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true) // Start as loading to check storage
  const [error, setError] = useState('')

  // Check for existing session on startup
  useEffect(() => {
    const access = localStorage.getItem('access_token')
    const refresh = localStorage.getItem('refresh_token')
    const username = localStorage.getItem('username') // Added to persist name

    if (access && username) {
      setUser({ username, access, refresh })
      api.defaults.headers.common['Authorization'] = `Bearer ${access}`
    }
    setLoading(false)
  }, [])

  const login = useCallback(async (username, password) => {
    setLoading(true)
    setError('')
    try {
      const res = await api.post('/auth/login/', { username, password })
      const data = res.data
      
      setUser({ username: data.username, access: data.access, refresh: data.refresh })
      
      // Persist to storage
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      localStorage.setItem('username', data.username)
      
      api.defaults.headers.common['Authorization'] = `Bearer ${data.access}`
      return true
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed.')
      return false
    } finally {
      setLoading(false)
    }
  }, [])

  const register = useCallback(async (username, password) => {
    setLoading(true)
    setError('')
    try {
      const res = await api.post('/auth/register/', { username, password })
      const data = res.data
      
      setUser({ username: data.username, access: data.access, refresh: data.refresh })
      
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      localStorage.setItem('username', data.username)
      
      api.defaults.headers.common['Authorization'] = `Bearer ${data.access}`
      return true
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed.')
      return false
    } finally {
      setLoading(false)
    }
  }, [])

  const logout = useCallback(async () => {
    try {
      if (user?.refresh) {
        await api.post('/auth/logout/', { refresh: user.refresh })
      }
    } catch (_) {
      // Ignore fail
    } finally {
      setUser(null)
      delete api.defaults.headers.common['Authorization']
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('username')
    }
  }, [user])

  return (
    <AuthContext.Provider value={{ user, loading, error, setError, login, register, logout }}>
      {!loading && children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)