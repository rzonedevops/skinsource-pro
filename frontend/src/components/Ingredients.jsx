import { useEffect, useState } from 'react'

function Ingredients() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch('/api/ingredients?per_page=50')
      .then((res) => res.json())
      .then((payload) => {
        const items = payload.data || payload.ingredients || []
        setData(items)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p>Loading ingredients...</p>
  if (error) return <p>Failed to load ingredients: {error}</p>
  if (!data.length) return <p>No ingredients available.</p>

  return (
    <div className="space-y-4">
      {data.map((item) => (
        <div key={item.id} className="card" style={{ padding: '0.8rem 1rem' }}>
          <h3 style={{ margin: 0 }}>{item.name}</h3>
          <p style={{ margin: '0.3rem 0', color: 'var(--rz-text-muted)' }}>{item.function || 'No function provided'}</p>
          <small style={{ color: 'var(--rz-text-muted)' }}>Category: {item.category} · Sustainability: {item.sustainability_score ?? 'n/a'}</small>
        </div>
      ))}
    </div>
  )
}

export default Ingredients
