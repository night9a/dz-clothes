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

  // Lock body scroll when menu is open
  useEffect(() => {
    if (menuOpen) {
      document.body.classList.add('menu-open')
    } else {
      document.body.classList.remove('menu-open')
    }
    return () => document.body.classList.remove('menu-open')
  }, [menuOpen])

  const closeMenu = () => setMenuOpen(false)

  return (
    <header className={`header ${scrolled ? 'header-scrolled' : ''}`}>
      <div className="header-glow" />
      <div className="container header-inner">
        <Link to="/" className="logo" onClick={closeMenu}>
          <span className="logo-icon">◆</span>
          <span className="logo-text">{t('siteName')}</span>
        </Link>
        
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

        <button
          type="button"
          className="header-burger"
          aria-label={menuOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={menuOpen}
          onClick={() => setMenuOpen((o) => !o)}
        >
          <span className={menuOpen ? 'active' : ''} />
          <span className={menuOpen ? 'active' : ''} />
          <span className={menuOpen ? 'active' : ''} />
        </button>

        <nav className={`nav ${menuOpen ? 'nav-open' : ''}`}>
          <NavLink to="/" end onClick={closeMenu}>
            {t('home')}
          </NavLink>
          <NavLink to="/shop" onClick={closeMenu}>
            {t('shop')}
          </NavLink>
          <NavLink to="/cart" className="cart-link" onClick={closeMenu}>
            {t('cart')}
            {count > 0 && (
              <span className="badge">
                <span className="badge-inner">{count}</span>
              </span>
            )}
          </NavLink>
          {user?.is_admin && (
            <NavLink to="/admin" onClick={closeMenu}>
              {t('admin')}
            </NavLink>
          )}
          {user ? (
            <button 
              type="button" 
              className="btn btn-ghost nav-btn" 
              onClick={() => { logout(); closeMenu() }}
            >
              {t('logout')}
            </button>
          ) : (
            <>
              <NavLink to="/login" onClick={closeMenu}>
                {t('login')}
              </NavLink>
              <NavLink to="/register" className="nav-highlight" onClick={closeMenu}>
                {t('register')}
              </NavLink>
            </>
          )}
        </nav>
      </div>
    </header>
  )
}