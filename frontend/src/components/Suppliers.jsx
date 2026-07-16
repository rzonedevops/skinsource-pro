import { useEffect, useState } from 'react'

function Suppliers() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch('/api/suppliers?per_page=50')
      .then((res) => res.json())
      .then((payload) => {
        const items = payload.data || payload.suppliers || []
        setData(items)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p>Loading suppliers...</p>
  if (error) return <p>Failed to load suppliers: {error}</p>
  if (!data.length) return <p>No suppliers available.</p>

  return (
    <div className="space-y-4">
      {data.map((supplier) => (
        <div key={supplier.id} className="card" style={{ padding: '0.8rem 1rem' }}>
          <h3 style={{ margin: 0 }}>{supplier.company_name}</h3>
          <p style={{ margin: '0.3rem 0', color: 'var(--rz-text-muted)' }}>{supplier.country || 'Country unknown'}</p>
          <small style={{ color: 'var(--rz-text-muted)' }}>
            Quality {supplier.scores?.quality ?? 'n/a'} · Reliability {supplier.scores?.reliability ?? 'n/a'} · Sustainability {supplier.scores?.sustainability ?? 'n/a'}
          </small>
        </div>
      ))}
    </div>
  )
}

export default Suppliers
