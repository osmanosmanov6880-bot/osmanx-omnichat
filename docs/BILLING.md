# SaaS billing and entitlements

- **Starter**: 1 user, 2 connections; analytics unavailable, automation creation disabled.
- **Business**: up to 10 users, 5 connections; analytics and team.
- **Professional**: up to 100 users, 30 connections; automation rules, advanced operations.
- **Enterprise**: entitlement limits set high; enterprise security, SLA, SSO, custom external API are **not implemented yet**.

These limits are enforced on the server on invite and connection creation and analysis/rules access. They are not a substitute for signed payments and entitlements verification. There is a `BillingEvent` table scaffold, but **no checkout, payment provider, invoice ledger, billing webhooks, renewals, cancellation, taxes or self-serve plan changes**. Organization.plan must currently be changed by a trusted administrator directly in DB after manual agreement; never expose such change to ordinary users.

Recommended future billing architecture: trusted payment-service webhooks, idempotent billing event queue, entitlement transition workflow, grace periods, immutable subscription receipts and separation of authorization from browser UX. Choose provider and jurisdictions with proper tax/legal due diligence.
