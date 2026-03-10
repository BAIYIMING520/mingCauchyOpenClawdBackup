#!/bin/bash
# OpenClaw Restore Script
# Usage: bash restore.sh

set -e

WORKSPACE="$HOME/.openclaw/workspace"
BACKUP_REPO="git@github.com:BAIYIMING520/mingCauchyOpenClawdBackup.git"

echo "🦞 OpenClaw Restore Script"
echo "============================"

# 1. Clone backup
echo "[1/5] Cloning backup repository..."
cd "$WORKSPACE"
if [ -d "temp_backup" ]; then rm -rf temp_backup; fi
git clone "$BACKUP_REPO" temp_backup

# 2. Restore core files
echo "[2/5] Restoring core files..."
for file in AGENTS.md SOUL.md USER.md IDENTITY.md TOOLS.md HEARTBEAT.md MEMORY.md INSTALLED_SKILLS.md; do
  if [ -f "temp_backup/$file" ]; then
    cp "temp_backup/$file" .
    echo "  ✓ $file"
  fi
done

# 3. Restore memory
echo "[3/5] Restoring memory..."
if [ -d "temp_backup/memory" ]; then
  cp -r temp_backup/memory .
  echo "  ✓ memory/"
fi

# 4. Reinstall skills
echo "[4/5] Reinstalling skills..."
if command -v skillhub &> /dev/null; then
  for skill in agent-browser find-skills github proactive-agent automation-workflows multi-search-engine tavily tavily-search summarize n8n obsidian tencentcloud-lighthouse-skill tencent-cos-skill tencent-docs weather; do
    echo "  → Installing $skill..."
    skillhub install "$skill" || echo "  ✗ $skill failed"
  done
else
  echo "  ⚠ skillhub not found, skipping"
fi

# 5. Cleanup
echo "[5/5] Cleaning up..."
rm -rf temp_backup

echo ""
echo "✅ Restore complete!"
echo ""
echo "Next steps:"
echo "  1. openclaw status"
echo "  2. Re-add cron jobs if needed"
