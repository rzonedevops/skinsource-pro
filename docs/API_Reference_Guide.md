# SkinSource Pro API Reference (v1)

## Base URL

- Local: `http://localhost:5000/api`

## Authentication and roles

Pass role context headers for protected actions:

- `X-User-Id: <int>`
- `X-User-Role: manager|analyst|viewer`

## Response envelope

Successful `v1` endpoints return:

```json
{
  "data": { "api_version": "v1", "...": "..." },
  "meta": { "pagination": { "page": 1, "per_page": 20, "total": 0, "pages": 0, "has_next": false, "has_prev": false } }
}
```

Errors return:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Missing required fields",
    "details": { "missing": ["title"] }
  }
}
```

## Procurement lifecycle

Statuses:
- `draft -> sent -> received -> evaluated -> awarded -> completed`
- `cancelled` allowed from non-terminal states

Invalid transitions return `409 invalid_transition`.

### Requests

- `GET /procurement/requests`
  - filters: `user_id,status,priority,ingredient_id`
  - pagination: `page,per_page,sort`

- `POST /procurement/requests` (`analyst+`)
  - required: `title,ingredient_id,quantity_needed`

- `GET /procurement/requests/{id}`
  - includes recipients, responses, awards, negotiations, and event timeline

- `PUT /procurement/requests/{id}` (`analyst+`)
  - supports request edits and status transitions

### Workflow stages

- `POST /procurement/requests/{id}/suppliers` (`analyst+`)
  - target RFQ recipients
- `POST /procurement/requests/{id}/send` (`manager+`)
  - send RFQ and start lifecycle tracking
- `POST /procurement/requests/{id}/responses` (`analyst+`)
  - receive/track supplier responses
- `POST /procurement/requests/{id}/score` (`analyst+`)
  - profiles: `cost_first|quality_first|sustainability_first|balanced`
- `POST /procurement/requests/{id}/award` (`manager+`)
  - records award rationale and winning response
- `POST /procurement/requests/{id}/close` (`manager+`)
  - close as `completed` or `cancelled`
- `POST /procurement/requests/{id}/negotiations` (`analyst+`)
  - append negotiation rounds and outcomes

### Operations and observability

- `GET /procurement/reminders` (`analyst+`)
  - deadline/overdue reminder generation
- `GET /procurement/dashboard`
  - deterministic savings from awarded vs baseline quoted/target prices

## Intelligence endpoints

All intelligence endpoints are available under both:
- `/intelligence/...` (compatibility)
- `/v1/intelligence/...` (canonical)

### Endpoints

- `POST /v1/intelligence/discover-suppliers`
  - required: `ingredient_name`
  - optional: `region`
  - supports pagination/sorting

- `GET /v1/intelligence/evaluate-supplier/{supplier_id}`
  - returns supplier performance evaluation and explainability

- `POST /v1/intelligence/optimize-pricing`
  - required: `ingredient_id, quantity`

- `GET /v1/intelligence/market-intelligence/{category}`
  - returns market insights and category risk signals

- `GET /v1/intelligence/supplier-recommendations?ingredient_id=<id>&profile=balanced&page=1&per_page=10&sort=-score`
  - profile-aware recommendations with explainability and risk signals

- `GET /v1/intelligence/price-trends/{ingredient_id}`
  - deterministic historical/forecasted trend output derived from stored data

- `POST /v1/intelligence/competitive-analysis`
  - required: `ingredient_ids`
  - optional: `profile`, `quantity`

- `GET /v1/intelligence/audit`
  - request audit log for intelligence endpoints

## Rate limiting and auditing

- Intelligence API is rate-limited per remote address (60 requests/minute).
- Every intelligence request is audited with endpoint, actor, payload summary, status, and timestamp.

## Canonical validation commands

```bash
cd /tmp/workspace/rzonedevops/skinsource-pro/backend && python -m pytest
cd /tmp/workspace/rzonedevops/skinsource-pro/frontend && npm test && npm run build
```
