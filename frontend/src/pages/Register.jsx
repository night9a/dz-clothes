import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { GoogleLogin } from '@react-oauth/google'
import * as api from '../api'
import { useAuth } from '../context/AuthContext'
import './Auth.css'

export default function Register() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { loginGoogle } = useAuth()
  const [form, setForm] = useState({ email: '', password: '', full_name: '' })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)
  const [googleLoading, setGoogleLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.register(form)
      setSuccess(true)
    } catch (err) {
      setError(err.message || 'Erreur')
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleSuccess = async (credentialResponse) => {
    if (!credentialResponse?.credential) return
    setGoogleLoading(true)
    setError('')
    try {
      await loginGoogle(credentialResponse.credential)
      navigate('/')
    } catch (err) {
      setError(err.message || 'Erreur')
    } finally {
      setGoogleLoading(false)
    }
  }

  if (success) {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <h1>{t('verifyEmail')}</h1>
          <p className="success-msg">{t('verifyEmailSent')}</p>
          <Link to="/login" className="btn btn-primary">{t('login')}</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>{t('register')}</h1>
        <div className="auth-google-wrap">
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={() => { setError('Connexion Google annulée'); setGoogleLoading(false) }}
            useOneTap={false}
            theme="filled_black"
            size="large"
            text="signup_with"
            locale="fr"
            shape="pill"
          />
        </div>
        <div className="auth-divider">
          <span>ou</span>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>{t('email')}</label>
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>{t('fullName')}</label>
            <input
              type="text"
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>{t('password')}</label>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
              minLength={6}
            />
          </div>
          {error && <p className="error-msg">{error}</p>}
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? '...' : t('register')}
          </button>
        </form>
        <p className="auth-switch">
          {t('hasAccount')} <Link to="/login">{t('login')}</Link>
        </p>
      </div>
    </div>
  )
}
