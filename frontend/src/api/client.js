import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

export const searchProducts = (zip_code, product_name, pack_size = '') =>
  api.post('/search/', { zip_code, product_name, pack_size })

export const getHistory = (zip_code, product_name) =>
  api.get('/history/', { params: { zip_code, product_name } })

export default api