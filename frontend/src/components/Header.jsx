import { useState, useEffect } from 'react'
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
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <header className={`header ${scrolled ? 'header-scrolled' : ''}`}>
      <div className="header-glow" />
      <div className="container header-inner">
        <Link to="/" className="logo">
          <span className="logo-icon">◆</span>
          <span className="logo-text">{t('siteName')}</span>
        </Link>
        
        <button
          type="button"
          className="header-burger"
          aria-label="Menu"
          aria-expanded={menuOpen}
          onClick={() => setMenuOpen((o) => !o)}
        >
          <span className={menuOpen ? 'active' : ''} />
          <span className={menuOpen ? 'active' : ''} />
          <span className={menuOpen ? 'active' : ''} />
        </button>

        <nav className={`nav ${menuOpen ? 'nav-open' : ''}`}>
          <NavLink to="/" end onClick={() => setMenuOpen(false)}>
            {t('home')}
          </NavLink>
          <NavLink to="/shop" onClick={() => setMenuOpen(false)}>
            {t('shop')}
          </NavLink>
          <NavLink to="/cart" className="cart-link" onClick={() => setMenuOpen(false)}>
            {t('cart')}
            {count > 0 && (
              <span className="badge">
                <span className="badge-inner">{count}</span>
              </span>
            )}
          </NavLink>
          {user?.is_admin && (
            <NavLink to="/admin" onClick={() => setMenuOpen(false)}>
              {t('admin')}
            </NavLink>
          )}
          {user ? (
            <button 
              type="button" 
              className="btn btn-ghost nav-btn" 
              onClick={() => { logout(); setMenuOpen(false) }}
            >
              {t('logout')}
            </button>
          ) : (
            <>
              <NavLink to="/login" onClick={() => setMenuOpen(false)}>
                {t('login')}
              </NavLink>
              <NavLink to="/register" className="nav-highlight" onClick={() => setMenuOpen(false)}>
                {t('register')}
              </NavLink>
            </>
          )}
        </nav>

        <div className="lang-switch">
          <button
            type="button"
            className={i18n.language === 'fr' ? 'active' : ''}
            onClick={() => i18n.changeLanguage('fr')}
            aria-label="French"
          >
            FR
          </button>
          <button
            type="button"
            className={i18n.language === 'ar' ? 'active' : ''}
            onClick={() => i18n.changeLanguage('ar')}
            aria-label="Arabic"
          >
            AR
          </button>
        </div>
      </div>
    </header>
  )
}