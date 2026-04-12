import { useLocation, useNavigate } from 'react-router'
import { useState } from 'react'
import styles from './ResultsPage.module.css'
import ReviewModal from '../components/ReviewModal'

const STORE_COLORS = {
  Walmart: '#0071CE',
  'King Soopers': '#E31837',
  Kroger: '#E31837',
}

function getStoreColor(storeName) {
  for (const [key, color] of Object.entries(STORE_COLORS)) {
    if (storeName?.toLowerCase().includes(key.toLowerCase())) return color
  }
  return '#C97B2A'
}

export default function ResultsPage() {
  const { state } = useLocation()
  const navigate = useNavigate()
  const [showReviewModal, setShowReviewModal] = useState(false)
  const [selectedProductId, setSelectedProductId] = useState(null)

  if (!state?.results) {
    navigate('/')
    return null
  }

  const { results, zipCode, productName, packSize } = state
  const cheapest = results[0]

  const subtitle = [
    `Near zip code ${zipCode}`,
    packSize ? `${packSize}s only` : null,
    `${results.length} products found`,
  ].filter(Boolean).join(' · ')

  const handleOpenReviewModal = (productId) => {
    setSelectedProductId(productId)
    setShowReviewModal(true)
  }

  const handleCloseReviewModal = () => {
    setShowReviewModal(false)
    setSelectedProductId(null)
  }

  const handleReviewSubmit = () => {
    // Refresh the page to show updated reviews
    window.location.reload()
  }

  return (
    <main className={styles.main}>
      {showReviewModal && (
        <ReviewModal
          productId={selectedProductId}
          isOpen={showReviewModal}
          onClose={handleCloseReviewModal}
          onReviewSubmit={handleReviewSubmit}
        />
      )}
      
      <div className={styles.header}>
        <div>
          <p className={styles.breadcrumb}>
            <button className={styles.back} onClick={() => navigate('/')}>← New Search</button>
          </p>
          <h2 className={styles.title}>
            Results for <em>"{productName}"</em>
          </h2>
          <p className={styles.subtitle}>{subtitle}</p>
        </div>
        {cheapest && (
          <div className={styles.bestDeal}>
            <div className={styles.bestLabel}>Best Price</div>
            <div className={styles.bestPrice}>${parseFloat(cheapest.price).toFixed(2)}</div>
            <div className={styles.bestStore}>{cheapest.store_name}</div>
          </div>
        )}
      </div>

      <div className="divider">✦</div>

      {results.length === 0 ? (
        <div className={`card ${styles.empty}`}>
          <p>No products found. Try a different search term, zip code, or pack size.</p>
        </div>
      ) : (
        <div className={styles.grid}>
          {results.map((product, i) => (
            <div
              key={product.id}
              className={`card ${styles.productCard} fade-up`}
              style={{ animationDelay: `${i * 0.06}s` }}
            >
              <div className={styles.rank}>#{i + 1}</div>
              <div
                className={styles.storeTag}
                style={{ borderColor: getStoreColor(product.store_name), color: getStoreColor(product.store_name) }}
              >
                {product.store_name}
              </div>
              <div className={styles.productName}>{product.name}</div>
              <div className={styles.price}>${parseFloat(product.price).toFixed(2)}</div>
              {product.product_url && (
                <a
                  href={product.product_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={styles.link}
                >
                  View Product →
                </a>
              )}
              <button
                className={`btn ${styles.reviewButton}`}
                onClick={() => handleOpenReviewModal(product.id)}
              >
                Review This Beer
              </button>
              {i === 0 && <div className={styles.cheapestBadge}>🏆 Cheapest</div>}
            </div>
          ))}
        </div>
      )}
    </main>
  )
}