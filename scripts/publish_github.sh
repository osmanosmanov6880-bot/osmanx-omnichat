#!/usr/bin/env sh
# Publish from an authenticated local Git working tree; never force-push.
set -eu
cd "$(dirname "$0")/.."
remote='https://github.com/osmanosmanov6880-bot/osmanx-omnichat.git'
command -v git >/dev/null || { echo 'Install git first' >&2; exit 1; }
if find . \( -name .git -o -name node_modules -o -name .venv -o -name __pycache__ -o -name backups \) -prune -o -type f \( -name .env -o -name '*.db' -o -name '*.sqlite3' -o -name '*.pem' -o -name '*.key' \) -print | grep -q .; then
  echo 'Refusing to publish: local secret or database file detected' >&2
  exit 1
fi
[ -d .git ] || git init -b main
if git remote | grep -qx origin; then
  [ "$(git remote get-url origin)" = "$remote" ] || { echo 'Unexpected origin remote' >&2; exit 1; }
else
  git remote add origin "$remote"
fi
git fetch origin main
if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
  git reset --mixed origin/main
else
  git merge-base --is-ancestor origin/main HEAD || { echo 'Remote and local history diverged; resolve manually' >&2; exit 1; }
fi
git add --all
git diff --cached --stat
printf 'Public repository. Type PUBLISH to proceed: '
read answer
[ "$answer" = 'PUBLISH' ] || exit 1
git commit -m 'feat: OMNICHAT R36 integrated R35 backend, UI and CI'
git push -u origin main
