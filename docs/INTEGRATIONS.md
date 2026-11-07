# Проверка интеграций и официальные ограничения

**Дата анализа:** 3 ноября 2026 года. **Состояние:** код адаптеров написан и смоделирован в тестах; официальные аккаунты и токены не предоставлялись, end-to-end с реальными каналами НЕ выполнен.

## Авито

Официальная документация: https://developers.avito.ru/api-catalog/messenger/documentation

- Для Seller Messenger API требуется бизнес-доступ и подходящий тариф (в зависимости от категории объявлений). Получить доступ и разрешения `messenger:read`, `messenger:write` через Авито для бизнеса.
- Реализованы Authorization Code OAuth scaffolding, проверка аккаунта `GET /core/v1/accounts/self`, чаты `GET /messenger/v2/accounts/{user_id}/chats`, сообщения `GET /messenger/v3/accounts/{user_id}/chats/{chat_id}/messages/`, текстовые ответы через официальный `POST /messenger/v1/accounts/{user_id}/chats/{chat_id}/messages`.
- Поллинг каждые ~36 секунд после запуска worker, ограниченный срез переписок. Не утверждается полная синхронизация/постоянный realtime — pagination/backfill нужно расширить и протестировать.
- Webhook Avito **не активируется**, пока разработчик не проверит актуальный механизм доверенного подтверждения источника и реальные права конкретного приложения.
- Для включения: `AVITO_CLIENT_ID`, `AVITO_CLIENT_SECRET`, `PUBLIC_BASE_URL`, корректно зарегистрированный callback; контакт с Avito для бизнес-доступа.

## Instagram Direct

Официальный набор Meta: https://www.postman.com/meta/instagram/overview

- Требуется профессиональный **Business/Creator** Instagram, App Review/права `instagram_business_basic` и `instagram_business_manage_messages` (а также требуемые Meta настройки подписки).
- Пользователь Instagram должен **написать профессиональному аккаунту первым**. Произвольный outreach в личные сообщения недоступен.
- Реализованы Instagram Login OAuth scaffolding с `state`, обмен short-lived token на long-lived token, проверка профиля, отправка текста, приём подписанных webhooks, базовое отображение вложений.
- Для webhook требуется App Secret `INSTAGRAM_APP_SECRET_WEBHOOK` или `INSTAGRAM_APP_SECRET` / `META_APP_SECRET`, подписка на сообщения и действительный HTTPS callback `.../api/webhooks/instagram`.
- Приложение консервативно проверяет ответ в пределах 24-часового клиентского окна. Текст ограничен **1000 байт UTF-8**, включая кириллицу и emoji. Варианты human-agent / exceptions не реализованы.
- Историческая синхронизация Conversations API, полноценная ротация токена, media-send, pagination и live App Review всё ещё не проверены.

## WhatsApp Business Platform Cloud API

Официальные коллекции: https://www.postman.com/meta/whatsapp-business-platform/overview

- Нужен Meta Business Portfolio, WhatsApp Business Account и **зарегистрированный номер**; действующий токен с `whatsapp_business_messaging`.
- В текущем UI вводятся Phone Number ID + действующий access token, после чего сервер проверяет номер через Meta Graph API перед показом статуса `connected`. Результат **никогда не имитируется**.
- Webhook подтверждается verify token `META_WEBHOOK_VERIFY_TOKEN`; POST события должны иметь правильную HMAC подпись App Secret (`WHATSAPP_APP_SECRET` или `META_APP_SECRET`). URL `https://<host>/api/webhooks/whatsapp`.
- Входящие текстовые и медиа-метаданные нормализуются; для WhatsApp media_id есть защищённый по доступу download proxy с host allowlist. Отправка **только текстовых** ответов через `/messages` в стандартном 24-часовом окне.
- **Шаблонные сообщения (business-initiated), media-send и Embedded Signup для многих арендаторов ещё не реализованы**; нельзя продавать как готовые.
- Для включения: `INTEGRATION_ENCRYPTION_KEY`, `META_WEBHOOK_VERIFY_TOKEN`, App Secret, Phone Number ID, authorized token, подписанный webhook.

## Правило допуска в production

Для каждой интеграции, перед отметкой `live certified`:

1. Зарегистрировать приложение / бизнес-аккаунт, получить необходимые permissions.
2. Проверить успешное получение реального тестового клиентского сообщения через official webhook / polling.
3. Отправить ответ только реальному **согласившемуся тестовому собеседнику**, проверить статус доставки.
4. Проверить истечение токена, rate limits, срыв сети, дубли webhook и отмену разрешений.
5. Убедиться, что приложению разрешён данный use case и каналу хватает оплаченных функций.
6. Протестировать несколько организаций, несколько аккаунтов и корректную изоляцию.
7. Задокументировать дату проверки, версии API и результаты, не публиковать секреты.
