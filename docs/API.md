# API quick reference · v0.3.0

All APIs are under `/api`. Browser auth uses cookie `omnichat_session` (HttpOnly) and double-submit CSRF token. For any write request after login/demo, send the readable `omnichat_csrf` cookie value as `X-CSRF-Token`. Never store OAuth tokens in browser localStorage.

| Task | Method | Endpoint |
| --- | --- | --- |
| Register a new owner/organization | POST | `/auth/register` |
| Login / logout | POST | `/auth/login`, `/auth/logout` |
| Open isolated demo workspace | POST | `/demo/start` |
| Current user/role/org | GET | `/auth/me` |
| Switch to authorized organization | POST | `/auth/switch/{organization_id}` |
| Conversations, search/filter | GET | `/conversations?q=&channel=&status=&assigned=&archived=&pinned=` |
| Chat, notes and messages | GET | `/conversations/{id}` |
| Reply, optimistic lock, idempotency | POST | `/conversations/{id}/reply` |
| Mark read/unread | POST | `/conversations/{id}/read`, `/conversations/{id}/unread` |
| Status / pin / assign | PATCH | `/conversations/{id}/status`, `/pin`, `/assign` |
| Team and invitations | GET, POST | `/team`, `/team/invite`, `/team/accept-invite` |
| Contacts and pipeline | GET/PATCH | `/contacts`, `/contacts/{id}` |
| Manual identity merge | POST | `/contacts/{target_id}/merge/{source_id}` |
| Reporting and SLA | GET | `/analytics`, `/alerts` |
| Rules | GET/POST/PATCH | `/rules`, `/rules/{id}` |
| Quick replies | GET/POST/DELETE | `/quick-replies`, `/quick-replies/{id}` |
| Connections | GET | `/integrations` |
| Avito / IG OAuth | POST / GET | `/integrations/oauth-start/{provider}`, `/integrations/oauth-callback/{provider}` |
| WhatsApp official token setup | POST | `/integrations/manual` |
| Avito sync | POST | `/integrations/{id}/sync` |
| Disconnect | POST | `/integrations/{id}/disconnect` |
| WhatsApp/Instagram webhook ingress | GET / POST | `/webhooks/{provider}` |
| Inbox refresh stream | WS | `/ws` |
| Queue operational status | GET | `/operations/outbox?status=uncertain` |
| Manual resolve unknown send | POST | `/operations/outbox/{job_id}/resolve` |
| Export / delete org data | GET / POST | `/organization/export`, `/organization/delete` |
| Service health | GET | `/health`, `/health/ready` |

## Example reply

```http
POST /api/conversations/CONVERSATION_ID/reply
X-CSRF-Token: <csrf cookie value>
Content-Type: application/json

{"body":"Здравствуйте, с радостью поможем!", "expected_version": 4, "client_nonce":"unique-random-id-per-send-123"}
```

The nonce must remain constant on retried UI requests; `expected_version` comes from the currently displayed conversation. A stale version returns **409** rather than silently overwriting another operator. Live sends are queued; an HTTP **201** means the message was stored locally, **not** confirmed delivered by the external service.

## Unknown delivery handling

On a provider POST timeout, ambiguous 5xx error, or crashed claimed worker, a job is marked `uncertain` and not automatically retried. Owner/admin verifies delivery in the provider, then calls `POST /api/operations/outbox/{job_id}/resolve` with `{"status":"accepted"|"failed", "evidence":"how delivery was verified", "external_id":"optional confirmed provider id"}`. This operation is tenant-scoped and audited. Do not mark `failed` and blindly resend until uncertain provider status is independently verified.

Full OpenAPI is at `/api/docs` in development (controlled by `ENABLE_API_DOCS`). Treat routes not listed in this summary according to the generated schema.


## v0.3 first-party website messaging, collaboration and operations

Session-authenticated (same CSRF and RBAC as the rest of `/api`):

| Verb | Path | Role | Purpose |
| --- | --- | --- | --- |
| GET | `/api/website-widgets` | owner/admin/lead | List company-owned widgets |
| POST | `/api/website-widgets` | owner/admin | Create widget + channel; enforces plan quota |
| PATCH | `/api/website-widgets/{id}` | owner/admin | Change origin list, design and enable state |
| POST | `/api/website-widgets/{id}/rotate-key` | owner/admin | Revoke public embed URL |
| POST | `/api/conversations/{id}/claim` | staff with conversation access | Conditional reply lease, 30-600s |
| POST | `/api/conversations/{id}/release` | lease holder | Release own lease |
| GET | `/api/operations/overview` | owner/admin/lead | Organization queue/channel stats |
| GET | `/api/operations/outbox` | owner/admin/lead | Organization outgoing jobs |
| POST | `/api/operations/outbox/{id}/resolve` | owner/admin | Evidence-backed manual reconciliation |
| GET | `/api/organization/localization` | owner/admin | IANA timezone + ISO currency options |
| PATCH | `/api/organization/localization` | owner/admin | Update locale basis; reject invalid currency reinterpretation |

Public widget (not employee-authenticated):

| Verb | Path | Purpose |
| --- | --- | --- |
| GET | `/api/public/widget/{key}/bootstrap` | Public theme and greeting |
| POST | `/api/public/widget/{key}/session` | Create private visitor token |
| GET | `/api/public/widget/{key}/messages` | Read own messages with `X-Widget-Session` |
| POST | `/api/public/widget/{key}/messages` | Send own inbound message, nonce required |
| GET | `/widget/{key}` | Frameable visitor chat HTML, origin-restricted CSP |
| GET | `/assets/embed.js` + `/assets/embed.css` | Drop-in website launcher |

See `WEBSITE_CHAT.md` for full setup and limitations. No new endpoints attest that external Meta or Avito accounts were connected.


## v0.5: новые официальные бот-каналы

- `POST /api/integrations/bots` — авторизованный владелец/админ, body: `provider` (telegram/vk/max), `access_token`, для VK `group_id`, `confirmation_token`. В случае успешной **проверки токена** создаёт канал `pending_webhook`, но не объявляет реальную доставку проверенной.
- `POST /api/integrations/{id}/activate-webhook` — явное действие владельца/админа; Telegram `setWebhook` или MAX `/subscriptions`, только при HTTPS `PUBLIC_BASE_URL`. После подписки остаётся `pending_webhook` до проверенного входящего события. VK требует ручной настройки Callback API.
- `POST /api/webhooks/telegram/{id}` — проверяется `X-Telegram-Bot-Api-Secret-Token`.
- `POST /api/webhooks/vk/{id}` — проверяются секрет и `group_id`; поддерживается `confirmation` с возвращением кода сообщества, `message_new`.
- `POST /api/webhooks/max/{id}` — проверяется `X-Max-Bot-Api-Secret`; поддерживается `message_created`.

Новые каналы имеют общий контракт `adapter_for`, `ingest_inbound` и `process_outbox`. У сервисов нет прав для доступа к произвольным личным перепискам пользователей.


### R29: подтверждение прочтения без гонки с входящим

`POST /api/conversations/{conversation_id}/read`

Тело обновлённого клиента: `{ "expected_version": 17 }`. Успех: HTTP 200, `{ "ok": true, "version": 18 }`. Если за время открытия переписки пришло новое сообщение, версия диалога изменяется: HTTP **409**; клиент обязан повторно получить переписку и не стирать новые непрочитанные сообщения. Проверяются компания и актуальное назначение оператора. Старые клиенты без тела запроса поддерживаются, но при обновлении UI рекомендуется отправлять `expected_version`.


## R31 — защищённая очередь входящих

- `GET /api/operations/inbound?status=failed` — только owner/admin/lead, максимум 100 метаданных записей своей компании. Без текста сообщения, шифротекста, подписи, номера и provider token.
- `POST /api/operations/inbound/{id}/retry` — только owner/admin с CSRF и JSON `{"reason":"..."}` (8–300 символов). Допустим только переход `failed` → `queued` с CAS и аудитом; **не отправляет исходящий ответ**.
- `GET /api/operations/overview` — новые tenant-scoped поля `inbound`, `inbound_duplicates_recorded_24h`, `inbound_oldest_pending_seconds`.
- Входящие подписанные webhook `/api/webhooks/{...}` сначала пишут encrypted normalized event в БД, затем пытаются обработать. JSON `accepted` показывает **немедленно сохранённые новые сообщения**, а не общее число событий, уже зафиксированных на будущую обработку.

Миграция `f31000a10001`, восстановление `backend/app/inbound_jobs.py`, инструкции `docs/RELEASE_R31_DURABLE_INBOUND_RU.md`.
