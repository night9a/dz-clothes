import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import * as api from '../../api'
import './AdminProducts.css'

const defaultProduct = {
  name_fr: '',
  name_ar: '',
  description_fr: '',
  description_ar: '',
  price: '',
  image_url: '',
  category: '',
  stock: 0,
  options_sizes: '',
  options_colors: '',
  is_active: true,
}

export default function AdminProducts() {
  const { t } = useTranslation()
  const [products, setProducts] = useState([])
  const [error, setError] = useState('')
  const [modal, setModal] = useState(null) // null | 'add' | { id, ...product }
  const [form, setForm] = useState(defaultProduct)
  const [saving, setSaving] = useState(false)

  const load = () => api.adminProducts().then(setProducts).catch((e) => setError(e.message))

  useEffect(() => {
    load()
  }, [])

  const openAdd = () => {
    setForm(defaultProduct)
    setModal('add')
  }
  const openEdit = (p) => {
    setForm({
      name_fr: p.name_fr || '',
      name_ar: p.name_ar || '',
      description_fr: p.description_fr || '',
      description_ar: p.description_ar || '',
      price: p.price ?? '',
      image_url: p.image_url || '',
      category: p.category || '',
      stock: p.stock ?? 0,
      options_sizes: (Array.isArray(p.options_sizes) ? p.options_sizes.join(', ') : p.options_sizes) || '',
      options_colors: (Array.isArray(p.options_colors) ? p.options_colors.join(', ') : p.options_colors) || '',
      is_active: p.is_active !== false,
    })
    setModal({ id: p.id, product: p })
  }
  const closeModal = () => setModal(null)

  const save = async () => {
    setSaving(true)
    try {
      if (modal === 'add') {
        await api.adminCreateProduct({
          ...form,
          price: Number(form.price) || 0,
          stock: Number(form.stock) || 0,
        })
      } else {
        await api.adminUpdateProduct(modal.id, {
          ...form,
          price: form.price !== '' ? Number(form.price) : undefined,
          stock: form.stock !== '' ? Number(form.stock) : undefined,
        })
      }
      closeModal()
      load()
    } catch (e) {
      setError(e.message)
    } finally {
      setSaving(false)
    }
  }

  const remove = async (id) => {
    if (!confirm('Supprimer ce produit ?')) return
    try {
      await api.adminDeleteProduct(id)
      load()
    } catch (e) {
      setError(e.message)
    }
  }

  if (error) return <p className="error-msg">{error}</p>

  return (
    <>
      <h1 className="admin-page-title">{t('adminProducts')}</h1>
      <button type="button" className="btn btn-primary" onClick={openAdd}>{t('add')} {t('adminProducts').toLowerCase()}</button>
      <div className="admin-table-wrap" style={{ marginTop: '1rem' }}>
        <table className="admin-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>{t('name')} (FR)</th>
              <th>{t('price')}</th>
              <th>{t('stock')}</th>
              <th>{t('active')}</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {products.map((p) => (
              <tr key={p.id}>
                <td>{p.id}</td>
                <td>{p.name_fr}</td>
                <td>{Number(p.price).toFixed(0)} DA</td>
                <td>{p.stock}</td>
                <td>{p.is_active ? 'Oui' : 'Non'}</td>
                <td>
                  <div className="admin-actions">
                    <button type="button" className="btn btn-ghost" onClick={() => openEdit(p)}>{t('edit')}</button>
                    <button type="button" className="btn btn-ghost" onClick={() => remove(p.id)}>{t('delete')}</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {products.length === 0 && <p className="empty-state">Aucun produit.</p>}

      {modal && (
        <div className="admin-modal-overlay" onClick={closeModal}>
          <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
            <h3>{modal === 'add' ? t('add') : t('edit')} produit</h3>
            <div className="form-group">
              <label>Nom (FR)</label>
              <input value={form.name_fr} onChange={(e) => setForm({ ...form, name_fr: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Nom (AR)</label>
              <input value={form.name_ar} onChange={(e) => setForm({ ...form, name_ar: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Prix (DA)</label>
              <input type="number" value={form.price} onChange={(e) => setForm({ ...form, price: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Stock</label>
              <input type="number" value={form.stock} onChange={(e) => setForm({ ...form, stock: e.target.value })} />
            </div>
            <div className="form-group">
              <label>URL image</label>
              <input value={form.image_url} onChange={(e) => setForm({ ...form, image_url: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Catégorie</label>
              <input value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} />
            </div>
            <div className="form-group">
              <label>{t('optionsSizes')}</label>
              <input value={form.options_sizes || ''} onChange={(e) => setForm({ ...form, options_sizes: e.target.value })} placeholder="S, M, L, XL" />
            </div>
            <div className="form-group">
              <label>{t('optionsColors')}</label>
              <input value={form.options_colors || ''} onChange={(e) => setForm({ ...form, options_colors: e.target.value })} placeholder="Noir, Blanc, Bleu" />
            </div>
            <div className="form-group">
              <label>
                <input type="checkbox" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} />
                {' '}Actif
              </label>
            </div>
            <div className="admin-modal-actions">
              <button type="button" className="btn btn-primary" onClick={save} disabled={saving}>{t('save')}</button>
              <button type="button" className="btn btn-ghost" onClick={closeModal}>Annuler</button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
