import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import * as api from '../../api'
import './AdminOrders.css'

export default function AdminOrders() {
  const { t } = useTranslation()
  const [orders, setOrders] = useState([])
  const [error, setError] = useState('')
  const [updating, setUpdating] = useState(null)

  useEffect(() => {
    api.adminOrders().then(setOrders).catch((e) => setError(e.message))
  }, [])

  const updateStatus = (id, status) => {
    setUpdating(id)
    api.adminUpdateOrderStatus(id, status).then(() => {
      setOrders((prev) => prev.map((o) => (o.id === id ? { ...o, status } : o)))
      setUpdating(null)
    }).catch(() => setUpdating(null))
  }

  if (error) return <p className="error-msg">{error}</p>

  return (
    <>
      <h1 className="admin-page-title">{t('adminOrders')}</h1>
      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>{t('orderNumber')}</th>
              <th>{t('date')}</th>
              <th>{t('customer')}</th>
              <th>{t('total')}</th>
              <th>{t('status')}</th>
              <th>Baridi</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {orders.map((o) => (
              <tr key={o.id}>
                <td><strong>{o.order_number}</strong></td>
                <td>{o.created_at ? new Date(o.created_at).toLocaleDateString() : '-'}</td>
                <td>{o.email} — {o.full_name}</td>
                <td>{Number(o.total).toFixed(0)} DA</td>
                <td>{o.status}</td>
                <td>{o.baridi_phone} {o.baridi_reference && `(${o.baridi_reference})`}</td>
                <td>
                  <select
                    value={o.status}
                    onChange={(e) => updateStatus(o.id, e.target.value)}
                    disabled={updating === o.id}
                    className="status-select"
                  >
                    <option value="pending">{t('pending')}</option>
                    <option value="paid">{t('paid')}</option>
                    <option value="shipped">{t('shipped')}</option>
                    <option value="delivered">{t('delivered')}</option>
                    <option value="cancelled">{t('cancelled')}</option>
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {orders.length === 0 && <p className="empty-state">Aucune commande.</p>}
    </>
  )
}
