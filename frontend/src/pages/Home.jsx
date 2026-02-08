import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useCart } from '../context/CartContext'
import * as api from '../api'
import { useState, useEffect } from 'react'
import './Home.css'

export default function Home() {
  const { t } = useTranslation()
  const { addToCart } = useCart()
  const [products, setProducts] = useState([])

  useEffect(() => {
    api.getProducts().then(setProducts)
  }, [])

  const featured = products.slice(0, 6)

  return (
    <div className="home">
      <section className="hero">
        <div className="container">
          <h1 className="hero-title">{t('siteName')}</h1>
          <p className="hero-subtitle">
            {t('shop')} — Mode & style
          </p>
          <Link to="/shop" className="btn btn-primary hero-cta">{t('shop')}</Link>
        </div>
      </section>

      <section className="section featured">
        <div className="container">
          <h2 className="section-title">{t('shop')}</h2>
          <div className="product-grid">
            {featured.map((p) => (
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
          {featured.length === 0 && (
            <p className="empty-state">Aucun produit pour le moment.</p>
          )}
          <div className="section-cta">
            <Link to="/shop" className="btn btn-ghost">{t('continueShopping')}</Link>
          </div>
        </div>
      </section>
    </div>
  )
}
