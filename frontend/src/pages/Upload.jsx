import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const CATEGORIES = [
  { value: 'data_analysis', label: 'Data Analysis' }, { value: 'marketing', label: 'Marketing' },
  { value: 'coding', label: 'Coding' }, { value: 'research', label: 'Research' },
  { value: 'content', label: 'Content' }, { value: 'other', label: 'Other' },
]
const TIERS = [
  { value: 'skill_creation_file', label: 'Skill Creation File' },
  { value: 'complete_skill', label: 'Complete Skill' },
  { value: 'workflow_template', label: 'Workflow Template' },
]

export default function Upload({ API, user }) {
  const navigate = useNavigate()
  const [form, setForm] = useState({ title: '', description: '', category: 'coding', product_tier: 'skill_creation_file', tags: '', price_tokens: 100 })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  if (!user) return <div className="text-center text-gray-400 py-12">Sign in to upload files.</div>

  const handleSubmit = async (e) => {
    e.preventDefault(); setSubmitting(true); setError('')
    try {
      const res = await API.post('/files', form)
      navigate(`/files/${res.data.id}`)
    } catch (err) { setError(err.response?.data?.detail || 'Upload failed') }
    setSubmitting(false)
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-white mb-6">Upload New File</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm text-gray-400 mb-1">Title</label>
          <input type="text" required value={form.title} onChange={e => setForm({...form, title: e.target.value})}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-cyan-500" />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Description</label>
          <textarea required rows={6} value={form.description} onChange={e => setForm({...form, description: e.target.value})}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-cyan-500" />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Category</label>
            <select value={form.category} onChange={e => setForm({...form, category: e.target.value})}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-cyan-500">
              {CATEGORIES.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Product Tier</label>
            <select value={form.product_tier} onChange={e => setForm({...form, product_tier: e.target.value})}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-cyan-500">
              {TIERS.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Tags (comma-separated)</label>
            <input type="text" value={form.tags} onChange={e => setForm({...form, tags: e.target.value})}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-cyan-500" />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Price (tokens)</label>
            <input type="number" min={0} value={form.price_tokens} onChange={e => setForm({...form, price_tokens: parseInt(e.target.value) || 0})}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-cyan-500" />
          </div>
        </div>
        {error && <div className="text-red-400 text-sm">{error}</div>}
        <button type="submit" disabled={submitting}
          className="bg-cyan-600 hover:bg-cyan-500 disabled:bg-gray-700 text-white px-6 py-3 rounded-lg font-medium transition">
          {submitting ? 'Uploading...' : 'Publish File'}
        </button>
      </form>
    </div>
  )
}
