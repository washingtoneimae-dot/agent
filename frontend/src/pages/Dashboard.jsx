import { useState } from 'react'

export default function Dashboard({ API, user, onAuth }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [isRegister, setIsRegister] = useState(false)
  const [error, setError] = useState('')

  if (!user) {
    const handleAuth = async (e) => {
      e.preventDefault(); setError('')
      try {
        const endpoint = isRegister ? '/auth/register' : '/auth/login'
        const body = isRegister ? { email, password, display_name: displayName } : { email, password }
        const res = await API.post(endpoint, body)
        localStorage.setItem('access_token', res.data.access_token)
        localStorage.setItem('refresh_token', res.data.refresh_token)
        const me = await API.get('/auth/me')
        onAuth(me.data)
      } catch (err) { setError(err.response?.data?.detail || 'Authentication failed') }
    }

    return (
      <div className="max-w-md mx-auto mt-12">
        <h1 className="text-3xl font-bold text-white mb-6">Sign In</h1>
        <form onSubmit={handleAuth} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Email</label>
            <input type="email" required value={email} onChange={e => setEmail(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-cyan-500" />
          </div>
          {isRegister && (
            <div>
              <label className="block text-sm text-gray-400 mb-1">Display Name</label>
              <input type="text" value={displayName} onChange={e => setDisplayName(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-cyan-500" />
            </div>
          )}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Password</label>
            <input type="password" required minLength={6} value={password} onChange={e => setPassword(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-cyan-500" />
          </div>
          {error && <div className="text-red-400 text-sm">{error}</div>}
          <button type="submit" className="w-full bg-cyan-600 hover:bg-cyan-500 text-white px-4 py-3 rounded-lg font-medium transition">
            {isRegister ? 'Create Account' : 'Sign In'}
          </button>
          <button type="button" onClick={() => setIsRegister(!isRegister)} className="text-sm text-cyan-400 hover:text-cyan-300">
            {isRegister ? 'Already have an account? Sign in' : 'New user? Create account'}
          </button>
        </form>
      </div>
    )
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token'); localStorage.removeItem('refresh_token'); onAuth(null)
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <button onClick={handleLogout} className="text-sm text-gray-400 hover:text-white transition">Sign Out</button>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-6">
        <h2 className="text-lg font-semibold text-white mb-4">Account</h2>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between"><span className="text-gray-400">Email</span><span className="text-white">{user.email}</span></div>
          <div className="flex justify-between"><span className="text-gray-400">Display Name</span><span className="text-white">{user.display_name}</span></div>
          <div className="flex justify-between"><span className="text-gray-400">Wallet</span><span className="text-cyan-400 font-bold">{user.wallet_balance.toFixed(0)} tokens</span></div>
          <div className="flex justify-between"><span className="text-gray-400">Reputation</span><span className="text-white">{user.reputation_score.toFixed(1)}</span></div>
        </div>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-2">Buy Tokens</h2>
        <p className="text-sm text-gray-400 mb-4">Demo mode — tokens credited instantly.</p>
        <div className="grid grid-cols-3 gap-3">
          {[{id:'starter',name:'Starter',tokens:500,price:4.99},{id:'builder',name:'Builder',tokens:2000,price:17.99},{id:'pro',name:'Pro',tokens:10000,price:79.99}].map(pack => (
            <button key={pack.id} onClick={async () => {
              const res = await API.post('/tokens/purchase', { pack: pack.id })
              onAuth({...user, wallet_balance: res.data.new_balance})
            }} className="bg-gray-800 border border-gray-700 hover:border-cyan-700 rounded-lg p-4 text-center transition">
              <div className="text-lg font-bold text-white">{pack.tokens.toLocaleString()}</div>
              <div className="text-xs text-gray-400">{pack.name}</div>
              <div className="text-sm text-cyan-400 font-medium mt-1">${pack.price}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
