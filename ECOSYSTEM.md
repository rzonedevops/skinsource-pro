# Ecosystem Position: skinsource-pro

> This repository is part of the [SkinTwin-AI ecosystem](https://github.com/jax-a11y/skintwin-ecosystem-design).
> Its machine-readable manifest lives at [`.skintwin/manifest.json`](./.skintwin/manifest.json); the
> ecosystem-wide source of truth is `registry/ecosystem.json` in the hub repo.

**Layer:** erp-federation · **Role:** procurement-service

SkinSource Pro is the intelligent procurement platform for skincare ingredient sourcing: Flask/SQLAlchemy
REST APIs covering ingredients, suppliers, and the full RFQ lifecycle (`draft -> sent -> received ->
evaluated -> awarded -> completed`), with a React frontend and role-based access (`manager`/`analyst`/`viewer`).
In the ecosystem it is the concrete procurement domain of the Federated ERP layer, exposed behind the
gateway prefix `/api/erp/*`.

## Provides

- `procurement-api` — Ingredient sourcing, suppliers, RFQ procurement lifecycle; concrete procurement domain of the Federated ERP layer.

## Consumes

- `supplier-dataset` — ~1,316 curated supplier-intelligence JSON listings (schema v1.0) for cosmetics manufacturing, provided by `rzonedevops/pcsdbx1`.

## Events

| Topic | Direction |
| --- | --- |
| `inventory.updated` | publishes |
| `order.paid` | subscribes |

Payload schemas live at `contracts/events/<topic>.schema.json` in the hub repo.

## CI

CI runs via `.github/workflows/ci.yml`: backend `pytest` plus frontend `vitest` and build, enforcing the
canonical commands in the README. Reusable workflow templates for the ecosystem are documented in the hub
repo's `ci/README.md`.
