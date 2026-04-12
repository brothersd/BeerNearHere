import { useEffect, useState } from 'react'
import api from '../api/client'
import styles from './ReviewsPage.module.css'
import { useAuth } from '../context/AuthContext'

export default function ReviewsPage() {
  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(true)
  
  // 👇 Get current user from AuthContext
  const { user } = useAuth()

  useEffect(() => {
    const fetchReviews = async () => {
      try {
        const res = await api.get('/all-reviews/')
        setReviews(res.data)
      } catch (err) {
        console.error('Failed to fetch reviews:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchReviews()
  }, [])

  // 👇 Delete Logic
  const handleDelete = async (reviewId) => {
    if (!window.confirm('Are you sure you want to delete this review?')) return
    
    try {
      await api.delete(`/reviews/${reviewId}/`)
      // Remove the deleted review from the UI instantly
      setReviews(prev => prev.filter(r => r.id !== reviewId))
    } catch (err) {
      console.error('Delete failed:', err)
      alert(err.response?.data?.error || 'Failed to delete review.')
    }
  }

  if (loading) return <div className="spinner" />

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Community Beer Reviews</h1>
      
      <div className={styles.grid}>
        {reviews.length === 0 ? (
          <p>No reviews have been submitted yet. Be the first!</p>
        ) : (
          reviews.map(review => (
            <div key={review.id} className={styles.card}>
              <div className={styles.header}>
                <span className={styles.productName}>{review.product_name || 'Unknown Beer'}</span>
                <span className={styles.stars}>
                  {'★'.repeat(review.rating)}{'☆'.repeat(5 - review.rating)}
                </span>
              </div>
              
              <p className={styles.content}>"{review.content}"</p>
              
              <div className={styles.footer}>
                <span>— {review.username || 'Anonymous'}</span>
                <span>{new Date(review.created_at).toLocaleDateString()}</span>
              </div>

              {/* 👇 DELETE BUTTON: Only renders if current user is the author */}
              {user && review.username === user.username && (
                <button
                  onClick={() => handleDelete(review.id)}
                  style={{
                    marginTop: '0.75rem',
                    background: 'none',
                    border: '1px solid rgba(255, 107, 107, 0.3)',
                    color: '#ff6b6b',
                    cursor: 'pointer',
                    padding: '0.5rem 0.8rem',
                    borderRadius: '4px',
                    fontSize: '0.85rem',
                    width: '100%',
                    transition: 'all 0.2s',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '6px'
                  }}
                  onMouseEnter={(e) => e.target.style.background = 'rgba(255, 107, 107, 0.1)'}
                  onMouseLeave={(e) => e.target.style.background = 'none'}
                >
                  🗑️ Delete Review
                </button>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}