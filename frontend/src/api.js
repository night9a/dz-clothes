const API = 'https://dz-clothes-zyae.vercel.app/api/'

function getHeaders(includeAuth = true) {
  const headers = { 'Content-Type': 'application/json' }
  const token = localStorage.getItem('dz_token')
  if (includeAuth && token) headers['Authorization'] = `Bearer ${token}`
  const cartSession = localStorage.getItem('dz_cart_session')
  if (cartSession) headers['X-Cart-Session'] = cartSession
  return headers
}

function ensureCartSession() {
  if (!localStorage.getItem('dz_cart_session')) {
    localStorage.setItem('dz_cart_session', 's_' + Math.random().toString(36).slice(2) + Date.now())
  }
}

export async function register(data) {
  const res = await fetch(`${API}/auth/register`, {
    method: 'POST',
    headers: getHeaders(false),
    body: JSON.stringify({ ...data, lang: localStorage.getItem('dz_lang') || 'fr' }),
  })
  const json = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(json.error || 'Erreur')
  return json
}

export async function login(email, password) {
  const res = await fetch(`${API}/auth/login`, {
    method: 'POST',
    headers: getHeaders(false),
    body: JSON.stringify({ email, password }),
  })
  const json = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(json.error || 'Erreur')
  return json
}

export async function loginGoogle(credential) {
  const res = await fetch(`${API}/auth/google`, {
    method: 'POST',
    headers: getHeaders(false),
    body: JSON.stringify({ credential }),
  })
  const json = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(json.error || 'Erreur')
  return json
}

export async function verifyEmail(token) {
  const res = await fetch(`${API}/auth/verify-email`, {
    method: 'POST',
    headers: getHeaders(false),
    body: JSON.stringify({ token }),
  })
  const json = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(json.error || 'Erreur')
  return json
}

export async function me() {
  const res = await fetch(`${API}/auth/me`, { headers: getHeaders() })
  if (res.status === 401) return null
  const json = await res.json().catch(() => ({}))
  return json.user || null
}

export async function getProducts(params = {}) {
  const q = new URLSearchParams({ lang: localStorage.getItem('dz_lang') || 'fr', ...params })
  const res = await fetch(`${API}/products?${q}`)
  const json = await res.json().catch(() => [])
  return Array.isArray(json) ? json : []
}

export async function getProduct(id) {
  const res = await fetch(`${API}/products/${id}?lang=${localStorage.getItem('dz_lang') || 'fr'}`)
  if (!res.ok) return null
  return res.json()
}

export async function getCart() {
  ensureCartSession()
  const res = await fetch(`${API}/cart?lang=${localStorage.getItem('dz_lang') || 'fr'}`, { headers: getHeaders() })
  const json = await res.json().catch(() => [])
  return Array.isArray(json) ? json : []
}

export async function addToCart(productId, quantity = 1, optionSize = '', optionColor = '') {
  ensureCartSession()
  const res = await fetch(`${API}/cart`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({
      product_id: productId,
      quantity,
      option_size: optionSize || undefined,
      option_color: optionColor || undefined,
      cart_session: localStorage.getItem('dz_cart_session'),
    }),
  })
  const json = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(json.error || 'Erreur')
  return json
}

export async function updateCartItem(itemId, quantity) {
  const res = await fetch(`${API}/cart/${itemId}`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify({ quantity }),
  })
  if (!res.ok) throw new Error('Erreur')
  return res.json()
}

export async function removeCartItem(itemId) {
  const res = await fetch(`${API}/cart/${itemId}`, { method: 'DELETE', headers: getHeaders() })
  if (!res.ok) throw new Error('Erreur')
  return res.json()
}

export async function validateDiscount(code, subtotal) {
  const res = await fetch(`${API}/discount/validate`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ code, subtotal }),
  })
  const json = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(json.error || 'Code invalide')
  return json
}

export async function checkout(payload) {
  const res = await fetch(`${API}/checkout`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ ...payload, cart_session: localStorage.getItem('dz_cart_session') }),
  })
  const json = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(json.error || 'Erreur')
  return json
}

// Admin
export async function adminStats() {
  const res = await fetch(`${API}/admin/stats`, { headers: getHeaders() })
  if (!res.ok) throw new Error('Non autorisé')
  return res.json()
}

export async function adminOrders() {
  const res = await fetch(`${API}/admin/orders`, { headers: getHeaders() })
  if (!res.ok) throw new Error('Non autorisé')
  return res.json()
}

export async function adminOrderDetail(id) {
  const res = await fetch(`${API}/admin/orders/${id}`, { headers: getHeaders() })
  if (!res.ok) throw new Error('Non autorisé')
  return res.json()
}

export async function adminUpdateOrderStatus(id, status) {
  const res = await fetch(`${API}/admin/orders/${id}/status`, {
    method: 'PATCH',
    headers: getHeaders(),
    body: JSON.stringify({ status }),
  })
  if (!res.ok) throw new Error('Erreur')
  return res.json()
}

export async function adminProducts() {
  const res = await fetch(`${API}/admin/products`, { headers: getHeaders() })
  if (!res.ok) throw new Error('Non autorisé')
  return res.json()
}

export async function adminCreateProduct(data) {
  const res = await fetch(`${API}/admin/products`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error((await res.json().catch(() => ({}))).error || 'Erreur')
  return res.json()
}

export async function adminUpdateProduct(id, data) {
  const res = await fetch(`${API}/admin/products/${id}`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Erreur')
  return res.json()
}

export async function adminDeleteProduct(id) {
  const res = await fetch(`${API}/admin/products/${id}`, { method: 'DELETE', headers: getHeaders() })
  if (!res.ok) throw new Error('Erreur')
  return res.json()
}

export async function adminDiscounts() {
  const res = await fetch(`${API}/admin/discounts`, { headers: getHeaders() })
  if (!res.ok) throw new Error('Non autorisé')
  return res.json()
}

export async function adminCreateDiscount(data) {
  const res = await fetch(`${API}/admin/discounts`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error((await res.json().catch(() => ({}))).error || 'Erreur')
  return res.json()
}

export async function adminUpdateDiscount(id, data) {
  const res = await fetch(`${API}/admin/discounts/${id}`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Erreur')
  return res.json()
}

export async function adminDeleteDiscount(id) {
  const res = await fetch(`${API}/admin/discounts/${id}`, { method: 'DELETE', headers: getHeaders() })
  if (!res.ok) throw new Error('Erreur')
  return res.json()
}

export async function adminTelegramGet() {
  const res = await fetch(`${API}/admin/settings/telegram`, { headers: getHeaders() })
  if (!res.ok) throw new Error('Non autorisé')
  return res.json()
}

export async function adminTelegramSet(telegramChatId) {
  const res = await fetch(`${API}/admin/settings/telegram`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ telegram_chat_id: telegramChatId }),
  })
  if (!res.ok) throw new Error('Erreur')
  return res.json()
}
