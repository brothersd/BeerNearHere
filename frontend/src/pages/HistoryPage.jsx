import { useState, useEffect } from 'react'
import api from '../api/client'
import styles from './HistoryPage.module.css'

export default function HistoryPage() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filter, setFilter] = useState('')
  const [zipFilter, setZipFilter] = useState('')

  useEffect(() => {
    api.get('/products/')
      .then(res => setProducts(res.data.results || res.data))
      .catch(() => setError('Could not load history. Is the backend running?'))
      .finally(() => setLoading(false))
  }, [])

  const filtered = products.filter(p => {
    const matchName = p.name?.toLowerCase().includes(filter.toLowerCase())
    const matchZip = zipFilter ? p.zip_code?.includes(zipFilter) : true
    return matchName && matchZip
  })

  // Group by zip code
  const grouped = filtered.reduce((acc, p) => {
    const key = p.zip_code || 'Unknown'
    if (!acc[key]) acc[key] = []
    acc[key].push(p)
    return acc
  }, {})

  return (
    <main className={styles.main}>
      <h2 className={styles.title}>Price History</h2>
      <p className={styles.subtitle}>All products saved across your searches</p>

      <div className="divider">✦</div>

      <div className={styles.filters}>
        <input
          className="input"
          placeholder="Filter by product name..."
          value={filter}
          onChange={e => setFilter(e.target.value)}
        />
        <input
          className="input"
          placeholder="Filter by zip code..."
          maxLength={5}
          value={zipFilter}
          onChange={e => setZipFilter(e.target.value.replace(/\D/g, ''))}
        />
      </div>

      {loading && <div className="spinner" />}
      {error && <p className={styles.error}>{error}</p>}

      {!loading && !error && filtered.length === 0 && (
        <div className={`card ${styles.empty}`}>
          <p>No price history yet. Run a search to get started.</p>
        </div>
      )}

      {Object.entries(grouped).map(([zip, items]) => (
        <div key={zip} className={styles.group}>
          <div className={styles.groupHeader}>
            <span className="badge">📍 {zip}</span>
            <span className={styles.groupCount}>{items.length} products</span>
          </div>
          <div className={styles.table}>
            <div className={styles.tableHeader}>
              <span>Product</span>
              <span>Store</span>
              <span>Price</span>
              <span>Updated</span>
            </div>
            {items
              .sort((a, b) => parseFloat(a.price) - parseFloat(b.price))
              .map((p, i) => (
                <div key={p.id} className={`${styles.tableRow} fade-up`} style={{ animationDelay: `${i * 0.03}s` }}>
                  <span className={styles.productName}>
                    {p.product_url
                      ? <a href={p.product_url} target="_blank" rel="noopener noreferrer">{p.name}</a>
                      : p.name
                    }
                  </span>
                  <span className={styles.storeName}>{p.store_name}</span>
                  <span className={styles.price}>${parseFloat(p.price).toFixed(2)}</span>
                  <span className={styles.date}>
                    {new Date(p.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  </span>
                </div>
              ))}
          </div>
        </div>
      ))}
    </main>
  )
}
