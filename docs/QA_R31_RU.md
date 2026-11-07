# QA R31 — локальная проверка защищённой входящей очереди

**Локальные проверки, 5 ноября 2026:** без реальных аккаунтов соцсетей, production-сервера и настоящего PostgreSQL. Полная регрессия: **262/262 теста прошли в 32 независимых модулях**, каждый процесс завершился с кодом 0.

## Новые сценарии

`PYTHONPATH=backend:. PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q -p pytest_asyncio.plugin backend/tests/test_r31_durable_inbound.py`

- Подписанный Instagram webhook сохраняется, его повтор идемпотентен; принятая запись не содержит текста сообщения.
- Отказ сразу после надёжной записи WhatsApp оставляет зашифрованное событие для worker, который восстанавливает переписку.
- Пять неудачных попыток, журнал причины, ручной возврат с проверкой прав и CAS, успешная обработка после исправления.
- Восстановление захвата после аварии и защита от повторной записи старого сообщения.
- Роли, изоляция компаний, срок хранения, удаление рабочей области и отклонение некорректных подписанных событий.
- Пятый потерянный claim переводится в `failed`, не зависает навсегда.

## Схема и миграция

- `DATABASE_URL=sqlite:///... alembic -c backend/alembic.ini upgrade head`
- `DATABASE_URL=sqlite:///... alembic -c backend/alembic.ini check`
- `python scripts/verify_r31_upgrade.py`: заполненная схема R30 с клиентом, перепиской и сообщением сохранена после обновления, новая таблица `inbound_jobs` создана.

## Настоящий браузер

`PYTHONPATH=backend:. python scripts/browser_r31_inbound_recovery.py` — Chromium на 1512×950, 390×844 и 320×700; ручной возврат, API, SQL worker и обновление статуса. Скриншоты: `docs/preview-r31-inbound-recovery-{desktop,mobile,phone320}.png`.

## CI, НЕ проверенное локально

`scripts/verify_r31_postgres.py` — только PostgreSQL 16 с отдельными ОС-процессами, распределённый `INSERT ON CONFLICT` и atomic claim. Включён в `.github/workflows/ci.yml` как требуемая проверка, **не утверждается как прошедший**.

Ограничения: legacy React runtime, тестовый Chromium вместо физических устройств, отсутствие живого провайдера. Все скриншоты — тестовые данные. Полный процесс pytest ранее иногда зависал, поэтому проверяем каждый модуль отдельно с кодом выхода 0.

## Итог локальной регрессии

`PYTHONPATH=backend:. PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q -p pytest_asyncio.plugin backend/tests/test_*.py` **НЕ** используется для объявления успешного общего прогона: в истории проекта единый процесс мог зависать на завершении. Для R31 каждый из **32 файлов `test_*.py`** запущен отдельным процессом; записаны коды выхода и суммы. Результат: **262/262 пройдено, 0 упавших модулей**.

- `backend/tests/test_r31_durable_inbound.py`: **11/11 PASS**.
- Проверка SQLite Alembic на чистой базе: `upgrade head` + `check`: **PASS** (`f31000a10001`, drift отсутствует).
- `python scripts/verify_r31_upgrade.py`: **PASS**, заполненная база R30 сохранила данные.
- `tsc --project frontend/tsconfig.json`: **PASS**; `node --check frontend/public/widget-client.js`: **PASS**.
- `python scripts/browser_r31_inbound_recovery.py`: **PASS** на 1512, 390 и 320 px с реальным локальным FastAPI, ручным возвратом и обработкой SQL-события.
- Конфигурация `.github/workflows/ci.yml` разобрана YAML-парсером: **PASS**.
- `scripts/verify_r31_postgres.py`: **НЕ запускался локально**, только добавлен как обязательный CI-тест; выполнение CI через GitHub не подтверждено.
