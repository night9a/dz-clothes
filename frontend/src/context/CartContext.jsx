import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import * as api from '../api'

const CartContext = createContext(null)

export function CartProvider({ children }) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)

  const refresh = useCallback(() => {
    setLoading(true)
    api.getCart().then(setItems).finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  const addToCart = async (productId, quantity = 1, optionSize = '', optionColor = '') => {
    await api.addToCart(productId, quantity, optionSize, optionColor)
    refresh()
  }

  const updateQuantity = async (itemId, quantity) => {
    await api.updateCartItem(itemId, quantity)
    refresh()
  }

  const removeItem = async (itemId) => {
    await api.removeCartItem(itemId)
    refresh()
  }

  const total = items.reduce((sum, i) => sum + i.price * i.quantity, 0)
  const count = items.reduce((sum, i) => sum + i.quantity, 0)

  return (
    <CartContext.Provider value={{ items, loading, total, count, addToCart, updateQuantity, removeItem, refresh }}>
      {children}
    </CartContext.Provider>
  )
}

export function useCart() {
  const ctx = useContext(CartContext)
  if (!ctx) throw new Error('useCart must be used within CartProvider')
  return ctx
}
