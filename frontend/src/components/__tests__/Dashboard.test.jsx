import { render, screen, waitFor } from '@testing-library/react'
import Dashboard from '../Dashboard.jsx'

beforeEach(() => {
  global.fetch = vi.fn(() =>
    Promise.resolve({
      ok: true,
      json: () =>
        Promise.resolve({
          data: {
            statistics: {
              total_requests: 10,
              active_rfqs: 3,
              pending_orders: 2,
              completed_orders: 5,
              total_savings: 1234.5,
              active_suppliers: 4,
            },
            recent_requests: [{ id: 1, title: 'RFQ', status: 'sent', priority: 'high', response_count: 2 }],
            recent_events: [{ id: 1, event_type: 'status_transition', from_status: 'draft', to_status: 'sent', created_at: '2026-01-01T00:00:00' }],
          },
        }),
    }),
  )
})

afterEach(() => {
  vi.restoreAllMocks()
})

test('shows dashboard metrics and timeline', async () => {
  render(<Dashboard />)

  await waitFor(() => {
    expect(screen.getByText('Procurement intelligence signals')).toBeInTheDocument()
  })

  expect(screen.getByText('Total requests')).toBeInTheDocument()
  expect(screen.getByText('10')).toBeInTheDocument()
  expect(screen.getByText('Lifecycle timeline')).toBeInTheDocument()
})
