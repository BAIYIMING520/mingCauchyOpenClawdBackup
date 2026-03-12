#!/usr/bin/env python3
"""
东方财富A股分时监控服务
功能：管理自选股 + 开盘时间自动抓取分时数据
"""

import json
import os
from datetime import datetime, time
from pathlib import Path

# 配置文件路径
CONFIG_FILE = Path(__file__).parent / "config.json"

DEFAULT_CONFIG = {
    "stocks": [],  # 自选股列表 ["600519", "000001", "300750"]
    "interval": 60,  # 抓取间隔（秒）
    "enabled": True
}

def load_config() -> dict:
    """加载配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()

def save_config(config: dict):
    """保存配置"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def add_stock(code: str):
    """添加股票"""
    config = load_config()
    code = code.strip().upper()
    if code not in config["stocks"]:
        config["stocks"].append(code)
        save_config(config)
        return True
    return False

def remove_stock(code: str):
    """移除股票"""
    config = load_config()
    code = code.strip().upper()
    if code in config["stocks"]:
        config["stocks"].remove(code)
        save_config(config)
        return True
    return False

def get_stocks():
    """获取自选股列表"""
    return load_config()["stocks"]

def is_trading_time() -> bool:
    """检查当前是否在交易时间"""
    now = datetime.now()
    current_time = now.time()
    
    # 9:30-11:30 上午
    morning_start = time(9, 30)
    morning_end = time(11, 30)
    
    # 13:00-15:00 下午
    afternoon_start = time(13, 0)
    afternoon_end = time(15, 0)
    
    # 周末
    if now.weekday() >= 5:
        return False
    
    return (morning_start <= current_time <= morning_end) or \
           (afternoon_start <= current_time <= afternoon_end)

if __name__ == "__main__":
    # 测试
    print("当前自选股:", get_stocks())
    print("交易时间:", is_trading_time())
    
    # 添加测试股票
    add_stock("000001")
    add_stock("600519")
    print("添加后:", get_stocks())
