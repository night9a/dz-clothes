import { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'
import './Header.css'

export default function Header() {
  const { t, i18n } = useTranslation()
  const { user, logout } = useAuth()
  const { count } = useCart()
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <header className="header">
      <div className="container header-inner">
        <Link to="/" className="logo">{t('siteName')}</Link>
        <button
          type="button"
          className="header-burger"
          aria-label="Menu"
          aria-expanded={menuOpen}
          onClick={() => setMenuOpen((o) => !o)}
        >
          <span />
          <span />
          <span />
        </button>
        <nav className={`nav ${menuOpen ? 'nav-open' : ''}`}>
          <NavLink to="/" end onClick={() => setMenuOpen(false)}>{t('home')}</NavLink>
          <NavLink to="/shop" onClick={() => setMenuOpen(false)}>{t('shop')}</NavLink>
          <NavLink to="/cart" className="cart-link" onClick={() => setMenuOpen(false)}>
            {t('cart')} {count > 0 && <span className="badge">{count}</span>}
          </NavLink>
          {user?.is_admin && <NavLink to="/admin" onClick={() => setMenuOpen(false)}>{t('admin')}</NavLink>}
          {user ? (
            <button type="button" className="btn btn-ghost nav-btn" onClick={() => { logout(); setMenuOpen(false) }}>{t('logout')}</button>
          ) : (
            <>
              <NavLink to="/login" onClick={() => setMenuOpen(false)}>{t('login')}</NavLink>
              <NavLink to="/register" onClick={() => setMenuOpen(false)}>{t('register')}</NavLink>
            </>
          )}
        </nav>
        <div className="lang-switch">
          <button
            type="button"
            className={i18n.language === 'fr' ? 'active' : ''}
            onClick={() => i18n.changeLanguage('fr')}
          >
            FR
          </button>
          <button
            type="button"
            className={i18n.language === 'ar' ? 'active' : ''}
            onClick={() => i18n.changeLanguage('ar')}
          >
            AR
          </button>
        </div>
      </div>
    </header>
  )
}
