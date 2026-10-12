#!/usr/bin/env bash
set -euo pipefail
cd /workspace/meeting-todos
python3 build.py
# ignore the timestamp line when deciding whether content changed
if git diff --quiet -I 'Updated ' -- index.html; then echo "No changes"; git checkout -- index.html; exit 0; fi
git add index.html build.py publish.sh
git commit -m "Update to-dos $(date '+%Y-%m-%d %H:%M %Z')"
git push origin main
