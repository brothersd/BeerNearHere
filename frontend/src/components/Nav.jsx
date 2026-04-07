// src/components/Nav.jsx
import { NavLink, useNavigate } from 'react-router'
import { useAuth } from '../context/AuthContext'
import styles from './Nav.module.css'

export default function Nav() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/auth')
  }

  return (
    <header className={styles.header}>
      <NavLink to="/" className={styles.logo}>
        <span className={styles.mug}>🍺</span>
        <div>
          <div className={styles.title}>Beer Near Here</div>
          <div className={styles.tagline}>Find the cheapest pint in town</div>
        </div>
      </NavLink>

      <div className={styles.right}>
        <nav className={styles.nav}>
          <NavLink to="/" end className={({ isActive }) => isActive ? styles.active : ''}>Search</NavLink>
          <NavLink to="/history" className={({ isActive }) => isActive ? styles.active : ''}>History</NavLink>
        </nav>
        <div className={styles.userInfo}>
          <span className={styles.username}>👤 {user?.username}</span>
          <button className={styles.signOut} onClick={handleLogout}>Sign Out</button>
        </div>
      </div>
    </header>
  )
}
