// src/components/ReviewModal.jsx
import { useState } from 'react'
import api from '../api/client'
import styles from './ReviewModal.module.css'

export default function ReviewModal({ productId, isOpen, onClose, onReviewSubmit }) {
  const [rating, setRating] = useState(0)
  const [content, setContent] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  if (!isOpen) return null

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (rating === 0) {
      setError('Please select a rating')
      return
    }
    
    if (!content.trim()) {
      setError('Review content is required')
      return
    }

    setIsSubmitting(true)
    setError('')
    
    try {
      // POST request using the centralized API client
      const response = await api.post(`/products/${productId}/reviews/`, {
        rating,
        content: content.trim() // Key must match the 'content' field in the model
      })

      // Update the parent component with the new review data
      onReviewSubmit(response.data)
      
      setRating(0)
      setContent('')
      onClose()
    } catch (err) {
      if (err.response?.status === 401) {
        setError('Your session has expired. Please log in again.')
      } else if (err.response?.data) {
        // Extract specific validation errors from Django
        const serverError = err.response.data.content || err.response.data.rating || err.response.data.error
        setError(serverError || 'Invalid review data. Please check your input.')
      } else {
        setError('An error occurred while submitting your review.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleRatingClick = (value) => {
    setRating(value)
  }

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={e => e.stopPropagation()}>
        <h2 className={styles.title}>Submit a Review</h2>
        
        <form onSubmit={handleSubmit}>
          <div className={styles.ratingSection}>
            <label className={styles.label}>Rating *</label>
            <div className={styles.stars}>
              {[1, 2, 3, 4, 5].map((star) => (
                <span
                  key={star}
                  className={`${styles.star} ${star <= rating ? styles.filled : ''}`}
                  onClick={() => handleRatingClick(star)}
                >
                  ★
                </span>
              ))}
            </div>
          </div>

          <div className={styles.contentSection}>
            <label className={styles.label}>Your Review *</label>
            <textarea
              className={styles.textarea}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="How was the beer?"
              rows="4"
              required
            />
          </div>

          {error && <p className={styles.error}>{error}</p>}

          <div className={styles.buttonGroup}>
            <button
              type="button"
              className="btn secondary"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Submitting...' : 'Submit Review'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}