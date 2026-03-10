# OpenClaw Cron Jobs Export

> Auto-generated. Last updated: 2026-03-10

## Restore Commands

Run these to recreate cron jobs after a fresh install:

```bash
# Daily security audit (9:00)
openclaw cron add --name "healthcheck:daily-audit" --cron "0 9 * * *" --message "运行 openclaw security audit 并报告结果" --channel feishu --announce

# Weekly update check (Monday 10:00)
openclaw cron add --name "healthcheck:update-check" --cron "0 10 * * 1" --message "运行 openclaw update status 检查是否有新版本" --channel feishu --announce

# Workspace backup (every 4 hours)
openclaw cron add --name "backup:workspace" --cron "0 0,4,8,12,16,20 * * *" --message "检查 workspace 是否有变化，如有则自动备份到 GitHub" --channel feishu --announce
```

---

## Current Jobs (JSON)

```json
{
  "jobs": [
    {
      "name": "backup:workspace",
      "cron": "0 0,4,8,12,16,20 * * *",
      "message": "检查 workspace 是否有变化，如有则自动备份到 GitHub"
    },
    {
      "name": "healthcheck:daily-audit",
      "cron": "0 9 * * *",
      "message": "运行 openclaw security audit 并报告结果"
    },
    {
      "name": "healthcheck:update-check",
      "cron": "0 10 * * 1",
      "message": "运行 openclaw update status 检查是否有新版本"
    }
  ]
}
```
