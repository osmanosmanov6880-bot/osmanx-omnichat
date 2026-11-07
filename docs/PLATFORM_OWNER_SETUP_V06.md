# OSMANX 0.6 — подготовка владельцем SaaS-платформы к подключению аккаунтов других компаний

> Эти действия выполняет **владелец платформы**, не каждый клиент отдельно. **Не выполнены на реальных внешних аккаунтах в текущем релизе.** Публикация и платёжные системы намеренно отложены.

## 1. Инфраструктура и шифрование

- Настройте защищённый домен и HTTPS (`PUBLIC_BASE_URL=https://chat.example.com`), корректную настройку callback и прокси, `COOKIE_SECURE=true`, `APP_ENV=production`, PostgreSQL, постоянное резервное копирование. Клиентам **не** требуется собственный сервер OSMANX.
- Задайте `INTEGRATION_ENCRYPTION_KEY` (Fernet), храните только в защищённом хранилище секретов; ключ используется для шифрования OAuth/access tokens и временных Page tokens. Не меняйте его без плана миграции/перешифрования.
- Прогоните миграции Alembic с резервной копией. В `d081e22a0b17` введён уникальный активный канал для одной внешней личности; при дублях миграция требует ручной безопасной сверки, а не смешивает данные компаний.
- Перед публичным запуском обновите React 16 на поддерживаемый стек, проверьте PostgreSQL/Docker, WAF/Redis-лимиты, аудит безопасности, резервное восстановление, шифрование резервных копий.

## 2. Meta — Instagram, Facebook Messenger, WhatsApp

Создайте Meta App, оформите Business Verification, запрашивайте соответствующие Advanced Access и App Review. Embedded Signup для клиентов как Solution/Tech Partner требует проверки приложения и разрешений **`business_management`, `whatsapp_business_management`** (плюс отдельные разрешения WhatsApp Messaging). См. официальный [Embedded Signup](https://www.postman.com/meta/whatsapp-business-platform/documentation/du6gzjv/embedded-signup). Это нельзя заменить токеном тестового разработчика.

Переменные платформы (значения — **только в secret store**, не в GitHub):

- `META_APP_ID`, `META_APP_SECRET`, `META_WHATSAPP_CONFIG_ID` — WhatsApp Embedded Signup; для одного общего приложения может использоваться тот же App ID, что и для Facebook Messenger.
- `FACEBOOK_APP_ID`, `FACEBOOK_APP_SECRET` — Facebook Login + Page API; если опущены, код использует META_APP_ID и META_APP_SECRET.
- `INSTAGRAM_APP_ID`, `INSTAGRAM_APP_SECRET` — Instagram Login и профессиональные DM; `INSTAGRAM_APP_SECRET_WEBHOOK` при отличии webhook секрета.
- `META_WEBHOOK_VERIFY_TOKEN` — секрет вызова GET challenge в Meta App Dashboard.
- `META_GRAPH_VERSION` — используемая API-версия Graph; проверяйте поддерживаемость перед выкладкой.

Callback URL в настройках приложений: `https://chat.example.com/api/integrations/oauth-callback/instagram` и `/api/integrations/oauth-callback/messenger`. Для Meta Webhooks настройте: `/api/webhooks/instagram`, `/api/webhooks/whatsapp`, `/api/webhooks/messenger`. Методы на стороне Meta и поля подписки должны соответствовать продукту и разрешениям конкретного приложения. OSMANX проверяет HMAC подписи исходного тела; неподписанные события отвергаются.

**WhatsApp:** Embedded Signup выдаёт code/WABA ID/Phone Number ID; код серверно обменивается на access token, номер проверяется через WABA phone_numbers; система вызывает WABA `/subscribed_apps`, сохраняет зашифрованный токен, ожидает подписанного входящего webhook. Дополнительно регистрация телефона с 6-значным PIN. Понадобятся системный пользователь, соответствующие права WABA, business verification и соблюдение требований Meta; в зависимости от модели партнёрства могут требоваться дополнительные операции с назначением системных пользователей и кредитной линией. Не заявляйте «готово», пока реально не протестировали.

**Instagram:** профессиональный аккаунт, правильный Instagram Login и scope `instagram_business_manage_messages`, глобальный Meta webhook и per-account subscription `me/subscribed_apps`. Только разрешённые обращения и допустимые окна обслуживания.

**Messenger:** `pages_show_list`, `pages_messaging`, `pages_manage_metadata`, `pages_read_engagement` и Page tasks с MESSAGING. Callback временно хранит список страниц зашифрованным, клиент сам выбирает нужную страницу, после чего OSMANX подписывает её на события. Подписанное входящее подтверждает подключение; обычный Facebook-профиль не подключается как личная переписка.

## 3. Авито

Нужны `AVITO_CLIENT_ID`, `AVITO_CLIENT_SECRET` и право на Messenger API в соответствующем бизнес-аккаунте. Callback: `/api/integrations/oauth-callback/avito`. OAuth привязывается к конкретному владельцу и рабочему пространству, обрабатывает одноразовый state. После OAuth канал имеет статус `pending_sync` — первая успешная синхронизация через разрешённое Avito API переводит его в подключённые. Эта интеграция **не прошла живую проверку** с выданными Avito правами.

## 4. Telegram, VK, MAX

У каждого клиента свой бот/сообщество и токен. После серверной проверки токена OSMANX выдаёт HTTPS endpoint **с идентификатором конкретного канала** и создаёт уникальный секрет; webhook регистрируется только после явного действия клиента.

- Telegram: `POST https://api.telegram.org/bot<TOKEN>/setWebhook`, `secret_token`, `X-Telegram-Bot-Api-Secret-Token`; [официальный Bot API](https://core.telegram.org/bots/api).
- VK: сообщество, Callback API confirmation code и secret, событие `message_new`, сообщение через `messages.send`. Проверьте соответствие правам сообщества и доступной версии API.
- MAX: HTTPS вебхук (официальная документация требует порт 443), `X-Max-Bot-Api-Secret`; [официальные инструкции](https://dev.max.ru/docs-api/methods/POST/subscriptions/).

## 5. Приёмка каждой интеграции — обязательный gate

1. Пройти авторизацию **реальным разрешённым аккаунтом компании**.
2. Подтвердить идентичность через официальный API без вывода токена клиенту.
3. Получить подписанное, не поддельное входящее сообщение.
4. Убедиться, что оно попало только в Inbox нужной компании и не продублировалось при повторном webhook.
5. Отправить ответ из OSMANX и проверить его в исходной социальной сети.
6. Проверить истёкший токен, отзыв доступа, ограничения 24-часового окна, неверные подписи, тайм-ауты, неизвестный результат отправки, отключение аккаунта и восстановление.
7. Зафиксировать официальное одобрение, дату, версию API и тестовый протокол до разрешения клиентских аккаунтов на production.

## 6. Что пока не является готовым

App Review и одобрения Meta, лицензирование Авито, полноценная отправка вложений, шаблоны WhatsApp вне окна обслуживания, сертификаты/сетевые webhooks в настоящем интернете, нагрузочные тесты, восстановление PostgreSQL, поддерживаемый React, юридическая проверка DPA/трансграничной передачи данных. Публичная публикация и биллинг по решению пользователя отложены.

**Не передавайте App Secret, access token или .env в чат, клиенту, скриншоты и публичный репозиторий.**
