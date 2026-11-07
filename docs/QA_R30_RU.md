# QA R30 — атомарное создание первой переписки

Дата: 5 ноября 2026. Проект: восстановленная ветка OSMANX OMNICHAT R19–R30. Контекст: локальные тестовые SQLite и Chromium, **без живых аккаунтов** и без production-развёртывания.

## Новые проверки R30

Команда: `PYTHONPATH=backend:. pytest -q backend/tests/test_r30_first_inbound_claim.py --disable-warnings`.

**25/25 прошли**. Проверены: первое создание одного клиента/диалога; повтор того же provider event ID; два разных чата одного клиента; одновременные первые сообщения; два одновременных повтора одного ID; два участника одной внешней беседы; изоляция двух организаций; 8 повреждённых provider timestamps; импорт истории без unread; отклонение слишком длинного ID без частичных записей; настоящий signed Telegram webhook с повтором; 6 повреждённых подписанных payload Telegram, VK и MAX; безопасное время MAX.

Проверка совместимости сразу с R29 и базовыми тестами ботов: `PYTHONPATH=backend:. pytest -q backend/tests/test_r30_first_inbound_claim.py backend/tests/test_r29_inbound_cas.py backend/tests/test_bot_channels.py` — **39/39 прошли**.

## Проверка интерфейса

- `PYTHONPATH=backend:. python scripts/browser_r30_first_contact.py`: **PASS** на 1512×950, 390×844 и 320×700. В каждой проверке два параллельных первых события создают один диалог с двумя сообщениями; повтор первого события не создаёт третье. Реальная страница приложения в Chromium связана с локальным FastAPI/SQLite.
- `PYTHONPATH=backend:. python scripts/browser_r29_unread_race.py`: **PASS** на трёх размерах, HTTP 409 и защита непрочитанного сохранены.
- `PYTHONPATH=backend:. python scripts/browser_wa_template.py`: **PASS** на трёх размерах, интерфейс WhatsApp-шаблонов не нарушен.
- Скриншоты: `docs/preview-r30-first-contact-desktop.png`, `-mobile.png`, `-phone320.png`.

## Сборка и БД

- `tsc --project frontend/tsconfig.json` — **PASS**.
- `node --check frontend/public/widget-client.js` — **PASS**.
- `python -m compileall -q backend/app scripts/verify_r30_postgres.py scripts/browser_r30_first_contact.py scripts/verify_r30_regression.py` — **PASS**.
- SQLite `alembic upgrade head`, `alembic check` и `assert_schema_current(engine)` — **PASS**, миграция R30 не нужна: уникальные ограничения уже существуют.
- `.github/workflows/ci.yml` проверен синтаксическим YAML-парсером — **PASS**, R30 API, браузер и PostgreSQL-тест включены.

## Полная регрессия

Проверка выполняется `PYTHONPATH=backend:. python scripts/verify_r30_regression.py`: каждый тестовый файл в отдельном процессе, проверяется **код выхода 0**, а не только строка `passed`. Переход на отдельные процессы нужен из-за нестабильных teardown при запуске всего набора в одном Python-процессе в данном окружении. **Полная регрессия завершена успешно: 251 из 251 теста, 31 из 31 модуля с кодом выхода 0.** Команда `PYTHONPATH=backend:. python scripts/verify_r30_regression.py` вывела `R30_ISOLATED_MODULE_REGRESSION=PASS 251 TESTS 31 MODULES`. Ранее единый процесс pytest неоднократно зависал при завершении, поэтому отдельные модули остаются обязательным способом проверки в локальной среде.

## PostgreSQL — не проверено локально

`scripts/verify_r30_postgres.py` добавлен к CI: настоящий PostgreSQL, четыре параллельных воркера на новом клиенте, три повтора одного события, два участника новой групповой беседы, контроль отсутствия лишних карточек. Локальная среда не содержит PostgreSQL и `psycopg`, поэтому **не заявляем PASS PostgreSQL**.

## Ограничения

Не выполнялись настоящие внешние отправки, полноценный пентест, проверка всех мобильных физических устройств, PostgreSQL production, новая сборка React 19, платежи и деплой. Сборка остаётся **локальным инженерным релизом**.
