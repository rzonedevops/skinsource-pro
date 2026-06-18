# SkinSource Pro

SkinSource Pro is an intelligent procurement platform for skincare ingredient sourcing.

## Canonical local commands

### Backend
```bash
cd /tmp/workspace/rzonedevops/skinsource-pro/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/seed_data.py
python src/services/seed_intelligence_data.py
python src/main.py
```

### Backend tests
```bash
cd /tmp/workspace/rzonedevops/skinsource-pro/backend
source .venv/bin/activate
python -m pytest
```

### Frontend
```bash
cd /tmp/workspace/rzonedevops/skinsource-pro/frontend
npm install
npm run dev
```

### Frontend tests and build
```bash
cd /tmp/workspace/rzonedevops/skinsource-pro/frontend
npm test
npm run build
```

## Authentication and authorization model

Procurement/intelligence APIs require role context via headers:

- `X-User-Id`: user id
- `X-User-Role`: `manager`, `analyst`, or `viewer`

Role boundaries:
- `viewer`: read-only
- `analyst`: create/update requests, target suppliers, submit responses, scoring
- `manager`: send RFQ, award, close lifecycle

## CI

CI (`.github/workflows/ci.yml`) enforces the canonical commands:
- backend: `pip install -r requirements.txt`, `python -m pytest`
- frontend: `npm ci`, `npm test`, `npm run build`

## API reference

See `/tmp/workspace/rzonedevops/skinsource-pro/docs/API_Reference_Guide.md` for normalized `v1` contracts and error schema.
