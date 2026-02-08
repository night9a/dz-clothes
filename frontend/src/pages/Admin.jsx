import { Routes, Route, NavLink } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import AdminDashboard from './admin/AdminDashboard'
import AdminOrders from './admin/AdminOrders'
import AdminProducts from './admin/AdminProducts'
import AdminDiscounts from './admin/AdminDiscounts'
import AdminSettings from './admin/AdminSettings'
import './Admin.css'

export default function Admin() {
  const { t } = useTranslation()

  return (
    <div className="admin-layout">
      <aside className="admin-sidebar">
        <nav>
          <NavLink to="/admin" end>{t('adminDashboard')}</NavLink>
          <NavLink to="/admin/orders">{t('adminOrders')}</NavLink>
          <NavLink to="/admin/products">{t('adminProducts')}</NavLink>
          <NavLink to="/admin/discounts">{t('adminDiscounts')}</NavLink>
          <NavLink to="/admin/settings">{t('adminSettings')}</NavLink>
        </nav>
      </aside>
      <div className="admin-main">
        <Routes>
          <Route index element={<AdminDashboard />} />
          <Route path="orders" element={<AdminOrders />} />
          <Route path="products" element={<AdminProducts />} />
          <Route path="discounts" element={<AdminDiscounts />} />
          <Route path="settings" element={<AdminSettings />} />
        </Routes>
      </div>
    </div>
  )
}
