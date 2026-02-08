import { Outlet } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import Header from './Header'
import Footer from './Footer'

export default function Layout() {
  return (
    <>
      <Header />
      <main style={{ minHeight: 'calc(100vh - 140px)' }}>
        <Outlet />
      </main>
      <Footer />
    </>
  )
}
