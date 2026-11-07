# GitHub: безопасная публикация исходников

Целевой репозиторий: https://github.com/osmanosmanov6880-bot/osmanx-omnichat

Внимание: на момент подготовки он **публичный**. Рекомендуется временно переключить в Private перед первой загрузкой.

## Перед первым push

1. Проверить `git status --short` и `git ls-files`; не добавлять `.env`, базы `.db`/`.sqlite3`, логи, архивы резервного копирования, приватные чаты и client uploads.
2. Настроить SSH или GitHub credential manager; не писать PAT в URL и не отправлять токены в переписку.
3. Если репозиторий уже имеет README-коммит, сделать `git fetch origin`, затем `git pull --rebase origin main` до `push`. Не делать `--force`.
4. Команды в распакованной папке проекта:

```bash
git init
git branch -M main
git remote add origin https://github.com/osmanosmanov6880-bot/osmanx-omnichat.git
git add .
git status --short
git commit -m "feat: import audited OMNICHAT R36 on R35"
git pull --rebase origin main
git push -u origin main
```

GitHub Actions из `.github/workflows/ci.yml` проверяет backend, миграции, TypeScript и браузер. Первый push — это **публикация кода, не выкладка рабочей системы в production**. Перед включением реальной отправки в мессенджеры требуется проверка авторизаций, прав и отказов на тестовых аккаунтах провайдеров.

## Готовые скрипты для распакованного ZIP

В Windows из корневой папки проекта:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\publish_github.ps1
```

В Linux/macOS из корневой папки:

```bash
sh scripts/publish_github.sh
```

Они проверяют наличие баз и ключей, подхватывают уже опубликованный README, показывают состав коммита и требуют ручного подтверждения публичной публикации. Не выполняйте из папки с рабочими данными клиентов.
