import { useEffect, useMemo, useState } from 'react'

function Dashboard() {
  const [payload, setPayload] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch('/api/procurement/dashboard')
      .then(async (res) => {
        const data = await res.json()
        if (!res.ok) throw new Error(data?.error?.message || 'Failed to load dashboard')
        return data
      })
      .then((data) => setPayload(data.data || data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const stats = payload?.statistics || {}
  const recentEvents = payload?.recent_events || []
  const recentRequests = payload?.recent_requests || []

  const healthSignals = useMemo(() => {
    if (!payload) return []
    const total = stats.total_requests || 0
    const completed = stats.completed_orders || 0
    const completionRate = total ? Math.round((completed / total) * 100) : 0
    const active = stats.active_rfqs || 0

    return [
      { label: 'Completion rate', value: `${completionRate}%`, tone: completionRate >= 60 ? 'good' : 'warn' },
      { label: 'Active RFQs', value: active, tone: active > 0 ? 'good' : 'warn' },
      { label: 'Realized savings', value: `$${(stats.total_savings || 0).toFixed(2)}`, tone: (stats.total_savings || 0) > 0 ? 'good' : 'warn' },
    ]
  }, [payload, stats])

  if (loading) return <p>Loading procurement intelligence dashboard...</p>
  if (error) return <p>Dashboard error: {error}</p>

  return (
    <div className="space-y-6">
      <section className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(180px,1fr))' }}>
        <StatCard label="Total requests" value={stats.total_requests || 0} />
        <StatCard label="Active RFQs" value={stats.active_rfqs || 0} />
        <StatCard label="Pending awards" value={stats.pending_orders || 0} />
        <StatCard label="Completed" value={stats.completed_orders || 0} />
        <StatCard label="Savings" value={`$${(stats.total_savings || 0).toFixed(2)}`} />
        <StatCard label="Active suppliers" value={stats.active_suppliers || 0} />
      </section>

      <section className="card" style={{ padding: '1rem' }}>
        <h3 style={{ marginTop: 0 }}>Procurement intelligence signals</h3>
        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(170px,1fr))' }}>
          {healthSignals.map((signal) => (
            <div key={signal.label} className={`signal-tile${signal.tone === 'good' ? ' signal-tile--good' : ''}`}>
              <small className="signal-tile__label">{signal.label}</small>
              <div className="signal-tile__value">{signal.value}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(280px,1fr))' }}>
        <div className="card" style={{ padding: '1rem' }}>
          <h3 style={{ marginTop: 0 }}>Recent requests</h3>
          {!recentRequests.length && <p>No recent requests found.</p>}
          {recentRequests.map((req) => (
            <div key={req.id} style={{ padding: '0.5rem 0', borderBottom: '1px solid var(--rz-border-subtle)' }}>
              <strong>{req.title}</strong>
              <div style={{ fontSize: '0.85rem', color: 'var(--rz-text-muted)' }}>
                {req.status} · priority {req.priority} · {req.response_count} responses
              </div>
            </div>
          ))}
        </div>

        <div className="card" style={{ padding: '1rem' }}>
          <h3 style={{ marginTop: 0 }}>Lifecycle timeline</h3>
          {!recentEvents.length && <p>No events captured yet.</p>}
          {recentEvents.map((event) => (
            <div key={event.id} style={{ padding: '0.45rem 0', borderBottom: '1px solid var(--rz-border-subtle)' }}>
              <strong>{event.event_type}</strong>
              <div style={{ fontSize: '0.85rem', color: 'var(--rz-text-muted)' }}>{event.from_status || '-'} → {event.to_status || '-'}</div>
              <small style={{ color: 'var(--rz-text-faint)' }}>{event.created_at}</small>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

function StatCard({ label, value }) {
  return (
    <div className="rz-stat">
      <div className="rz-stat__value">{value}</div>
      <div className="rz-stat__label">{label}</div>
    </div>
  )
}

export default Dashboard
