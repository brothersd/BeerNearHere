// src/components/Nav.jsx
import { useState, useEffect, useRef } from 'react'
import { NavLink, useNavigate } from 'react-router'
import { useAuth } from '../context/AuthContext'
import ChangePasswordModal from './ChangePasswordModal'
import styles from './Nav.module.css'

export default function Nav() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const [isChangePasswordModalOpen, setIsChangePasswordModalOpen] = useState(false)
  const dropdownRef = useRef(null)

  const handleLogout = async () => {
    await logout()
    navigate('/auth')
  }

  const handleOpenChangePassword = () => {
    setIsChangePasswordModalOpen(true)
    setIsDropdownOpen(false)
  }

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const toggleDropdown = () => setIsDropdownOpen(!isDropdownOpen)

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
          <NavLink 
            to="/" 
            end 
            className={({ isActive }) => isActive ? styles.active : ''}
          >
            Search
          </NavLink>
          
          {/* New Reviews Link */}
          <NavLink 
            to="/reviews" 
            className={({ isActive }) => isActive ? styles.active : ''}
          >
            Reviews
          </NavLink>

          <NavLink 
            to="/history" 
            className={({ isActive }) => isActive ? styles.active : ''}
          >
            History
          </NavLink>
        </nav>

        {user ? (
          <div className={styles.userInfo} ref={dropdownRef}>
            <button className={styles.usernameDropdown} onClick={toggleDropdown}>
              👤 {user.username} <span className={styles.arrow}>{isDropdownOpen ? '▲' : '▼'}</span>
            </button>
            {isDropdownOpen && (
              <div className={styles.dropdownMenu}>
                <button className={styles.dropdownItem} onClick={handleOpenChangePassword}>
                  Change Password
                </button>
                <button className={styles.dropdownItem} onClick={() => navigate('/settings/delete-account')}>
                  Delete Account
                </button>
                <div className={styles.dropdownDivider}></div>
                <button className={`${styles.dropdownItem} ${styles.signOut}`} onClick={handleLogout}>
                  Sign Out
                </button>
              </div>
            )}
          </div>
        ) : (
          <NavLink to="/auth" className="btn">Sign In</NavLink>
        )}
      </div>

      <ChangePasswordModal 
        isOpen={isChangePasswordModalOpen} 
        onClose={() => setIsChangePasswordModalOpen(false)} 
      />
    </header>
  )
}