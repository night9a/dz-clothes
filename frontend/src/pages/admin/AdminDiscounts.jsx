import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import * as api from '../../api'
import './AdminDiscounts.css'

const defaultDiscount = {
  code: '',
  percent_off: 0,
  amount_off: 0,
  min_purchase: 0,
  max_uses: '',
  is_active: true,
}

export default function AdminDiscounts() {
  const { t } = useTranslation()
  const [discounts, setDiscounts] = useState([])
  const [error, setError] = useState('')
  const [modal, setModal] = useState(null)
  const [form, setForm] = useState(defaultDiscount)
  const [saving, setSaving] = useState(false)

  const load = () => api.adminDiscounts().then(setDiscounts).catch((e) => setError(e.message))

  useEffect(() => {
    load()
  }, [])

  const openAdd = () => {
    setForm(defaultDiscount)
    setModal('add')
  }
  const openEdit = (d) => {
    setForm({
      code: d.code || '',
      percent_off: d.percent_off ?? 0,
      amount_off: d.amount_off ?? 0,
      min_purchase: d.min_purchase ?? 0,
      max_uses: d.max_uses ?? '',
      is_active: d.is_active !== false,
    })
    setModal({ id: d.id })
  }
  const closeModal = () => setModal(null)

  const save = async () => {
    setSaving(true)
    try {
      const payload = {
        ...form,
        percent_off: Number(form.percent_off) || 0,
        amount_off: Number(form.amount_off) || 0,
        min_purchase: Number(form.min_purchase) || 0,
        max_uses: form.max_uses === '' ? null : Number(form.max_uses),
      }
      if (modal === 'add') {
        await api.adminCreateDiscount(payload)
      } else {
        await api.adminUpdateDiscount(modal.id, payload)
      }
      closeModal()
      load()
    } catch (e) {
      setError(e.message)
    } finally {
      setSaving(false)
    }
  }

  const remove = async (id) => {
    if (!confirm('Supprimer cette réduction ?')) return
    try {
      await api.adminDeleteDiscount(id)
      load()
    } catch (e) {
      setError(e.message)
    }
  }

  if (error) return <p className="error-msg">{error}</p>

  return (
    <>
      <h1 className="admin-page-title">{t('adminDiscounts')}</h1>
      <button type="button" className="btn btn-primary" onClick={openAdd}>{t('add')} {t('code')}</button>
      <div className="admin-table-wrap" style={{ marginTop: '1rem' }}>
        <table className="admin-table">
          <thead>
            <tr>
              <th>{t('code')}</th>
              <th>%</th>
              <th>Montant (DA)</th>
              <th>Min achat</th>
              <th>{t('usedCount')}</th>
              <th>{t('active')}</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {discounts.map((d) => (
              <tr key={d.id}>
                <td><strong>{d.code}</strong></td>
                <td>{Number(d.percent_off).toFixed(0)}</td>
                <td>{Number(d.amount_off).toFixed(0)}</td>
                <td>{Number(d.min_purchase).toFixed(0)}</td>
                <td>{d.used_count ?? 0} {d.max_uses != null ? `/ ${d.max_uses}` : ''}</td>
                <td>{d.is_active ? 'Oui' : 'Non'}</td>
                <td>
                  <div className="admin-actions">
                    <button type="button" className="btn btn-ghost" onClick={() => openEdit(d)}>{t('edit')}</button>
                    <button type="button" className="btn btn-ghost" onClick={() => remove(d.id)}>{t('delete')}</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {discounts.length === 0 && <p className="empty-state">Aucune réduction.</p>}

      {modal && (
        <div className="admin-modal-overlay" onClick={closeModal}>
          <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
            <h3>{modal === 'add' ? t('add') : t('edit')} réduction</h3>
            <div className="form-group">
              <label>{t('code')}</label>
              <input value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value.toUpperCase() })} placeholder="PROMO20" />
            </div>
            <div className="form-group">
              <label>{t('percentOff')}</label>
              <input type="number" min={0} max={100} value={form.percent_off} onChange={(e) => setForm({ ...form, percent_off: e.target.value })} />
            </div>
            <div className="form-group">
              <label>{t('amountOff')}</label>
              <input type="number" min={0} value={form.amount_off} onChange={(e) => setForm({ ...form, amount_off: e.target.value })} />
            </div>
            <div className="form-group">
              <label>{t('minPurchase')}</label>
              <input type="number" min={0} value={form.min_purchase} onChange={(e) => setForm({ ...form, min_purchase: e.target.value })} />
            </div>
            <div className="form-group">
              <label>{t('maxUses')}</label>
              <input type="number" min={0} value={form.max_uses} onChange={(e) => setForm({ ...form, max_uses: e.target.value })} placeholder="Illimité" />
            </div>
            <div className="form-group">
              <label>
                <input type="checkbox" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} />
                {' '}Actif
              </label>
            </div>
            <div className="admin-modal-actions">
              <button type="button" className="btn btn-primary" onClick={save} disabled={saving}>{t('save')}</button>
              <button type="button" className="btn btn-ghost" onClick={closeModal}>Annuler</button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
