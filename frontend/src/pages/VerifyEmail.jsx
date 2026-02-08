import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import * as api from '../api'
import './Auth.css'

export default function VerifyEmail() {
  const { t } = useTranslation()
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  const [status, setStatus] = useState('loading') // loading | ok | error

  useEffect(() => {
    if (!token) {
      setStatus('error')
      return
    }
    api.verifyEmail(token).then(() => setStatus('ok')).catch(() => setStatus('error'))
  }, [token])

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>{t('verifyEmail')}</h1>
        {status === 'loading' && <p>Vérification en cours...</p>}
        {status === 'ok' && (
          <>
            <p className="success-msg">Votre email a été vérifié. Vous pouvez vous connecter.</p>
            <Link to="/login" className="btn btn-primary">{t('login')}</Link>
          </>
        )}
        {status === 'error' && (
          <>
            <p className="error-msg">Lien invalide ou expiré.</p>
            <Link to="/register" className="btn btn-ghost">{t('register')}</Link>
          </>
        )}
      </div>
    </div>
  )
}
