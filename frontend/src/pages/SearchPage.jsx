import { useState } from 'react'
import { useNavigate } from 'react-router'
import { searchProducts } from '../api/client'
import styles from './SearchPage.module.css'

const PACK_SIZES = [
  { label: 'Any Size', value: '' },
  { label: 'Single', value: 'single' },
  { label: '6 Pack', value: '6 pack' },
  { label: '12 Pack', value: '12 pack' },
  { label: '15 Pack', value: '15 pack' },
  { label: '18 Pack', value: '18 pack' },
  { label: '24 Pack', value: '24 pack' },
  { label: '30 Pack', value: '30 pack' },
  { label: '36 Pack', value: '36 pack' },
]

export default function SearchPage() {
  const [zipCode, setZipCode] = useState('')
  const [productName, setProductName] = useState('')
  const [packSize, setPackSize] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!zipCode || !productName) return
    setLoading(true)
    setError('')
    try {
      const res = await searchProducts(zipCode, productName, packSize)
      navigate('/results', { state: { results: res.data.results, zipCode, productName, packSize } })
    } catch (err) {
      setError('Failed to fetch results. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className={styles.main}>
      <div className={styles.hero}>
        <div className={styles.heroText}>
          <h1 className={styles.headline}>Find Your Beer.</h1>
          <h1 className={styles.headline2}>Find the Price.</h1>
          <p className={styles.sub}>
            Compare beer prices at Kroger and Walmart near you.<br />
            Enter your zip code and we'll do the legwork.
          </p>
        </div>
        <div className={styles.foamDecor}>🍺</div>
      </div>

      <div className={`card ${styles.formCard}`}>
        <div className={styles.chalkLabel}>Search For Beer Near Here</div>
        <form onSubmit={handleSearch} className={styles.form}>
          <div className={styles.field}>
            <label className={styles.label}>Zip Code</label>
            <input
              className="input"
              type="text"
              placeholder="e.g. 80918"
              maxLength={5}
              value={zipCode}
              onChange={e => setZipCode(e.target.value.replace(/\D/g, ''))}
              required
            />
          </div>
          <div className={styles.field}>
            <label className={styles.label}>What are you looking for?</label>
            <input
              className="input"
              type="text"
              placeholder="e.g. Pabst, IPA, Corona..."
              value={productName}
              onChange={e => setProductName(e.target.value)}
              required
            />
          </div>
          <div className={styles.field}>
            <label className={styles.label}>Pack Size</label>
            <select
              className={`input ${styles.select}`}
              value={packSize}
              onChange={e => setPackSize(e.target.value)}
            >
              {PACK_SIZES.map(size => (
                <option key={size.value} value={size.value}>
                  {size.label}
                </option>
              ))}
            </select>
          </div>
          <button className="btn" type="submit" disabled={loading}>
            {loading ? 'Searching...' : 'Find My Beer'}
          </button>
        </form>
        {loading && <div className="spinner" />}
        {error && <p className={styles.error}>{error}</p>}
      </div>

      <div className={styles.stores}>
        <span className="badge">Kroger</span>
        <span className={styles.storesSep}>✦</span>
        <span className="badge">King Soopers</span>
        <span className={styles.storesSep}>✦</span>
        <span className="badge">Walmart</span>
      </div>
    </main>
  )
}