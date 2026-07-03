import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

const CATEGORIES = [
  { value: '', label: 'All Categories' },
  { value: 'data_analysis', label: 'Data Analysis' },
  { value: 'marketing', label: 'Marketing' },
  { value: 'coding', label: 'Coding' },
  { value: 'research', label: 'Research' },
  { value: 'content', label: 'Content' },
  { value: 'other', label: 'Other' },
]

const TIERS = [
  { value: '', label: 'All Tiers' },
  { value: 'skill_creation_file', label: 'Skill Creation Files' },
  { value: 'complete_skill', label: 'Complete Skills' },
  { value: 'workflow_template', label: 'Workflow Templates' },
]

export default function Browse({ API }) {
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(true)
  const [category, setCategory] = useState('')
  const [tier, setTier] = useState('')
  const [sort, setSort] = useState('rank')
  const [search, setSearch] = useState('')

  useEffect(() => {
    setLoading(true)
    const params = { sort, limit: 50 }
    if (category) params.category = category
    if (tier) params.tier = tier
    API.get('/files', { params })
      .then((res) => {
        let data = res.data
        if (search) {
          const q = search.toLowerCase()
          data = data.filter(f => f.title.toLowerCase().includes(q) || f.tags?.toLowerCase().includes(q))
        }
        setFiles(data)
      })
      .catch(() => setFiles([]))
      .finally(() => setLoading(false))
  }, [category, tier, sort])

  return (
    <div>
      <h1 className="text-3xl font-bold text-white mb-6">Skill Marketplace</h1>

      <div className="flex flex-wrap gap-3 mb-8">
        <input type="text" placeholder="Search files..." value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm text-white w-64 focus:outline-none focus:border-cyan-500" />
        <select value={category} onChange={(e) => setCategory(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-cyan-500">
          {CATEGORIES.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
        </select>
        <select value={tier} onChange={(e) => setTier(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-cyan-500">
          {TIERS.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
        </select>
        <select value={sort} onChange={(e) => setSort(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-cyan-500">
          <option value="rank">Top Ranked</option>
          <option value="newest">Newest</option>
          <option value="downloads">Most Downloaded</option>
          <option value="price">Cheapest</option>
        </select>
      </div>

      {loading ? (
        <div className="text-center text-gray-400 py-12">Loading...</div>
      ) : files.length === 0 ? (
        <div className="text-center text-gray-400 py-12">No files found. Be the first to upload!</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {files.map((file) => (
            <Link key={file.id} to={`/files/${file.id}`}
              className="block bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-cyan-700 transition">
              <div className="flex items-start justify-between mb-3">
                <span className="text-xs font-medium bg-gray-800 text-cyan-400 px-2 py-1 rounded">{file.category.replace('_', ' ')}</span>
                <span className="text-sm font-bold text-cyan-400">{file.price_tokens} tokens</span>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">{file.title}</h3>
              <p className="text-sm text-gray-400 mb-4 line-clamp-2">{file.description}</p>
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>by {file.contributor_name || 'anon'}</span>
                <div className="flex items-center gap-3">
                  <span>⭐ {file.rank_score.toFixed(1)}</span>
                  <span>⬇ {file.download_count}</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
