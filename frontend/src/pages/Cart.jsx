import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useCart } from '../context/CartContext'
import { useAuth } from '../context/AuthContext'
import './Cart.css'

export default function Cart() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { user } = useAuth()
  const { items, loading, total, updateQuantity, removeItem } = useCart()

  const handleCheckout = (e) => {
    if (!user) {
      e.preventDefault()
      navigate('/login?redirect=/checkout')
    }
  }

  if (loading) {
    return (
      <div className="container cart-page">
        <p className="empty-state">Chargement...</p>
      </div>
    )
  }

  if (items.length === 0) {
    return (
      <div className="container cart-page">
        <h1 className="page-title">{t('yourCart')}</h1>
        <p className="empty-state">{t('emptyCart')}</p>
        <Link to="/shop" className="btn btn-primary">{t('continueShopping')}</Link>
      </div>
    )
  }

  return (
    <div className="container cart-page">
      <h1 className="page-title">{t('yourCart')}</h1>
      <div className="cart-layout">
        <div className="cart-list">
          {items.map((item) => (
            <div key={item.id} className="cart-item">
              <div className="cart-item-image">
                {item.image_url ? (
                  <img src={item.image_url} alt={item.name} />
                ) : (
                  <div className="product-placeholder" />
                )}
              </div>
              <div className="cart-item-details">
                <Link to={`/product/${item.product_id}`}>{item.name}{(item.option_size || item.option_color) && (
                  <span className="cart-item-options"> — {[item.option_size, item.option_color].filter(Boolean).join(' / ')}</span>
                )}</Link>
                <p className="cart-item-price price-dz">{Number(item.price).toLocaleString('fr-DZ')}</p>
                <div className="cart-item-actions">
                  <input
                    type="number"
                    min={1}
                    max={item.stock || 99}
                    value={item.quantity}
                    onChange={(e) => updateQuantity(item.id, Number(e.target.value) || 1)}
                  />
                  <button type="button" className="btn btn-ghost" onClick={() => removeItem(item.id)}>{t('delete')}</button>
                </div>
              </div>
              <p className="cart-item-total price-dz">{Number(item.price * item.quantity).toLocaleString('fr-DZ')}</p>
            </div>
          ))}
        </div>
        <div className="cart-summary">
          <h3>{t('subtotal')}</h3>
          <p className="cart-total price-dz">{Number(total).toLocaleString('fr-DZ')}</p>
          <Link to={user ? '/checkout' : '/login'} className="btn btn-primary" onClick={handleCheckout}>
            {user ? t('checkout') : (<>{t('login')} — {t('signInToPurchase')}</>)}
          </Link>
        </div>
      </div>
    </div>
  )
}
