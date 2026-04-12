import { useEffect, useState } from 'react'
import api from '../api/client'

export default function AllReviews() {
  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/products/all-reviews/')
      .then(res => setReviews(res.data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="container">Loading reviews...</div>

  return (
    <div className="container">
      <h1>Community Beer Reviews</h1>
      <div className="reviews-grid">
        {reviews.map(review => (
          <div key={review.id} className="review-card">
            <h3>{review.product_name}</h3> {/* Ensure your serializer includes product_name */}
            <div className="rating">{'★'.repeat(review.rating)}</div>
            <p>"{review.content}"</p>
            <small>By {review.username} on {new Date(review.created_at).toLocaleDateString()}</small>
          </div>
        ))}
      </div>
    </div>
  )
}