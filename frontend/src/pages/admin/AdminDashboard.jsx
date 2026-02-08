import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import * as api from '../../api'
import './AdminDashboard.css'

export default function AdminDashboard() {
  const { t } = useTranslation()
  const [stats, setStats] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.adminStats().then(setStats).catch((e) => setError(e.message))
  }, [])

  if (error) return <p className="error-msg">{error}</p>
  if (!stats) return <p>Chargement...</p>

  const chartData = (stats.sales_by_day || []).slice().reverse().map((d) => ({
    date: d.date.slice(0, 10),
    ventes: d.total,
    commandes: d.count,
  }))

  return (
    <>
      <h1 className="admin-page-title">{t('adminDashboard')}</h1>
      <div className="admin-stats-grid">
        <div className="admin-stat-card">
          <h4>{t('orders')}</h4>
          <p>{stats.total_orders}</p>
        </div>
        <div className="admin-stat-card">
          <h4>{t('sales')} (DA)</h4>
          <p>{Number(stats.total_sales).toFixed(0)}</p>
        </div>
        <div className="admin-stat-card">
          <h4>{t('adminProducts')}</h4>
          <p>{stats.total_products}</p>
        </div>
      </div>
      <div className="chart-container">
        <h3>Ventes par jour</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="date" stroke="var(--text-muted)" fontSize={12} />
            <YAxis stroke="var(--text-muted)" fontSize={12} tickFormatter={(v) => `${v} DA`} />
            <Tooltip contentStyle={{ background: 'var(--surface2)', border: '1px solid var(--border)', borderRadius: 8 }} />
            <Line type="monotone" dataKey="ventes" stroke="var(--accent)" strokeWidth={2} dot={{ fill: 'var(--accent)' }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </>
  )
}
