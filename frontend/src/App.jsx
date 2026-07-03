import { useState, useEffect } from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import axios from 'axios'
import Browse from './pages/Browse'
import FileDetail from './pages/FileDetail'
import Upload from './pages/Upload'
import Dashboard from './pages/Dashboard'

const API = axios.create({ baseURL: '/api/v1' })

API.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export { API }

export default function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      API.get('/auth/me')
        .then((res) => setUser(res.data))
        .catch(() => localStorage.removeItem('access_token'))
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  return (
    <div className="min-h-screen bg-gray-950">
      <nav className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-8">
              <Link to="/" className="text-xl font-bold text-cyan-400">AgentMarket</Link>
              <div className="hidden md:flex gap-6">
                <Link to="/" className="text-sm text-gray-300 hover:text-white transition">Browse</Link>
                <Link to="/upload" className="text-sm text-gray-300 hover:text-white transition">Upload</Link>
              </div>
            </div>
            <div className="flex items-center gap-4">
              {user ? (
                <>
                  <span className="text-sm text-cyan-400">{user.wallet_balance.toFixed(0)} tokens</span>
                  <Link to="/dashboard" className="text-sm text-gray-300 hover:text-white transition">
                    {user.display_name || user.email}
                  </Link>
                </>
              ) : (
                <Link to="/dashboard" className="text-sm bg-cyan-600 hover:bg-cyan-500 text-white px-4 py-2 rounded-lg transition">
                  Sign In
                </Link>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          <Route path="/" element={<Browse API={API} />} />
          <Route path="/files/:id" element={<FileDetail API={API} user={user} />} />
          <Route path="/upload" element={<Upload API={API} user={user} />} />
          <Route path="/dashboard" element={<Dashboard API={API} user={user} onAuth={setUser} />} />
        </Routes>
      </main>
    </div>
  )
}
