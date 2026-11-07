# Архитектура OSMANX OMNICHAT v0.2

## Топология

```text
                 React/TypeScript Web UI (desktop/mobile)
                           |
                   HTTPS + HttpOnly cookie
                           |
                 FastAPI / Auth middleware
                           |
       +-------------------+------------------+
       |                   |                  |
  Inbox / CRM         Rules / Analytics     /api/ws
       |                   |                  |
       +-------------------+------------------+
                           |
                   SQLAlchemy (tenant scoped)
                           |
                PostgreSQL or local SQLite
                           |
             +-------------+--------------+
             |                            |
        OutgoingJob worker          Incoming adapters
             |                            |
    Avito / IG / WhatsApp      Avito polling; verified
      official send APIs         Meta HMAC webhooks
```

### Data ownership

Organization has independent memberships, connections, contacts, conversations, messages, notes, rules, templates, jobs, billing events and audit events. The AuthSession stores a hashed random token and selects exactly one active organization. Access checks always compare `organization_id` and the active membership role. A manager/operator can only read assigned conversations and associated contacts, while lead/admin/owner can read the organization.

**Identity never inferred by display name.** `ContactIdentity(channel_id, external_user_id)` maps the platform-scoped user to a CRM contact. Cross-platform merge is an explicit authorized action. Concurrent identical external messages are deduplicated by `(conversation_id, external_id)`; repeated employee sends by `(conversation_id, client_nonce)`.

### Inbound pipeline

1. WhatsApp/Instagram POST `/api/webhooks/{provider}` receives raw body, verifies `X-Hub-Signature-256` against configured Meta App Secret.
2. The request resolves a **verified connected channel** using the provider account ID. Events for unknown channels are ignored.
3. `ingest_inbound` upserts tenant-isolated contact identity and conversation, deduplicates external IDs, increments unread/version and applies enabled rules. Transaction commit persists the normalized message.
4. Avito uses the approved OAuth account and `getChatsV2` + `getMessagesV3` polling. Historical messages have `history=True` to prevent fake new-unread counts or repeated automation.
5. WebSocket clients receive an invalidation signal, then refresh via authenticated HTTP API. 7-second polling is a network-failure fallback.

### Outbound pipeline

1. UI sends text, `expected_version` and unique `client_nonce` with CSRF token.
2. Server checks tenant/assignment, channel-specific text limit and permitted message window.
3. Atomic conditional `UPDATE conversations WHERE version=?` rejects simultaneous conflicting replies with HTTP 409.
4. Demo message is delivered to **test DB only**; live message and SQL OutgoingJob are committed atomically.
5. One worker claims due jobs, calls the official provider, stores acceptance ID, records failures and eligible retry backoff.
6. A POST timeout, ambiguous provider response or crashed in-flight worker is quarantined with `uncertain` delivery state and **never automatically retried**; owner/admin can reconcile it with evidence via `/api/operations/outbox/{id}/resolve`.

Current SQL worker and in-process limiter are appropriate for controlled MVP deployments with **one application worker**. Production horizontal scaling requires a separately deployed dispatcher, durable dead-letter reporting, per-channel rate limits and backpressure.

### Universal adapter contract

Each adapter implements: `connect`, `disconnect`, `get_conversations`, `get_messages`, `receive_messages`, `send_message`, `refresh_credentials`, `get_capabilities`. An adapter cannot use bypass/scraping. Envelope: `{organization_id, channel_id, external_chat_id, external_id, sender_id, direction, kind, body, attachment, created_at}`. Extensions must preserve tenant scope and idempotency.

### Important architectural differences

The master prompt *suggested* Next.js, NestJS, Prisma, Redis and BullMQ. This deliverable uses React/TypeScript + FastAPI + SQLAlchemy + SQL transactional outbox because the available environment lacks npm package downloads. The GitHub project can be upgraded or migrated; do not claim the suggested stack has been built.


## v0.3 first-party website channel and operations

The first-party channel is not an Avito/Instagram/WhatsApp proxy. It comprises `backend/app/website.py`, `frontend/public/embed.js`, external `frontend/public/embed.css`, `widget.html`, `widget.css`, `widget-client.js`, and two new organization-scoped tables `website_widgets`, `website_visitors`. Each `WebsiteWidget` owns exactly one `ChannelConnection(provider=website)`; a visitor gets a random bearer token whose SHA-256 is stored, and is bound to one conversation. Operator replies use the existing message normalization model directly, without enqueueing an external API send. Authorized external provider sends still use the outbox and require remote delivery evidence.

The timed conversation ownership lease (`reply_lock_owner_id`, `reply_lock_expires_at`) uses a SQL conditional update and increments conversation version. A reply is rejected if a different active lease owner holds the conversation; the existing optimistic `expected_version` is still required for actual send.

`backend/app/operations.py` and `/api/operations/outbox` expose only organization-scoped state, not external credentials. `backend/app/worker.py` is the independent background process in `docker-compose.yml`, while local development may continue to run the worker in the main API process. This is a single-worker architecture, not a horizontally scaled broker.

International groundwork is in `organizations.currency`, `organizations.timezone`; the analytics query groups daily inbound events by configured IANA timezone. Revenue amounts remain human-entered fields, not invented conversions.


## v0.4: командный центр и управляемая очередь

Слой `backend/app/command.py` не зависит от AI и внешних площадок. Он использует текущие `Conversation`, `Message`, `Membership`, `AuditLog` и новые `SavedInboxView`; хранит приоритеты и фильтры в PostgreSQL/SQLite, проверяет org и права на сервере. Композитные индексы поддерживают сортировки по организации, активной очереди, приоритетам и времени исходящих сообщений. При запросе `/api/command-center` последняя исходящая активность для последних 500 обращений определяется агрегирующим SQL вместо отдельных запросов для каждого диалога. Сериализуются только первые 25 приоритетных кандидатов. Подробнее: [COMMAND_CENTER.md](COMMAND_CENTER.md).
