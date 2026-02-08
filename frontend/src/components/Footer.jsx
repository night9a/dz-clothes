import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import './Footer.css'

const INSTAGRAM_URL = 'https://www.instagram.com/mosho_tenx/'

export default function Footer() {
  const { t } = useTranslation()

  return (
    <footer className="footer">
      <div className="container footer-inner">
        <div className="footer-links">
          <Link to="/">{t('home')}</Link>
          <Link to="/shop">{t('shop')}</Link>
          <Link to="/cart">{t('cart')}</Link>
        </div>
        <p className="footer-credit">
          {t('createdBy')}{' '}
          <a href={INSTAGRAM_URL} target="_blank" rel="noopener noreferrer" className="credit-link" aria-label="Instagram mosho">
            mosho
          </a>
        </p>
      </div>
    </footer>
  )
}
