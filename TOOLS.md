# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## 股票监控 (Stock Monitor)

### 服务地址
- **前端**: http://111.229.214.87:8000
- **自选股**: 000001(上证指数), 600519, 002050, 603019, 300308, 300502

### 功能
- 实时行情展示
- 分时图表（点击卡片查看）
- 告警配置（涨跌幅、快速波动、放量、连续涨/跌）
- Quote/0 设备推送
- 后台定时任务（交易时间自动检查告警）

### 代码位置
```
/root/.openclaw/workspace/stock_monitor/
├── app.py           # Flask Web服务 + 前端
├── client.py        # 东方财富API客户端
├── config.py        # 配置管理
├── config.json      # 配置文件
├── database.py      # SQLite数据库
├── alerts.py        # 告警检查逻辑
├── scheduler.py     # 后台定时任务
└── stock_data.db   # 分时数据

/root/.openclaw/workspace/skills/quote0/
└── quote0.js       # Quote/0设备控制
```

### 告警类型
1. **涨跌幅告警** - 单日涨跌超过阈值
2. **快速波动告警** - N分钟内涨跌超过阈值
3. **放量告警** - 成交量激增
4. **连续涨/跌监控** - 30分钟/1/2/3小时持续涨/跌
5. **开盘/收盘推送** - 定时推送

### 管理命令
```bash
# 启动服务
cd /root/.openclaw/workspace/stock_monitor && python3 app.py

# 查看日志
tail -f /root/.openclaw/workspace/stock_monitor/app.log

# 手动推送测试
cd /root/.openclaw/workspace/stock_monitor && python3 -c "
from client import EastMoneyClient
from alerts import AlertChecker
from config import get_stocks

client = EastMoneyClient()
checker = AlertChecker()
for code in get_stocks():
    data = client.get_realtime(code)
    if data:
        alerts = checker.check_all(code, data)
        for a in alerts:
            print(f'🚨 {a[\"msg\"]}')
            checker.push_to_quote0(a['msg'])
"
```
