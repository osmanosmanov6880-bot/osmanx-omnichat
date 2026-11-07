# Security review and data protection

## Implemented controls

- Passwords: per-user salted `scrypt` hashes; no passwords logged or returned.
- Auth: 48-byte random opaque session cookies, SHA-256 hash at rest, HttpOnly/SameSite=Lax, CSRF synchronizer token per session, 7-day TTL.
- RBAC: checked on API/server and every conversation/contact query, not only in React.
- Tenant isolation: organization-scoped SQL rows, manual contact linking only, webhook channel-to-tenant resolution.
- Integration secrets: `cryptography.Fernet` encrypted with user-provided `INTEGRATION_ENCRYPTION_KEY`; no secrets in frontend.
- Meta webhooks: compare HMAC SHA-256 against raw request body; dedup by hashed external IDs.
- OAuth: random 600-second `state` with org/user-bound state validation; code exchanged server-side only.
- Output: React escapes messages; attachments fetched via tenant-authenticated proxy for WhatsApp and Meta domain allowlist; no inline scripting in CSP.
- Server sends `X-Frame-Options:DENY`, `X-Content-Type-Options:nosniff`, CSP, restrictive Permissions-Policy.
- Signed text: channel-specific limits; default client-service window checks.
- Auditing: recorded employee operations, notes, assignments, invites, changes; tenant-specific export/deletion.
- Production mode refuses insecure cookies or HTTP `PUBLIC_BASE_URL`.

## Known security and privacy gaps: block public paid launch

1. Vendored React **16.0** is out of support; upgrade to actively supported React and dependencies, re-test end-to-end browser behavior. Offline environment prevented dependency retrieval.
2. There is no password reset, MFA, session administration UI, SSO/SCIM or verified e-mail ownership flow.
3. In-process per-IP throttling does not survive multiple instances; move to shared Redis/WAF limits for production, add abuse monitoring.
4. No independent penetration test, SAST/DAST audit, supply-chain audit or legal/privacy review has been performed.
5. Row-level tenant isolation is application enforced; PostgreSQL RLS policies could add defense-in-depth.
6. The WebSocket uses a 2-second authenticated DB check; scaling and authorization changes need load tests. Verify trusted proxy headers and Origin before external launch.
7. Complete data retention / legal holds / export requests and deletion policies need legal review; current retention deletes messages and notes, not every category or every provider-side copy.
8. Single Fernet key with no rotation/versioning; add managed secrets and a rotation plan before onboarding customers.
9. Webhook retries under concurrent deliveries may create unique-index conflict responses; add external queue and retry-aware webhook ACK strategy.
10. Media URL allowlists and attachment malware scanning must be reviewed for all real accounts and formats.
11. Logs currently use standard Python/Uvicorn, not a full observability/SIEM pipeline.
12. The API supports multiple organizations but does not implement self-service organization creation/switching UX beyond memberships.

## Production hardening checklist

- `APP_ENV=production`, `COOKIE_SECURE=true`, HTTPS domain, `PUBLIC_BASE_URL` matches external origin.
- Secrets in vault (or tightly protected environment), distinct app secrets for each Meta App and no public upload of `.env`.
- Restrict Postgres network access, regular TLS cert renewals, encrypted daily backups, restore rehearsal.
- HTTPS, HSTS, WAF, minimum necessary firewall ports, dependabot updates and CI vulnerability scans.
- Explicit legal basis, retention settings, access audit, breach reporting process, data processing agreement.
- Simulate malicious cross-tenant ID queries, CSRF, replay, callback state reuse, forged Meta events, log secret leakage.


## Additional v0.3 controls and caveats

- `X-Frame-Options: DENY` remains on application views, but is intentionally removed from **widget iframe routes only**. The widget has a dynamic, narrowly scoped `frame-ancestors` CSP derived from validated merchant HTTPS origins.
- Website visitor secret tokens are 48-byte randomly generated values, hashed in storage, not embedded in the installation script. The public widget ID cannot fetch private conversations.
- Staff timed leases are enforced on the server and with a versioned database compare-and-swap; UI buttons are not the security boundary.
- Public widget creation uses per-IP throttling; message sending is throttled per verified visitor. Shared cross-instance limits, bot prevention, request budgets and DDoS protection are **not** included and block an open public deployment.
- The launcher serves CSS externally to avoid inline-style CSP exceptions. Merchant domains still must allow the script, stylesheet and iframe origins explicitly.
- Third-party token validation is not equivalent to provider E2E verification. Reconcile uncertain provider POST outcomes with independent evidence; never send them again automatically.
- React 16 remains unmaintained, and privileged access recovery/MFA, Redis/WAF quotas, SAST/DAST, data residency and actual restore tests remain outstanding.

## Обновление v0.6 — customer-owned accounts

- Добавлен self-service multiple-org и выбор только тех Facebook Pages, которые пользователь предоставил через собственную OAuth-сессию. Access token страниц зашифрован и временно хранится до истечения TTL; TTL-уборщик и удаление организации очищают эту таблицу.
- Частичный уникальный SQL-индекс не допускает активной привязки одной внешней идентичности сразу к нескольким организациям.
- WhatsApp Embedded Signup использует одноразовый state, привязанный к организации и владельцу. Browser-supplied WABA/Phone Number ID проверяются официальным API: произвольный ID не может подменить аккаунт.
- Диагностика не возвращает токены. VK confirmation/secret может получить только owner/admin по отдельному явному запросу, поэтому их нельзя показывать в логах/скриншотах.
- Сохраняется HMAC проверка Meta Webhooks; статус `connected` устанавливается только после проверенного входящего (или успешного sync Авито), а не после входа в аккаунт.
- Панель поддерживает разрешённый `connect.facebook.net` для Embedded Signup только на `/`; страницы виджетов и API не разрешают посторонние скрипты.
- **Остающиеся обязательные production-gates:** React 16 upgrade, OAuth/App Review, Postgres RLS defense in depth, MFA/recovery, Redis/WAF, SIEM, storage encryption and key rotation, DPA/GDPR/legal review, signed webhooks+outgoing live tests, data retention and restore drills.
