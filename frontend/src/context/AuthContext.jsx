// src/context/AuthContext.jsx
import { createContext, useContext, useState, useCallback } from 'react'
import api from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)      // { username, access, refresh }
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const login = useCallback(async (username, password) => {
    setLoading(true)
    setError('')
    try {
      const res = await api.post('/auth/login/', { username, password })
      const data = res.data
      setUser({ username: data.username, access: data.access, refresh: data.refresh })
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
      // Logout even if API call fails
    } finally {
      setUser(null)
      delete api.defaults.headers.common['Authorization']
    }
  }, [user])

  return (
    <AuthContext.Provider value={{ user, loading, error, setError, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
