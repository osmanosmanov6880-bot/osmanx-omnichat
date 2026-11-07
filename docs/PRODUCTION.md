# Runbook: deployment and operations

## Requirements

Linux host with Docker Engine + Docker Compose, domain/DNS, ports 80/443, protected persistent disk, operator access. The Docker configuration was **not executed in this build environment**; validate on your server before production use.

## Initial deployment

1. `cp .env.example .env` and set strong **URL-safe** `POSTGRES_PASSWORD`, `PUBLIC_HOST=chat.yourdomain.com`, `PUBLIC_BASE_URL=https://chat.yourdomain.com`, `APP_ENV=production`, `COOKIE_SECURE=true`, `ENABLE_API_DOCS=false`.
2. Generate a Fernet encryption key and place only in protected secret store: `python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'`.
3. Configure DNS A/AAAA; only expose ports 80/443 via Caddy; app binds to 127.0.0.1:8000 for loopback-only direct access.
4. `docker compose --profile https up --build -d`.
5. `docker compose logs -f app` and check `GET /api/health/ready` via HTTPS.
6. Go through registered callback URLs in Meta/Avito dashboards; validate signed webhooks and live account scope.
7. Invite test operators, perform authorized conversation QA, role isolation and backup restore tests.

## Health and monitoring

- Liveness `GET /api/health`; readiness `GET /api/health/ready` checks SQL connectivity.
- Review `/api/operations/outbox?status=uncertain` daily; do not resend an unknown external delivery until confirmed. Owner/admin can reconcile via API with an audit note.
- Log `app` errors, 5xx/429 rates, webhook signature failures, `outgoing_jobs` queue depth/retry counts, synchronization errors, memory/CPU and DB latency.
- Set an alert on worker exceptions and on growing failed/queued outbox rows. No preconfigured Prometheus/Grafana dashboard is included; add your monitoring stack.
- v0.3 runs a separate **worker** service under Docker Compose. The local shell start still enables an in-API background worker. Use only one outbox worker until multi-node claiming, crash recovery and queue scaling are tested.

## Backup and restore

The v1.5 backup tool stops on `pg_dump` errors, checks `pg_restore -l`,
and publishes a SHA-256 manifest. Archives are PostgreSQL custom format, not
the earlier `sql.gz` format:

```bash
./infra/backup-postgres.sh
python3 scripts/backup_safety.py postgres-verify --file backups/YOUR_FILE.dump
```

The two files (`.dump` and `.dump.manifest.json`) must be stored together in
encrypted offsite storage. Keep permissions restricted and configure retention.
An archive listing is **not** proof of successful recovery: restore into a
separate test database and validate tables/data before trusting a release.
Never restore a backup over a live DB by piping it into a running production
database. No remote encryption or scheduled rotation is bundled.

Local SQLite development uses `backup_local_windows.bat` or
`./backup_local_linux.sh`. A consistent SQLite backup is made automatically
before a pending local Alembic schema upgrade. For inspection, use
`sqlite-verify` and `sqlite-restore-new --target NEW_FILE`. Never overwrite the
original file by hand without a separate recovery plan.

## Releases / rollback

- Back up DB before schema changes; review migration backward compatibility.
- GitHub Actions is configured to execute backend tests, TypeScript compilation and Alembic drift check; container build is separately dispatchable.
- Deploy an immutable tagged build, verify smoke tests and logs; restore DB snapshot before incompatible downgrade.
- Never run a destructive rollback on a populated production database without a tested recovery plan.


## v0.3 worker, website chat, and rollout verification

`docker compose up --build -d` now starts `postgres`, `app` and `worker`. The API container sets `ENABLE_OUTBOX_WORKER=false`; `worker` runs `python -m app.worker` after the application is healthy. The worker handles due outbound API jobs, Avito polling (if configured), and retention clean-up. Verify `docker compose ps`, `docker compose logs worker`, and actual queue processing before public rollout. Docker is **not** installed in this build environment; these runtime checks remain pending.

Set merchant iframe origins in **Sites / Web Chat** and make sure merchants explicitly allow your actual public domain in `script-src`, `style-src` and `frame-src`. The widget HTML emits dynamic `frame-ancestors`; test the merchant's effective CSP with DevTools before onboarding.

Use shared distributed rate limiting, quotas and abuse detection before publishing public visitor sessions. The current rate limiter is in-memory, and cannot be treated as production DDoS protection. Do not enable HTTPS/CDN proxy layers blindly: explicitly test cookie, CSRF, websocket Origin and forwarded headers.

The first production release requires supported React, live account validation for each enabled third-party adapter, a formal recovery/reset process, observability, Postgres backup restore, and an incident runbook. No billing provider is connected.


### v1.3: обязательная проверка миграции и доверенного прокси

Production API останавливается при отсутствующей или устаревшей версии Alembic. Перед запуском выполнить `alembic upgrade head`. Не направлять публичные запросы к Uvicorn в обход настроенного HTTPS-прокси. `TRUSTED_PROXY_CIDRS` можно включать только для настоящих внутренних прокси; не устанавливайте `0.0.0.0/0`. Подробности в `SCALING_AND_PROXY_RU.md`.
