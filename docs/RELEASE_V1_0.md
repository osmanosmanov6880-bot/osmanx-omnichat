# OSMANX OMNICHAT v1.0 -- Connector Assurance / Delivery Truth

**Build type:** self-hosted, locally tested MVP, not production certification.
**Focus:** fewer clicks for setup, more truthful channel and message status.
**Explicitly out of scope:** payment processing, hosting/deployment, unapproved accounts.

## What changed in executable code

1. `backend/app/integrations/probe` is implemented in `backend/app/onboarding.py` as `POST /api/integrations/{channel_id}/probe`. Each check enforces organization ownership and owner/admin RBAC. It performs official read-only provider identity requests. For Telegram and MAX with a configured HTTPS public base it additionally compares the exact provider-side subscribed webhook URL. It cannot send a message or manufacture an incoming event. The response distinguishes access, webhook registration, confirmed inbound, and provider acceptance of outbound.
2. A persistent SQL cooldown (`channel_connections.last_probe_at`) prevents repetitive probe calls across application instances. Migration `f1000010cafe` adds the field. The server returns HTTP 429 for checks within 30 seconds.
3. The React integrations UI displays one primary action for checking a connection. Detailed actions are retained in an expandable section. The app explains the next verified step, rather than green-labeling a token as a working channel.
4. `delivery_state.advance_delivery_state` makes WhatsApp status receipts monotonic: `delivered -> sent` and `read -> delivered` cannot regress. Failures arriving after proven delivery/read also cannot overwrite that evidence. It still allows explicit later successful delivery to reconcile a failed status.
5. Outgoing message bubbles now distinguish queued, processing, API accepted, provider sent, delivered, read, failed, and uncertain. `accepted` is **not a delivery checkmark**. Older or unknown status codes also never default to a success checkmark.
6. The quick-start checklist counts a live outbound only after provider acceptance (or proven website-chat delivery), never when the message is merely queued.
7. Backend health version and UI version labels are aligned to 1.0.0.

## Verified in this environment

- `71 passed` Python backend/API tests, including seven new delivery/probe cases and an updated quick-start regression test.
- TypeScript build with `tsc --project frontend/tsconfig.json` (rebuilt app.js included in archive).
- Clean SQLite migration through Alembic and schema-drift check.
- Old v0.9 database migration to v1.0 with existing organization and channel rows preserved.
- Browser-run FastAPI-backed React flow in Chromium for desktop, 390px phone and 320px narrow phone: integration screen, mobile navigation, exact-channel probe, four stages, no JS exceptions or horizontal overflow.
- External HTTP replies in tests are mocked, deliberately. No credentials or approvals for real social accounts were supplied.

## Not yet verified / blockers for real customer production

- Live incoming AND outgoing for each approved provider account (Avito, Instagram, WhatsApp, Telegram, VK, MAX, Messenger).
- Meta App Review, Avito authorization and allowed account features; real redirect domains and webhooks.
- React 16 vendor files must be upgraded to a supported version; currently functioning but unsupported.
- Docker/PostgreSQL production deployment, HTTPS/DNS, external penetration test, backup restore and load tests.
- WhatsApp template messages outside the customer service window and complete media support; not provided by this release.
- Billing, paid subscriptions and public deployment remain intentionally disabled.

## How to test the artifact

```sh
PYTHONPATH=backend pytest -q backend/tests

tsc --project frontend/tsconfig.json

PYTHONPATH=backend python scripts/browser_v10_connection.py

python scripts/check_live_setup.py
```

The browser script mocks official provider HTTP and uses real FastAPI handlers in process; do not represent it as testing a public URL or delivering a real social message.
