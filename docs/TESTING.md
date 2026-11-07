# Test procedures - OSMANX OMNICHAT v0.4.0

Run from the repository root, using installed Python/TypeScript and, for browser tests, Playwright + Chromium.

```bash
PYTHONPATH=backend pytest -q backend/tests
# 34 passed

tsc --project frontend/tsconfig.json
# exit status 0

DATABASE_URL=sqlite:////tmp/omnichat-world-schema-qa.db PYTHONPATH=backend alembic -c backend/alembic.ini upgrade head
DATABASE_URL=sqlite:////tmp/omnichat-world-schema-qa.db PYTHONPATH=backend alembic -c backend/alembic.ini check
# no new upgrade operations detected

python scripts/browser_world_e2e.py
# CHROMIUM_APP_AND_WIDGET_ROUNDTRIP=PASS
# CHROMIUM_MOBILE_WEBSITE_PAGE=PASS
# UNAUTHENTICATED_VISITOR_READ=401
# JAVASCRIPT_ERRORS=[]
```

The browser script uses actual React and visitor widget assets with a **real FastAPI TestClient** (no mock response fixtures). The Chromium environment has an administrator navigation restriction, therefore the browser request transport is bridged in-process. Physical server/network, CSP on merchant websites, real PostgreSQL and HTTPS E2E remain separate tests to perform before launch.

`backend/tests` verifies authentication and CSRF, plan quota checks, cross-organization boundaries, webhooks signature and replay protection, no automatic uncertain replay, CRM, team rules, audit, data deletion, website visitor confidentiality, idempotent messages, lease ownership, IANA timezone and revenue currency safeguards, and operational dashboards.

`python scripts/visual_smoke.py` remains available as a fast offline fixture-backed rendering smoke test; unlike `browser_world_e2e.py` it does **not** call the real backend for screen interactions.

Recommended release-blocking tests: live authorized provider account E2E, Docker Compose startup, Postgres migrations and rollback, worker crash recovery, full-text search at volume, keyboard + screen reader navigation, CSP against real merchant sites, genuine mobile Safari/Chrome, penetration test, rate limiting behind reverse proxies, and backup restore drill.


## Проверка v0.4: рабочие экраны и центр управления

```bash
python scripts/browser_v04_e2e.py
# V04 REAL-BACKEND CHROMIUM: desktop command, priority, saved views,
# visitor roundtrip, responsive mobile: PASS
# JS errors: []
# Mobile overflow: 0
```

Сценарий дополнительно проверяет изменение приоритета с optimistic version, создание и применение сохранённой подборки, светлую/тёмную тему, русский сайт-виджет, реальную передачу visitor → Inbox → оператор → visitor через TestClient и открытие переписки из мобильной приоритетной очереди. Для этого сценария используются Playwright и Chromium, обычно не необходимые для запуска самого приложения.

Новые тесты `test_command_center.py` проверяют роли, чужую организацию, серверную очередь, конфликт версий, фильтры и литеральный SQL-поиск по сообщениям до LIMIT.
