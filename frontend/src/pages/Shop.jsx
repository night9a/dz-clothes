import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useCart } from '../context/CartContext'
import * as api from '../api'
import { useState, useEffect } from 'react'
import './Shop.css'

export default function Shop() {
  const { t } = useTranslation()
  const { addToCart } = useCart()
  const [products, setProducts] = useState([])
  const [category, setCategory] = useState('')

  useEffect(() => {
    api.getProducts(category ? { category } : {}).then(setProducts)
  }, [category])

  return (
    <div className="shop-page">
      <div className="container">
        <h1 className="page-title">{t('shop')}</h1>
        <div className="shop-layout">
          <aside className="filters">
            <label className="form-group">
              <span>{t('category')}</span>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="filter-select"
              >
                <option value="">Toutes</option>
                {[...new Set(products.map((p) => p.category).filter(Boolean))].map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </label>
          </aside>
          <div className="product-grid">
            {products.map((p) => (
              <article key={p.id} className="product-card">
                <Link to={`/product/${p.id}`} className="product-card-image-wrap">
                  {p.image_url ? (
                    <img src={p.image_url} alt={p.name} />
                  ) : (
                    <div className="product-placeholder" />
                  )}
                </Link>
                <div className="product-card-body">
                  <h3><Link to={`/product/${p.id}`}>{p.name}</Link></h3>
                  <p className="price-dz">{Number(p.price).toLocaleString('fr-DZ')}</p>
                  <button
                    type="button"
                    className="btn btn-primary"
                    onClick={() => addToCart(p.id)}
                  >
                    {t('addToCart')}
                  </button>
                </div>
              </article>
            ))}
          </div>
        </div>
        {products.length === 0 && (
          <p className="empty-state">{t('emptyCart')}</p>
        )}
      </div>
    </div>
  )
}
