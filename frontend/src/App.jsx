// src/App.jsx
import { Routes, Route, Navigate } from 'react-router'
import { AuthProvider, useAuth } from './context/AuthContext'
import Nav from './components/Nav'
import SearchPage from './pages/SearchPage'
import ResultsPage from './pages/ResultsPage'
import HistoryPage from './pages/HistoryPage'
import ReviewsPage from './pages/ReviewsPage' // New Page
import AuthPage from './pages/AuthPage'
import DeleteAccountPage from './pages/DeleteAccountPage'
import './App.css'

/**
 * A wrapper component that redirects users to /auth 
 * if they try to access a private page while logged out.
 */
function PrivateRoute({ children }) {
  const { user, loading } = useAuth()
  
  if (loading) return <div className="loader">Loading...</div>
  return user ? children : <Navigate to="/auth" />
}

function AppRoutes() {
  return (
    <div className="app-container">
      <Nav />
      <main className="main-content">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<SearchPage />} />
          <Route path="/results" element={<ResultsPage />} />
          <Route path="/auth" element={<AuthPage />} />
          <Route path="/reviews" element={<ReviewsPage />} />

          {/* Protected Routes */}
          <Route 
            path="/history" 
            element={
              <PrivateRoute>
                <HistoryPage />
              </PrivateRoute>
            } 
          />
          <Route 
            path="/settings/delete-account" 
            element={
              <PrivateRoute>
                <DeleteAccountPage />
              </PrivateRoute>
            } 
          />

          {/* Catch-all redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  )
}