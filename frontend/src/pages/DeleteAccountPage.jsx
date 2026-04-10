// src/pages/DeleteAccountPage.jsx
import { useState } from 'react'
import { useNavigate } from 'react-router'
import { useAuth } from '../context/AuthContext'
import api from '../api/client'
import styles from './DeleteAccountPage.module.css'

export default function DeleteAccountPage() {
  const [isDeleting, setIsDeleting] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const { logout } = useAuth()

  const handleDeleteAccount = async () => {
    if (!window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      return
    }

    setIsDeleting(true)
    setError('')

    try {
      await api.delete('/auth/delete-account/')
      
      // Clear authentication tokens from localStorage
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      
      // Logout the user
      await logout()
      
      // Redirect to login page
      navigate('/auth')
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to delete account. Please try again.')
      setIsDeleting(false)
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        <div className={styles.card}>
          <h2>Delete Account</h2>
          
          <p className={styles.warning}>
            Warning: This action will permanently delete your account and all associated data.
          </p>
          
          <p className={styles.description}>
            If you proceed, your username and password will be removed from our system.
            You will need to create a new account if you wish to use the service again.
          </p>

          {error && <p className={styles.error}>{error}</p>}

          <div className={styles.buttonGroup}>
            <button
              className={`${styles.deleteButton} btn`}
              onClick={handleDeleteAccount}
              disabled={isDeleting}
            >
              {isDeleting ? 'Deleting...' : 'Delete Account'}
            </button>
            
            <button
              className={`${styles.cancelButton} btn`}
              onClick={() => navigate('/')}
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}