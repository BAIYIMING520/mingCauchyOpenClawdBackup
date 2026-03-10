# OpenClaw Continuity Backup

> Automated backup of OpenClaw workspace core files for session continuity.

## What's Backed Up

- `MEMORY.md` - Long-term curated memories
- `memory/` - Daily session logs
- `USER.md` - User profile and preferences
- `SOUL.md` - Agent persona definition
- `IDENTITY.md` - Agent identity (name, emoji, avatar)
- `TOOLS.md` - Local tool configurations
- `AGENTS.md` - Workspace agent rules
- `HEARTBEAT.md` - Periodic check configuration

## What's Excluded

- Token / secrets / credentials
- Session data
- node_modules
- Logs and caches

## Recovery

To restore continuity after a fresh install:

1. Clone this repo to your workspace
2. Restore the above core files
3. Run `openclaw status` to verify

## Auto-Backup

This repo is auto-backed up periodically via OpenClaw cron jobs.
Commit messages include timestamp and change summary.
