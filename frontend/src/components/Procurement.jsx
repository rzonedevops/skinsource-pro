import { useEffect, useMemo, useState } from 'react'

const API_HEADERS = {
  'Content-Type': 'application/json',
  'X-User-Id': '1',
  'X-User-Role': 'manager',
}

const initialForm = {
  ingredient_id: '',
  title: '',
  description: '',
  quantity_needed: 100,
  target_price: '',
  delivery_date: '',
  deadline: '',
  priority: 'medium',
}

function Procurement() {
  const [ingredients, setIngredients] = useState([])
  const [suppliers, setSuppliers] = useState([])
  const [requests, setRequests] = useState([])
  const [responses, setResponses] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [activeRequestId, setActiveRequestId] = useState(null)
  const [workflowError, setWorkflowError] = useState(null)
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState(initialForm)
  const [selectedSuppliers, setSelectedSuppliers] = useState([])
  const [scoreProfile, setScoreProfile] = useState('balanced')
  const [awardRationale, setAwardRationale] = useState('')

  const activeRequest = useMemo(() => requests.find((request) => request.id === activeRequestId) || null, [requests, activeRequestId])

  useEffect(() => {
    initialize()
  }, [])

  useEffect(() => {
    if (!activeRequest?.ingredient_id) {
      setRecommendations([])
      return
    }

    fetch(`/api/v1/intelligence/supplier-recommendations?ingredient_id=${activeRequest.ingredient_id}&profile=${scoreProfile}&per_page=8`)
      .then((res) => res.json())
      .then((payload) => setRecommendations(payload?.data?.recommendations || []))
      .catch(() => setRecommendations([]))
  }, [activeRequest?.ingredient_id, scoreProfile])

  const initialize = async () => {
    setLoading(true)
    setWorkflowError(null)
    try {
      const [ingredientsRes, suppliersRes, requestsRes] = await Promise.all([
        fetch('/api/ingredients?per_page=100'),
        fetch('/api/suppliers?per_page=100'),
        fetch('/api/procurement/requests?per_page=50'),
      ])

      const ingredientsPayload = await ingredientsRes.json()
      const suppliersPayload = await suppliersRes.json()
      const requestsPayload = await requestsRes.json()

      const normalizedIngredients = ingredientsPayload.data || ingredientsPayload.ingredients || []
      const normalizedSuppliers = suppliersPayload.data || suppliersPayload.suppliers || []
      const normalizedRequests = requestsPayload.data || requestsPayload.requests || []

      setIngredients(normalizedIngredients)
      setSuppliers(normalizedSuppliers)
      setRequests(normalizedRequests)

      const firstRequest = normalizedRequests[0]
      if (firstRequest?.id) {
        setActiveRequestId(firstRequest.id)
        await loadRequestDetails(firstRequest.id)
      }
    } catch (error) {
      setWorkflowError(error.message)
    } finally {
      setLoading(false)
    }
  }

  const loadRequestDetails = async (requestId) => {
    const response = await fetch(`/api/procurement/requests/${requestId}`)
    const payload = await response.json()
    const normalized = payload.data || payload
    setResponses(normalized.responses || [])

    if (Array.isArray(normalized.recipients)) {
      setSelectedSuppliers(normalized.recipients.map((recipient) => recipient.supplier_id))
    }
  }

  const updateForm = (field, value) => setForm((prev) => ({ ...prev, [field]: value }))

  const createRequest = async (event) => {
    event.preventDefault()
    setWorkflowError(null)

    try {
      const response = await fetch('/api/procurement/requests', {
        method: 'POST',
        headers: API_HEADERS,
        body: JSON.stringify({
          ...form,
          ingredient_id: Number(form.ingredient_id),
          quantity_needed: Number(form.quantity_needed),
          target_price: form.target_price ? Number(form.target_price) : null,
          deadline: form.deadline || null,
        }),
      })

      const payload = await response.json()
      if (!response.ok) throw new Error(payload?.error?.message || 'Unable to create request')

      const created = payload.data
      const nextRequests = [created, ...requests]
      setRequests(nextRequests)
      setActiveRequestId(created.id)
      setForm(initialForm)
      setSelectedSuppliers([])
      setResponses([])
    } catch (error) {
      setWorkflowError(error.message)
    }
  }

  const saveTargets = async () => {
    if (!activeRequestId) return
    setWorkflowError(null)

    try {
      const response = await fetch(`/api/procurement/requests/${activeRequestId}/suppliers`, {
        method: 'POST',
        headers: API_HEADERS,
        body: JSON.stringify({ supplier_ids: selectedSuppliers }),
      })

      const payload = await response.json()
      if (!response.ok) throw new Error(payload?.error?.message || 'Unable to target suppliers')

      await initialize()
    } catch (error) {
      setWorkflowError(error.message)
    }
  }

  const sendRFQ = async () => {
    if (!activeRequestId) return

    try {
      const response = await fetch(`/api/procurement/requests/${activeRequestId}/send`, {
        method: 'POST',
        headers: API_HEADERS,
        body: JSON.stringify({ deadline: activeRequest?.deadline }),
      })
      const payload = await response.json()
      if (!response.ok) throw new Error(payload?.error?.message || 'Unable to send RFQ')
      await initialize()
    } catch (error) {
      setWorkflowError(error.message)
    }
  }

  const scoreResponses = async () => {
    if (!activeRequestId) return

    try {
      const response = await fetch(`/api/procurement/requests/${activeRequestId}/score`, {
        method: 'POST',
        headers: API_HEADERS,
        body: JSON.stringify({ profile: scoreProfile }),
      })
      const payload = await response.json()
      if (!response.ok) throw new Error(payload?.error?.message || 'Unable to score responses')
      await loadRequestDetails(activeRequestId)
      await initialize()
    } catch (error) {
      setWorkflowError(error.message)
    }
  }

  const awardRequest = async (responseId) => {
    if (!activeRequestId || !awardRationale.trim()) {
      setWorkflowError('Award rationale is required.')
      return
    }

    try {
      const response = await fetch(`/api/procurement/requests/${activeRequestId}/award`, {
        method: 'POST',
        headers: API_HEADERS,
        body: JSON.stringify({ response_id: responseId, rationale: awardRationale }),
      })

      const payload = await response.json()
      if (!response.ok) throw new Error(payload?.error?.message || 'Unable to award request')

      setAwardRationale('')
      await initialize()
      await loadRequestDetails(activeRequestId)
    } catch (error) {
      setWorkflowError(error.message)
    }
  }

  const toggleSupplier = (supplierId, checked) => {
    setSelectedSuppliers((prev) => {
      if (checked && !prev.includes(supplierId)) return [...prev, supplierId]
      if (!checked) return prev.filter((id) => id !== supplierId)
      return prev
    })
  }

  if (loading) return <p>Loading procurement workflow...</p>

  return (
    <div className="space-y-6">
      {workflowError && <p style={{ color: 'hsl(0 84% 60%)' }}>Workflow error: {workflowError}</p>}

      <section className="card" style={{ padding: '1rem' }}>
        <h2 style={{ marginTop: 0 }}>RFQ Builder</h2>
        <form onSubmit={createRequest} className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(220px,1fr))' }}>
          <label className="rz-field">
            <span className="rz-field__label">Ingredient</span>
            <select value={form.ingredient_id} onChange={(event) => updateForm('ingredient_id', event.target.value)} required className="rz-field__input">
              <option value="">Select ingredient</option>
              {ingredients.map((ingredient) => (
                <option key={ingredient.id} value={ingredient.id}>{ingredient.name}</option>
              ))}
            </select>
          </label>
          <label className="rz-field">
            <span className="rz-field__label">Request title</span>
            <input value={form.title} onChange={(event) => updateForm('title', event.target.value)} required className="rz-field__input" />
          </label>
          <label className="rz-field">
            <span className="rz-field__label">Quantity needed (kg)</span>
            <input type="number" min="1" value={form.quantity_needed} onChange={(event) => updateForm('quantity_needed', event.target.value)} required className="rz-field__input" />
          </label>
          <label className="rz-field">
            <span className="rz-field__label">Target price ($/kg)</span>
            <input type="number" min="0" step="0.01" value={form.target_price} onChange={(event) => updateForm('target_price', event.target.value)} className="rz-field__input" />
          </label>
          <label className="rz-field">
            <span className="rz-field__label">Delivery date</span>
            <input type="date" value={form.delivery_date} onChange={(event) => updateForm('delivery_date', event.target.value)} className="rz-field__input" />
          </label>
          <label className="rz-field">
            <span className="rz-field__label">Deadline (ISO timestamp)</span>
            <input value={form.deadline} onChange={(event) => updateForm('deadline', event.target.value)} placeholder="2026-06-20T17:00:00" className="rz-field__input" />
          </label>
          <label className="rz-field" style={{ gridColumn: '1 / -1' }}>
            <span className="rz-field__label">Requirements</span>
            <textarea value={form.description} onChange={(event) => updateForm('description', event.target.value)} rows={3} className="rz-field__input" />
          </label>
          <div style={{ gridColumn: '1 / -1', display: 'flex', justifyContent: 'flex-end' }}>
            <button type="submit" className="rz-btn rz-btn--primary rz-btn--sm">Create request</button>
          </div>
        </form>
      </section>

      <section className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(320px,1fr))' }}>
        <div className="card" style={{ padding: '1rem' }}>
          <h3 style={{ marginTop: 0 }}>Lifecycle timeline & alerts</h3>
          {!requests.length && <p>No requests created yet.</p>}
          {requests.map((request) => (
            <button
              key={request.id}
              onClick={() => {
                setActiveRequestId(request.id)
                loadRequestDetails(request.id)
              }}
              style={{
                width: '100%',
                border: `1px solid ${activeRequestId === request.id ? 'var(--rz-border-accent)' : 'var(--rz-border)'}`,
                borderRadius: 8,
                textAlign: 'left',
                padding: '0.6rem',
                marginBottom: 8,
                background: activeRequestId === request.id ? 'var(--rz-bg-surface)' : 'transparent',
                color: 'var(--rz-text-primary)',
                cursor: 'pointer',
              }}
            >
              <strong>{request.title}</strong>
              <div style={{ fontSize: '0.85rem', color: 'var(--rz-text-muted)' }}>
                {request.status} · {request.priority} priority · {request.is_overdue ? 'Overdue' : 'On track'}
              </div>
            </button>
          ))}
        </div>

        <div className="card" style={{ padding: '1rem' }}>
          <h3 style={{ marginTop: 0 }}>Target suppliers & send RFQ</h3>
          {!activeRequest && <p>Select a request to continue.</p>}
          {activeRequest && (
            <>
              <div className="space-y-4" style={{ maxHeight: 220, overflow: 'auto' }}>
                {suppliers.map((supplier) => (
                  <label key={supplier.id} style={{ display: 'block', borderBottom: '1px solid var(--rz-border-subtle)', paddingBottom: 8 }}>
                    <input
                      type="checkbox"
                      checked={selectedSuppliers.includes(supplier.id)}
                      onChange={(event) => toggleSupplier(supplier.id, event.target.checked)}
                      style={{ marginRight: 8 }}
                    />
                    {supplier.company_name} · {supplier.country}
                  </label>
                ))}
              </div>
              <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
                <button onClick={saveTargets} className="rz-btn rz-btn--primary rz-btn--sm">Save targets</button>
                <button onClick={sendRFQ} className="rz-btn rz-btn--ghost rz-btn--sm" disabled={!selectedSuppliers.length}>Send RFQ</button>
              </div>
            </>
          )}
        </div>
      </section>

      <section className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(320px,1fr))' }}>
        <div className="card" style={{ padding: '1rem' }}>
          <h3 style={{ marginTop: 0 }}>Supplier recommendation panel</h3>
          <label className="rz-field">
            <span className="rz-field__label">Scoring profile</span>
            <select value={scoreProfile} onChange={(event) => setScoreProfile(event.target.value)} className="rz-field__input">
              <option value="balanced">Balanced</option>
              <option value="cost_first">Cost-first</option>
              <option value="quality_first">Quality-first</option>
              <option value="sustainability_first">Sustainability-first</option>
            </select>
          </label>
          {!recommendations.length && <p style={{ marginTop: 8 }}>No recommendations yet.</p>}
          {recommendations.map((entry) => (
            <div key={entry.supplier.id} style={{ borderTop: '1px solid var(--rz-border-subtle)', padding: '0.6rem 0' }}>
              <strong>{entry.supplier.company_name}</strong>
              <div style={{ fontSize: '0.85rem', color: 'var(--rz-text-muted)' }}>
                Score: {entry.recommendation_score} · Price: ${entry.offering.price_per_kg}/kg · Lead time: {entry.offering.lead_time_days} days
              </div>
              <small style={{ color: 'var(--rz-text-muted)' }}>Why: {(entry.explainability?.why || []).join(', ') || 'Insufficient data'}</small>
              {entry.risk_signals?.length > 0 && <div style={{ color: 'hsl(0 84% 60%)', fontSize: '0.8rem' }}>Risk: {entry.risk_signals.join(', ')}</div>}
            </div>
          ))}
        </div>

        <div className="card" style={{ padding: '1rem' }}>
          <h3 style={{ marginTop: 0 }}>Response comparison matrix</h3>
          {!activeRequest && <p>Select a request first.</p>}
          {activeRequest && (
            <>
              <button onClick={scoreResponses} className="rz-btn rz-btn--primary rz-btn--sm" disabled={!responses.length}>Score/rank options</button>
              {!responses.length && <p style={{ marginTop: 8 }}>No supplier responses yet.</p>}
              {responses.map((response) => (
                <div key={response.id} style={{ borderTop: '1px solid var(--rz-border-subtle)', padding: '0.65rem 0' }}>
                  <strong>{response.supplier?.company_name || `Supplier #${response.supplier_id}`}</strong>
                  <div style={{ fontSize: '0.85rem', color: 'var(--rz-text-muted)' }}>
                    ${response.quoted_price}/kg · Lead {response.lead_time_days}d · Total score {response.score_breakdown?.total ?? 'n/a'}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--rz-text-muted)' }}>
                    Breakdown: price {response.score_breakdown?.price ?? 'n/a'} · quality {response.score_breakdown?.quality ?? 'n/a'} · sustainability {response.score_breakdown?.sustainability ?? 'n/a'} · risk {response.score_breakdown?.risk ?? 'n/a'}
                  </div>
                  {activeRequest.status !== 'awarded' && (
                    <button onClick={() => awardRequest(response.id)} className="rz-btn rz-btn--primary rz-btn--sm" style={{ marginTop: 6 }}>Award this supplier</button>
                  )}
                </div>
              ))}
            </>
          )}
        </div>
      </section>

      <section className="card" style={{ padding: '1rem' }}>
        <h3 style={{ marginTop: 0 }}>Award rationale capture</h3>
        <textarea
          rows={3}
          placeholder="Document why the selected supplier was chosen..."
          value={awardRationale}
          onChange={(event) => setAwardRationale(event.target.value)}
          className="rz-field__input"
        />
      </section>
    </div>
  )
}

export default Procurement
