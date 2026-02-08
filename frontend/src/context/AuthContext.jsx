import { createContext, useContext, useState, useEffect } from 'react'
import * as api from '../api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.me().then((u) => {
      setUser(u)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const login = async (email, password) => {
    const data = await api.login(email, password)
    localStorage.setItem('dz_token', data.access_token)
    setUser(data.user)
    return data
  }

  const loginGoogle = async (credential) => {
    const data = await api.loginGoogle(credential)
    localStorage.setItem('dz_token', data.access_token)
    setUser(data.user)
    return data
  }

  const logout = () => {
    localStorage.removeItem('dz_token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, loginGoogle, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
