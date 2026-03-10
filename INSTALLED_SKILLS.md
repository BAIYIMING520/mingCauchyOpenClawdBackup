# OpenClaw Installed Skills

> Auto-generated list of installed skills. Last updated: 2026-03-10

## How to Restore

Run this to reinstall all skills:

```bash
cd ~/.openclaw/workspace/skills/
for skill in $(cat INSTALLED_SKILLS.md | grep "^## " | sed 's/## //'); do
  skillhub install $skill
done
```

## Installed Skills

## Core
- agent-browser
- find-skills
- github

## AI & Automation
- proactive-agent
- automation-workflows

## Search & Research
- multi-search-engine
- tavily
- tavily-search
- summarize

## Productivity
- n8n
- obsidian

## Cloud & DevOps
- tencentcloud-lighthouse-skill
- tencent-cos-skill
- tencent-docs

## Utilities
- weather

---

*This file is auto-generated. Do not edit manually.*
