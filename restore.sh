#!/bin/bash
# OpenClaw Restore Script
# Usage: bash restore.sh

set -e

WORKSPACE="$HOME/.openclaw/workspace"
BACKUP_REPO="git@github.com:BAIYIMING520/mingCauchyOpenClawdBackup.git"

echo "🦞 OpenClaw Restore Script"
echo "============================"

# 1. Clone backup
echo "[1/6] Cloning backup repository..."
cd "$WORKSPACE"
if [ -d "temp_backup" ]; then rm -rf temp_backup; fi
git clone "$BACKUP_REPO" temp_backup

# 2. Restore core files
echo "[2/6] Restoring core files..."
for file in AGENTS.md SOUL.md USER.md IDENTITY.md TOOLS.md HEARTBEAT.md MEMORY.md INSTALLED_SKILLS.md; do
  if [ -f "temp_backup/$file" ]; then
    cp "temp_backup/$file" .
    echo "  ✓ $file"
  fi
done

# 3. Restore memory
echo "[3/6] Restoring memory..."
if [ -d "temp_backup/memory" ]; then
  cp -r temp_backup/memory .
  echo "  ✓ memory/"
fi

# 4. Reinstall skills
echo "[4/6] Reinstalling skills..."
if command -v skillhub &> /dev/null; then
  for skill in agent-browser find-skills github workspace-backup proactive-agent automation-workflows multi-search-engine tavily tavily-search summarize n8n obsidian tencentcloud-lighthouse-skill tencent-cos-skill tencent-docs weather; do
    echo "  → Installing $skill..."
    skillhub install "$skill" || echo "  ✗ $skill failed"
  done
else
  echo "  ⚠ skillhub not found, skipping"
fi

# 5. Restore cron jobs
echo "[5/6] Restoring cron jobs..."
if command -v openclaw &> /dev/null; then
  openclaw cron add --name "healthcheck:daily-audit" --cron "0 9 * * *" --message "运行 openclaw security audit 并报告结果" --channel feishu --announce
  openclaw cron add --name "healthcheck:update-check" --cron "0 10 * * 1" --message "运行 openclaw update status 检查是否有新版本" --channel feishu --announce
  openclaw cron add --name "backup:workspace" --cron "0 0,4,8,12,16,20 * * *" --message "检查 workspace 是否有变化，如有则自动备份到 GitHub" --channel feishu --announce
  echo "  ✓ Cron jobs restored"
else
  echo "  ⚠ openclaw not found, skipping"
fi

# 6. Cleanup
echo "[6/6] Cleaning up..."
rm -rf temp_backup

echo ""
echo "✅ Restore complete!"
echo ""
echo "Next steps:"
echo "  1. openclaw status"
