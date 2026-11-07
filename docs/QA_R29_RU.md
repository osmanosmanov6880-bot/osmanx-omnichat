# Протокол проверки OSMANX OMNICHAT R29

Дата: 5 ноября 2026 г. Среда: Python 3.13.5, Node.js 22, TypeScript CLI, FastAPI + SQLite, локальный Chromium через Playwright.

| Проверка | Результат | Предел достоверности |
|---|---|---|
| Серверная регрессия R19–R29 | **226/226 тестов пройдено**, 11 независимых процессов pytest, код 0 | SQLite / локальные тестовые API, без реальных соцсетей |
| Новые проверки R29 | **9/9** | Атомарные обновления, stale-ORM, идемпотентность, исторические сообщения, CAS, права компании |
| Сквозной браузер R29 | **3/3**, ПК 1512 px, телефон 390 px, узкий телефон 320 px | Настоящий React UI/compiled JS + FastAPI TestClient, без сетевого подключения провайдера |
| Гонка «просмотр → новое сообщение → прочитано» | **409 + автоматическое обновление + счётчик 2 сохранён**, во всех трёх видах | Событие тестово добавлено в действующую SQL-базу между запросами |
| JavaScript errors | **0** во всех трёх видах | Проверка Chromium |
| Горизонтальное переполнение | **Не обнаружено** на всех трёх размерах | Проверка `scrollWidth - innerWidth <= 1` |
| `tsc --project frontend/tsconfig.json` | **PASS** | Текущая React 16 сборка; React 19 ещё не установлен |
| `node --check frontend/public/app.js` | **PASS** | Синтаксическая проверка готового JS |
| Alembic: `upgrade head` + `check` | **PASS, нет drift** | Свежая SQLite-схема R28, R29 миграций не добавляет |
| PostgreSQL: четыре конкурентные сессии | **Не выполнялось локально**; тест `scripts/verify_r29_postgres.py` подключён в CI | Нужен PostgreSQL и psycopg; не объявлять успешным без реального запуска |
| Соцсети/production/платежи | **Не проверялись и не публиковались** | Перед коммерческим выпуском требуется отдельный аудит и разрешённые live-интеграции |

## Что проверено на обновлении

- R29 не добавляет таблиц и не меняет форму существующих данных R28.
- Существующая история и входящие сообщения сохраняются; обновление использует существующие поля `conversations.unread_count`, `conversations.version`, `conversations.last_message_at`, `conversations.last_inbound_at`.
- Интерфейс должен обновляться **вместе** с API: только новый frontend передаёт версию реально показанного диалога и умеет корректно обработать `409`.
- Один процесс pytest ранее иногда зависал на teardown в исторических релизах. Поэтому CI использует независимые группы; все группы R29 вернули код 0.

## Браузерные доказательства

- `docs/preview-r29-incoming-race-desktop.png`
- `docs/preview-r29-incoming-race-mobile.png`
- `docs/preview-r29-incoming-race-phone320.png`

Скриншоты сделаны Chromium с **тестовыми сообщениями**, не являются сгенерированными изображениями интерфейса. Событие появляется после получения первоначального диалога и до `POST /read`, затем сервер отказывает в старом подтверждении.

## Как воспроизвести

```bash
PYTHONPATH=backend:. pytest -q backend/tests/test_r29_inbound_cas.py
PYTHONPATH=backend:. python scripts/browser_r29_unread_race.py
tsc --project frontend/tsconfig.json
DATABASE_URL=sqlite:///./r29-schema.db PYTHONPATH=backend:. alembic -c backend/alembic.ini upgrade head
DATABASE_URL=sqlite:///./r29-schema.db PYTHONPATH=backend:. alembic -c backend/alembic.ini check
```

Для PostgreSQL через CI требуется запустить job `postgres-migrations` на настоящем сервисе PostgreSQL 16. Скрипт `scripts/verify_r29_postgres.py` явно откажет, если подставить SQLite.
