import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'

export default function FileDetail({ API, user }) {
  const { id } = useParams()
  const navigate = useNavigate()
  const [file, setFile] = useState(null)
  const [summary, setSummary] = useState(null)
  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(true)
  const [downloading, setDownloading] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    Promise.all([
      API.get(`/files/${id}`),
      API.get(`/reviews/${id}/summary`),
      API.get(`/reviews/${id}`),
    ])
      .then(([f, s, r]) => { setFile(f.data); setSummary(s.data); setReviews(r.data) })
      .catch(() => navigate('/'))
      .finally(() => setLoading(false))
  }, [id])

  const handleDownload = async () => {
    if (!user) { setMessage('Sign in to download files'); return }
    setDownloading(true); setMessage('')
    try {
      const res = await API.post(`/files/${id}/download`)
      setMessage(`Downloaded! Spent ${res.data.tokens_spent} tokens.`)
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Download failed')
    }
    setDownloading(false)
  }

  if (loading) return <div className="text-center text-gray-400 py-12">Loading...</div>
  if (!file) return <div className="text-center text-gray-400 py-12">File not found</div>

  const summaryData = summary?.summary_json || null

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 mb-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="flex gap-2 mb-2">
              <span className="text-xs font-medium bg-gray-800 text-cyan-400 px-2 py-1 rounded">{file.category.replace('_', ' ')}</span>
              <span className="text-xs font-medium bg-gray-800 text-purple-400 px-2 py-1 rounded">{file.product_tier.replace(/_/g, ' ')}</span>
            </div>
            <h1 className="text-3xl font-bold text-white">{file.title}</h1>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-cyan-400">{file.price_tokens} tokens</div>
            <div className="text-sm text-gray-500">⭐ {file.rank_score.toFixed(1)} · ⬇ {file.download_count}</div>
          </div>
        </div>
        <p className="text-gray-300 mb-6 whitespace-pre-wrap">{file.description}</p>
        <div className="flex items-center gap-4">
          <button onClick={handleDownload} disabled={downloading}
            className="bg-cyan-600 hover:bg-cyan-500 disabled:bg-gray-700 text-white px-6 py-3 rounded-lg font-medium transition">
            {downloading ? 'Processing...' : 'Download File'}
          </button>
          {message && <span className={`text-sm ${message.includes('failed') || message.includes('Insufficient') || message.includes('Sign in') ? 'text-red-400' : 'text-green-400'}`}>{message}</span>}
        </div>
      </div>

      {summaryData && summaryData.note !== 'Not enough reviews yet' ? (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-lg">📊</span>
            <h2 className="text-xl font-bold text-white">{file.category.replace('_', ' ').toUpperCase()} SKILL</h2>
          </div>
          <div className="text-sm text-gray-400 mb-2">⭐ {summary.avg_score.toFixed(1)} · {summary.total_reviews} reviews</div>
          <div className="bg-gray-800 rounded-lg p-4 mb-6 text-gray-200 italic">"{summaryData.overall_sentiment || ''}"</div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <h3 className="text-green-400 font-semibold mb-2">✓ WHAT IT EXCELS AT</h3>
              <ul className="space-y-1">{(summaryData.strengths || []).map((s, i) => <li key={i} className="text-sm text-gray-300">✓ {s}</li>)}</ul>
            </div>
            <div>
              <h3 className="text-yellow-400 font-semibold mb-2">⚠ WHAT TO WATCH</h3>
              <ul className="space-y-1">{(summaryData.weaknesses || []).map((w, i) => <li key={i} className="text-sm text-gray-300">⚠ {w}</li>)}</ul>
            </div>
          </div>
          {summaryData.pairing_insights && (
            <div className="border-t border-gray-800 pt-4">
              <h3 className="text-cyan-400 font-semibold mb-2">BEST COMBINED WITH</h3>
              <p className="text-sm text-gray-300">{summaryData.pairing_insights}</p>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 mb-6 text-center text-gray-500">
          Not enough reviews yet. Be the first to review this file.
        </div>
      )}

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-8">
        <h2 className="text-xl font-bold text-white mb-4">Reviews ({reviews.length})</h2>
        {reviews.length === 0 ? <p className="text-gray-500">No reviews yet.</p> : (
          <div className="space-y-4">
            {reviews.map(r => (
              <div key={r.id} className="bg-gray-800 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-yellow-400">{'⭐'.repeat(r.score)}</span>
                  {r.agent_used && <span className="text-xs bg-gray-700 text-cyan-400 px-2 py-0.5 rounded">{r.agent_used}</span>}
                  {r.use_case && <span className="text-xs bg-gray-700 text-purple-400 px-2 py-0.5 rounded">{r.use_case.replace('_', ' ')}</span>}
                </div>
                {r.review_text && <p className="text-sm text-gray-300">{r.review_text}</p>}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
