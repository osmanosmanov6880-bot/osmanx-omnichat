# Release v0.3 - website messaging and global readiness groundwork

Date: 2026-11-03. This is an engineering delivery report, not an independent compliance certification.

## Implemented in source

- New first-party Website Chat connector, widget management, origin validation, secure visitor sessions and embed runtime.
- Responsive visitor chat UI; direct staff-to-visitor messages, test-mode labeling, idempotent inbound messages, private visitor access.
- Conversation claim and release via atomic optimistic DB updates, preventing simultaneous conflicting replies while the lease is active.
- Tenant-scoped operations page with outbox diagnostics, last-error tracking, and evidence-required uncertain-send resolution.
- Separate worker service in Docker Compose, background queue and cleanup routines separated from the API process.
- IANA organization timezone and ISO currency selection; prevent reinterpretation of existing deal amounts; analytics buckets use org timezone.
- UI channel filters, branding, controls and responsive pages; server-side role validation for admin operations.
- Alembic revision for new data models and extra conversation/org attributes.

## Verification

- 28/28 automated Python tests pass on local SQLite (with three httpx deprecation warnings from existing webhook tests).
- TypeScript compilation succeeds (`tsc --project frontend/tsconfig.json`).
- Alembic upgrade and drift checks succeed on a fresh SQLite schema.
- Chromium renders compiled React and visitor widget scripts, and verifies a conversation round-trip with the actual FastAPI app through an in-process request bridge. Desktop and mobile screenshots saved.
- Chromium HTTP navigation was blocked by the execution environment: this test is **not** a real network browser-to-server or public HTTPS E2E validation.

## Nonimplemented / unverified dependencies

- No authorized live WhatsApp, Instagram or Avito account access, so there is **no proof of live provider message delivery**.
- Docker Compose and PostgreSQL deployment were not runnable in the current environment.
- Payment processing, recurring subscription collection, approval flows, high-availability topology and global production compliance remain incomplete.
- React 16 is end-of-life: modernization remains a blocking prerequisite to paid deployment.
- No formal accessibility, penetration, load or disaster-recovery test; not certified for international enterprise use.

## Weighted scope estimate

Feature coverage versus the original A-G brief is approximately **67%** using the same weighted categories as earlier releases. This number is not a production readiness, reliability or security score. See `STATUS.md` for the exact arithmetic.
