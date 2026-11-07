# OSMANX OMNICHAT R36 — authenticated local GitHub publication.
# Prerequisite: Git for Windows and GitHub credential manager, or existing SSH access.
# Run from the project root: powershell -ExecutionPolicy Bypass -File .\scripts\publish_github.ps1
$ErrorActionPreference='Stop'
$project = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $project
$remote='https://github.com/osmanosmanov6880-bot/osmanx-omnichat.git'
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'Установите Git for Windows.' }
$bad = Get-ChildItem -Force -File -Recurse | Where-Object { $_.FullName -notmatch '[\\/](\.git|node_modules|\.venv|__pycache__|backups)[\\/]' -and ($_.Name -match '^\.env($|\.(?!example$))' -or $_.Extension -in '.db','.sqlite','.sqlite3','.pem','.p12','.key') }
if ($bad) { throw ('Остановлено: найдены запрещённые файлы: '+(($bad | Select-Object -First 6 -ExpandProperty FullName) -join ', ')) }
if (-not (Test-Path '.git')) { git init -b main; if ($LASTEXITCODE) { throw 'git init failed' } }
$existing = @(git remote)
if ($existing -contains 'origin') {
    $actual = (git remote get-url origin).Trim()
    if ($actual -ne $remote) { throw "Неожиданный remote origin: $actual" }
} else { git remote add origin $remote }
# Preserve the existing README commit and never force-push.
git fetch origin main
if ($LASTEXITCODE) { throw 'Не удалось получить main: проверьте подключение GitHub.' }
$head = git rev-parse --verify HEAD 2>$null
if ($LASTEXITCODE -ne 0) {
    git reset --mixed origin/main
    if ($LASTEXITCODE) { throw 'Не удалось совместить начальную ветку с origin/main' }
} else {
    git merge-base --is-ancestor origin/main HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Удалённая ветка изменилась: вручную согласуйте историю, --force запрещён.' }
}
git add --all
if ($LASTEXITCODE) { throw 'git add failed' }
Write-Host 'Проверьте файлы, отправляемые в GitHub:'
git diff --cached --stat
Write-Host 'Запрещённые данные должны быть удалены до коммита.'
$answer = Read-Host 'Подтверждаете публикацию в ПУБЛИЧНЫЙ репозиторий? Введите PUBLISH'
if ($answer -cne 'PUBLISH') { throw 'Публикация отменена' }
git commit -m 'feat: OMNICHAT R36 integrated R35 backend, UI and CI'
if ($LASTEXITCODE) { throw 'git commit failed (возможно, нет изменений или не настроено имя)' }
git push -u origin main
if ($LASTEXITCODE) { throw 'Не удалось отправить git push' }
Write-Host 'Опубликовано: https://github.com/osmanosmanov6880-bot/osmanx-omnichat'
