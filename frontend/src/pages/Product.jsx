import { useParams, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useCart } from '../context/CartContext'
import * as api from '../api'
import { useState, useEffect } from 'react'
import './Product.css'

export default function Product() {
  const { id } = useParams()
  const { t } = useTranslation()
  const { addToCart } = useCart()
  const [product, setProduct] = useState(null)
  const [qty, setQty] = useState(1)
  const [size, setSize] = useState('')
  const [color, setColor] = useState('')
  const [added, setAdded] = useState(false)

  useEffect(() => {
    api.getProduct(Number(id)).then(setProduct)
  }, [id])

  useEffect(() => {
    if (product?.options_sizes?.length) setSize(product.options_sizes[0])
    if (product?.options_colors?.length) setColor(product.options_colors[0])
  }, [product])

  const handleAdd = () => {
    addToCart(product.id, qty, size || undefined, color || undefined).then(() => setAdded(true))
  }

  if (!product) {
    return (
      <div className="container product-page">
        <p className="empty-state">Produit introuvable.</p>
      </div>
    )
  }

  const hasSizes = product.options_sizes?.length > 0
  const hasColors = product.options_colors?.length > 0

  return (
    <div className="container product-page">
      <div className="product-detail">
        <div className="product-detail-image">
          {product.image_url ? (
            <img src={product.image_url} alt={product.name} />
          ) : (
            <div className="product-placeholder" />
          )}
        </div>
        <div className="product-detail-info">
          <h1>{product.name}</h1>
          <p className="product-detail-price price-dz">{Number(product.price).toLocaleString('fr-DZ')}</p>
          {product.description && <p className="product-detail-desc">{product.description}</p>}
          {hasSizes && (
            <div className="form-group">
              <label>{t('size')}</label>
              <select value={size} onChange={(e) => setSize(e.target.value)}>
                {product.options_sizes.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
          )}
          {hasColors && (
            <div className="form-group">
              <label>{t('color')}</label>
              <select value={color} onChange={(e) => setColor(e.target.value)}>
                {product.options_colors.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          )}
          <div className="form-group">
            <label>{t('quantity')}</label>
            <input
              type="number"
              min={1}
              max={product.stock || 99}
              value={qty}
              onChange={(e) => setQty(Number(e.target.value) || 1)}
            />
          </div>
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleAdd}
            disabled={product.stock === 0}
          >
            {added ? '✓ Ajouté' : t('addToCart')}
          </button>
          <Link to="/shop" className="btn btn-ghost" style={{ marginTop: '0.5rem' }}>{t('continueShopping')}</Link>
        </div>
      </div>
    </div>
  )
}
