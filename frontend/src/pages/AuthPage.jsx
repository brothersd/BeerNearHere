// src/pages/AuthPage.jsx
import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import styles from './AuthPage.module.css'

export default function AuthPage() {
  const [mode, setMode] = useState('login')  // 'login' | 'register'
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const { login, register, loading, error, setError } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (mode === 'login') {
      await login(username, password)
    } else {
      await register(username, password)
    }
  }

  const switchMode = (newMode) => {
    setMode(newMode)
    setError('')
    setUsername('')
    setPassword('')
  }

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        <div className={styles.logo}>
          <span className={styles.mug}>🍺</span>
          <h1 className={styles.title}>Beer Near Here</h1>
          <p className={styles.tagline}>Find the cheapest pint in town</p>
        </div>

        <div className={styles.card}>
          <div className={styles.tabs}>
            <button
              className={`${styles.tab} ${mode === 'login' ? styles.activeTab : ''}`}
              onClick={() => switchMode('login')}
            >
              Sign In
            </button>
            <button
              className={`${styles.tab} ${mode === 'register' ? styles.activeTab : ''}`}
              onClick={() => switchMode('register')}
            >
              Sign Up
            </button>
          </div>

          <form onSubmit={handleSubmit} className={styles.form}>
            <div className={styles.field}>
              <label className={styles.label}>Username</label>
              <input
                className="input"
                type="text"
                placeholder="your_username"
                value={username}
                onChange={e => setUsername(e.target.value)}
                autoComplete="username"
                required
              />
            </div>

            <div className={styles.field}>
              <label className={styles.label}>Password</label>
              <input
                className="input"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={e => setPassword(e.target.value)}
                autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                required
              />
            </div>

            {error && <p className={styles.error}>{error}</p>}

            <button className="btn" type="submit" disabled={loading}>
              {loading ? 'Please wait...' : mode === 'login' ? 'Sign In' : 'Create Account'}
            </button>
          </form>

          <div className={styles.chalkNote}>
            {mode === 'login'
              ? "Don't have an account? Click Sign Up above."
              : 'Already have an account? Click Sign In above.'}
          </div>
        </div>

        <div className={styles.stores}>
          <span className="badge">Kroger</span>
          <span style={{ color: 'var(--amber)', opacity: 0.4, fontSize: '0.7rem' }}>✦</span>
          <span className="badge">King Soopers</span>
          <span style={{ color: 'var(--amber)', opacity: 0.4, fontSize: '0.7rem' }}>✦</span>
          <span className="badge">Walmart</span>
        </div>
      </div>
    </div>
  )
}
