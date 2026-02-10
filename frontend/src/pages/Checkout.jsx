import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useCart } from '../context/CartContext'
import { useAuth } from '../context/AuthContext'
import * as api from '../api'
import './Checkout.css'

export default function Checkout() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { items, total, refresh } = useCart()
  const { user } = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [orderNumber, setOrderNumber] = useState(null)
  const [form, setForm] = useState({
    email: user?.email || '',
    full_name: '',
    shipping_address: '',
    baridi_phone: '',
    baridi_reference: '',
    discount_code: '',
  })
  const [discountApplied, setDiscountApplied] = useState(null)
  const [discountError, setDiscountError] = useState('')
  const finalTotal = discountApplied != null ? total - discountApplied : total

  useEffect(() => {
    if (user?.email) setForm((f) => ({ ...f, email: user.email }))
  }, [user])

  useEffect(() => {
    refresh()
  }, [refresh])

  const handleApplyDiscount = () => {
    if (!form.discount_code.trim()) return
    setDiscountError('')
    api.validateDiscount(form.discount_code.trim(), total).then((res) => {
      setDiscountApplied(res.discount_amount)
    }).catch((err) => {
      setDiscountError(err.message)
      setDiscountApplied(null)
    })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    api.checkout({
      email: form.email,
      full_name: form.full_name,
      shipping_address: form.shipping_address,
      baridi_phone: form.baridi_phone,
      baridi_reference: form.baridi_reference,
      discount_code: discountApplied != null ? form.discount_code : undefined,
    }).then((res) => {
      setOrderNumber(res.order_number)
      refresh()
    }).catch((err) => {
      setError(err.message)
      setLoading(false)
    })
  }

  if (!user) {
    return (
      <div className="container checkout-page">
        <div className="checkout-login-required">
          <h1 className="page-title">{t('checkout')}</h1>
          <p className="checkout-must-login">{t('signInToPurchase')}</p>
          <Link to="/login?redirect=/checkout" className="btn btn-primary">{t('login')}</Link>
          <Link to="/shop" className="btn btn-ghost">{t('continueShopping')}</Link>
        </div>
      </div>
    )
  }

  if (items.length === 0 && !orderNumber) {
    return (
      <div className="container checkout-page">
        <p className="empty-state">{t('emptyCart')}</p>
        <Link to="/shop" className="btn btn-primary">{t('continueShopping')}</Link>
      </div>
    )
  }

  if (orderNumber) {
    return (
      <div className="container checkout-page">
        <div className="checkout-success">
          <h1>{t('orderSuccess')}</h1>
          <p>{t('orderNumber')}: <strong>{orderNumber}</strong></p>
          <Link to="/shop" className="btn btn-primary">{t('continueShopping')}</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="container checkout-page">
      <h1 className="page-title">{t('checkout')}</h1>
      <div className="checkout-ccp-notice">
        <strong>{t('ccpVerification')}</strong>
      </div>
      <form onSubmit={handleSubmit} className="checkout-form">
        <div className="checkout-grid">
          <div className="checkout-form-section">
            <h2>{t('baridiMob')}</h2>
            <p className="form-hint">Renseignez les informations de votre paiement Baridi Mob (Algérie Poste).</p>
            <div className="form-group">
              <label>{t('baridiPhone')}</label>
              <input
                type="text"
                placeholder="Ex: 0550123456"
                value={form.baridi_phone}
                onChange={(e) => setForm({ ...form, baridi_phone: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>{t('baridiReference')}</label>
              <input
                type="text"
                placeholder="Référence de la transaction"
                value={form.baridi_reference}
                onChange={(e) => setForm({ ...form, baridi_reference: e.target.value })}
                required
              />
            </div>
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
                required
              />
            </div>
            <div className="form-group">
              <label>{t('shippingAddress')}</label>
              <textarea
                rows={3}
                value={form.shipping_address}
                onChange={(e) => setForm({ ...form, shipping_address: e.target.value })}
                required
              />
            </div>
          </div>
          <div className="checkout-summary">
            <h3>{t('yourCart')}</h3>
            <ul>
              {items.map((i) => (
                <li key={i.id}>{i.name} × {i.quantity} — <span className="price-dz">{Number(i.price * i.quantity).toLocaleString('fr-DZ')}</span></li>
              ))}
            </ul>
            <div className="discount-row">
              <div className="form-group">
                <label>{t('discountCode')}</label>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <input
                    type="text"
                    value={form.discount_code}
                    onChange={(e) => setForm({ ...form, discount_code: e.target.value })}
                    placeholder="CODE"
                  />
                  <button type="button" className="btn btn-ghost" onClick={handleApplyDiscount}>{t('apply')}</button>
                </div>
              </div>
              {discountError && <p className="error-msg">{discountError}</p>}
              {discountApplied != null && <p className="success-msg">-{discountApplied.toFixed(0)} DA</p>}
            </div>
            <p className="summary-subtotal">{t('subtotal')}: <span className="price-dz">{Number(total).toLocaleString('fr-DZ')}</span></p>
            {discountApplied != null && <p className="summary-discount">Réduction: -<span className="price-dz">{Number(discountApplied).toLocaleString('fr-DZ')}</span></p>}
            <p className="summary-total">{t('total')}: <span className="price-dz">{Number(finalTotal).toLocaleString('fr-DZ')}</span></p>
            {error && <p className="error-msg">{error}</p>}
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Envoi...' : t('checkout')}
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}
