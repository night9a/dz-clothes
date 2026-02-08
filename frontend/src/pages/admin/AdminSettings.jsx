import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import * as api from '../../api'
import './AdminSettings.css'

export default function AdminSettings() {
  const { t } = useTranslation()
  const [chatId, setChatId] = useState('')
  const [loaded, setLoaded] = useState(false)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    api.adminTelegramGet().then((r) => {
      setChatId(r.telegram_chat_id || '')
      setLoaded(true)
    }).catch(() => setLoaded(true))
  }, [])

  const save = async () => {
    setSaving(true)
    setMessage('')
    try {
      await api.adminTelegramSet(chatId)
      setMessage('Paramètres enregistrés. Si vous avez renseigné un Chat ID, vous recevrez un message de test sur Telegram.')
    } catch (e) {
      setMessage(e.message || 'Erreur')
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <h1 className="admin-page-title">{t('adminSettings')}</h1>
      <div className="settings-block">
        <h2>{t('telegramNotifications')}</h2>
        <p className="form-hint">
          Créez un bot avec @BotFather sur Telegram, puis envoyez /start à votre bot. Le bot vous renverra votre Chat ID. Collez-le ci-dessous pour recevoir une notification à chaque nouvelle commande.
        </p>
        <div className="form-group">
          <label>{t('telegramChatId')}</label>
          <input
            type="text"
            value={chatId}
            onChange={(e) => setChatId(e.target.value)}
            placeholder="Ex: 123456789"
          />
        </div>
        <button type="button" className="btn btn-primary" onClick={save} disabled={saving}>
          {saving ? '...' : t('save')}
        </button>
        {message && <p className={message.startsWith('Paramètres') ? 'success-msg' : 'error-msg'} style={{ marginTop: '1rem' }}>{message}</p>}
      </div>
    </>
  )
}
