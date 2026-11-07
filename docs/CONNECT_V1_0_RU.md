# OSMANX OMNICHAT v1.0 / Connect

**Запускаемый локальный MVP**, ориентированный на максимально простой путь: зарегистрировать компанию, выбрать канал, получить сообщение и ответить. Важные изменения в v0.9 — реальный быстрый старт из трёх шагов, настройка одной соцсети за раз, черновики при переключении диалогов и идемпотентная отправка после потерянного ответа сети. Утверждённый тёмный Obsidian Silence сохранён.

**Запуск:** распакуйте архив → Windows: `start_windows.bat`, Linux/macOS: `./start_linux.sh` → `http://127.0.0.1:8000`. Python 3.12+ и доступ к установке зависимостей нужны при первом запуске. Нажмите «Демоверсия» или зарегистрируйте отдельную компанию.

## Channels / Official accounts

### AVITO
Профессиональный аккаунт Авито с разрешением Messenger API

1. Получите в Авито доступ к Messenger API для своего тарифа
2. Разрешите доступ приложению OSMANX через официальный OAuth
3. Дождитесь первого успешного чтения переписок

### INSTAGRAM
Профессиональный аккаунт Instagram Business/Creator

1. Переключите аккаунт в профессиональный и разрешите доступ к сообщениям
2. Войдите через Instagram Login и предоставьте право на сообщения
3. Подпишитесь на события, затем проверьте входящий Direct

### WHATSAPP
WhatsApp Business Platform / Cloud API

1. Пройдите Meta Embedded Signup (при наличии одобренного Meta-приложения)
2. Создайте или выберите WABA, подтвердите бизнес-номер и права
3. Зарегистрируйте номер и проверьте входящий webhook

### TELEGRAM
Telegram-бот, принадлежащий компании

1. Создайте своего бота через @BotFather
2. Подключите полученный токен в OSMANX
3. Активируйте HTTPS webhook и отправьте сообщение боту

### VK
Сообщество ВКонтакте с разрешёнными сообщениями

1. Включите сообщения сообщества и выдайте ключ доступа
2. Укажите ID сообщества и код подтверждения Callback API
3. Зарегистрируйте webhook, секрет и проверьте входящее

### MESSENGER
Facebook Page с доступом к сообщениям Messenger

1. Авторизуйтесь в Facebook через официальное приложение Meta
2. Выберите принадлежащую компании Facebook-страницу
3. Подпишите страницу на события и проверьте входящий Messenger

### MAX
Официально созданный бот MAX

1. Получите токен бота в MAX для бизнеса
2. Подключите токен в OSMANX
3. Активируйте защищённую подписку и проверьте входящее

## Validation

Open your workspace, use the Integrations tab, choose one provider, and use the one-click connection check. Official account identity and Telegram/MAX webhook settings can be checked without sending a customer message. Then confirm a genuine incoming message and outgoing response using the original social app.

A token, a registered webhook, and API acceptance are three different things. Read and delivery receipts are further distinct statuses. The Demo Mode is never an external integration test.

## Security and external permissions

Use only accounts you own or are authorized to administer. Keep API tokens and callback secrets on the server. A browser on localhost cannot receive external HTTPS webhooks without a secure publicly reachable endpoint. Never use an unofficial API to read personal messages.

[More Russian onboarding details](CONNECT_REAL_CHANNELS_V08.md) | [Live setup preflight](../scripts/check_live_setup.py)
