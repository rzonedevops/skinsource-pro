import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import Procurement from '../Procurement.jsx'

const mockedData = {
  ingredients: { data: [{ id: 1, name: 'Vitamin C' }] },
  suppliers: { data: [{ id: 1, company_name: 'Supplier A', country: 'DE' }] },
  requests: { data: [{ id: 11, ingredient_id: 1, title: 'RFQ A', status: 'draft', priority: 'high', response_count: 0 }] },
  requestDetails: { data: { id: 11, ingredient_id: 1, title: 'RFQ A', recipients: [], responses: [] } },
  recommendations: { data: { recommendations: [{ supplier: { id: 1, company_name: 'Supplier A' }, offering: { price_per_kg: 90, lead_time_days: 10 }, recommendation_score: 4.2, explainability: { why: ['Competitive cost'] }, risk_signals: [] }] } },
}

beforeEach(() => {
  global.fetch = vi.fn((url) => {
    if (url.includes('/api/ingredients')) return Promise.resolve({ ok: true, json: () => Promise.resolve(mockedData.ingredients) })
    if (url.includes('/api/suppliers')) return Promise.resolve({ ok: true, json: () => Promise.resolve(mockedData.suppliers) })
    if (url.includes('/api/procurement/requests?')) return Promise.resolve({ ok: true, json: () => Promise.resolve(mockedData.requests) })
    if (url.includes('/api/procurement/requests/11')) return Promise.resolve({ ok: true, json: () => Promise.resolve(mockedData.requestDetails) })
    if (url.includes('/api/v1/intelligence/supplier-recommendations')) return Promise.resolve({ ok: true, json: () => Promise.resolve(mockedData.recommendations) })

    return Promise.resolve({ ok: true, json: () => Promise.resolve({ data: {} }) })
  })
})

afterEach(() => {
  vi.restoreAllMocks()
})

test('renders workflow sections and recommendation panel', async () => {
  render(<Procurement />)

  await waitFor(() => {
    expect(screen.getByText('RFQ Builder')).toBeInTheDocument()
  })

  expect(screen.getByText('Supplier recommendation panel')).toBeInTheDocument()
  expect(screen.getByText('Response comparison matrix')).toBeInTheDocument()
  expect(screen.getByText('Lifecycle timeline & alerts')).toBeInTheDocument()

  await waitFor(() => {
    expect(screen.getByText('Supplier A')).toBeInTheDocument()
  })

  fireEvent.change(screen.getByLabelText('Scoring profile'), { target: { value: 'cost_first' } })
  expect(screen.getByLabelText('Scoring profile')).toHaveValue('cost_first')
})
