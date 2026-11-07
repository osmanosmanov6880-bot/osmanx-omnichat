# OSMANX OMNICHAT - world-scale product roadmap

This roadmap differentiates implementation from evidence. v0.3 is a self-hostable functional MVP, **not** a globally available production SaaS.

## Product thesis

One conversation workspace that joins consented business messaging and first-party web chats, with staff collaboration, CRM, SLA, analytics, and transparent rule-based automation. An integration should never claim to be connected until the remote provider has verified credentials; it should never claim delivery without provider evidence.

## What makes a defensible offering

1. **Owner value:** fewer unanswered leads and faster handoffs, rather than another generic CRM clone.
2. **Operator value:** one inbox with history, lock/claim, saved replies and contextual CRM.
3. **Measurability:** first response time, unanswered conversations, source distribution; financially confirmed versus estimated revenue must remain separated.
4. **Portability:** first-party website messaging functions even without Meta or Avito approval; third-party connectors obey their own terms and policies.
5. **Trust:** isolation by company, signed events, auditable decisions, retention policies, no secret tokens in the browser.

## Go / no-go release gates

### Gate 1 - controlled local/internal pilot

- [x] Multi-organization core, demo, unified conversations, CRM and staff roles.
- [x] First-party website chat, admin and visitor apps, end-to-end script and API tests.
- [x] Separate outbox worker in Docker config, uncertain-delivery reconciliation.
- [x] Migrations on SQLite and static TypeScript compilation.
- [ ] Repeat physical-device browser checks, accessible UX audit, and security review of legacy React runtime.

### Gate 2 - single-company website-chat beta

- [ ] Upgrade React 16 to a maintained dependency version and verify the build.
- [ ] Start Docker Compose with PostgreSQL on an owned test server; verify migration, back-up/restore and worker recovery.
- [ ] Add persistent multi-node abuse prevention (Redis/WAF), email verification, password reset and session administration.
- [ ] Add telemetry, error capture, queue alerts, log scrubbing and uptime targets.
- [ ] Verify CSP embedding on at least three real customer website stacks.

### Gate 3 - verified external messaging channels

- [ ] Avito business permission and real message read, send, sync, refresh and failure test with an authorized owner.
- [ ] Instagram professional-account API permission/App Review, webhooks, user-initiated messaging restrictions, test sends and account changes.
- [ ] WhatsApp Business Platform identity, phone-number registration, customer-service window, approved templates and media flow.
- [ ] Per-provider capability flags, rate limiting, error dashboards and reconciliation playbooks.
- [ ] Provider policy/terms and regional restrictions verified at each deployment; no informal scraping.

### Gate 4 - subscription SaaS beta

- [ ] Contract and privacy review: jurisdiction, DPA, right-to-delete/export, retention and transfer restrictions.
- [ ] Payment processor selected by operating entity; checkout, subscription state, tax/invoices, suspension/grace periods and webhook replay.
- [ ] Managed secrets, key rotation, MFA/SSO pathway, audit retention and verified billing entitlements.
- [ ] RU/EN interface localization and accessibility review throughout the app (visitor widget is already RU/EN).

### Gate 5 - international growth

- [ ] Multi-region data residency, SLA/SLO, formal incident response and external security evaluation.
- [ ] Worker pools, broker queue, load tests, horizontal scale and HA/DR drills.
- [ ] Self-serve org onboarding, full event analytics, developer API, app marketplace, customer success workflow.
- [ ] Supported account integrations expanded based on actual partner approvals, not merely connector names.

## Suggested monetization experiments (not implemented prices)

- Starter: individual operators with 1-2 owned website channels.
- Business: team workflow with CRM, analytics, assignment and standard rules.
- Professional: more accounts, advanced workflows, integration diagnostics and SLA policies.
- Enterprise: SSO, data residency, approval workflows, advanced support and integration contracts.

Validate willingness to pay through a measured beta: obtain an explicit baseline of lost contacts, time-to-first-reply and conversion before and after adoption. No revenue numbers or product-market fit are claimed at this stage.
