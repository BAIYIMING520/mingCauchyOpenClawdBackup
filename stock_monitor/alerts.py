#!/usr/bin/env python3
"""
告警检查模块
"""

import sys
sys.path.append(__file__.rsplit('/', 1)[0])

from database import get_minute_data
from config import get_alerts_config, get_quote0_config
from client import EastMoneyClient
import subprocess
import numpy as np

class AlertChecker:
    def __init__(self):
        self.client = EastMoneyClient()
        self.alerts = get_alerts_config()
        self.quote0 = get_quote0_config()
    
    def check_all(self, code: str, realtime_data: dict):
        """检查所有告警"""
        alerts_triggered = []
        name = realtime_data.get('name', '')[:4]  # 股票简称
        
        # 1. 涨跌幅告警
        if self.alerts.get("price_change", {}).get("enabled"):
            threshold = self.alerts["price_change"].get("threshold", 5.0)
            pct = abs(realtime_data.get("change_pct", 0))
            if pct >= threshold:
                alerts_triggered.append({
                    "type": "price_change",
                    "msg": f"{code}{name} 涨跌{pct:.2f}%",
                    "severity": "high"
                })
        
        # 2. 快速波动告警
        if self.alerts.get("rapid_change", {}).get("enabled"):
            minutes = self.alerts["rapid_change"].get("minutes", 30)
            threshold = self.alerts["rapid_change"].get("threshold", 3.0)
            change = self._check_rapid_change(code, minutes)
            if change and abs(change) >= threshold:
                direction = "涨" if change > 0 else "跌"
                alerts_triggered.append({
                    "type": "rapid_change",
                    "msg": f"{code}{name} {minutes}分{direction}{abs(change):.2f}%",
                    "severity": "high"
                })
        
        # 3. 放量告警
        if self.alerts.get("volume_surge", {}).get("enabled"):
            threshold = self.alerts["volume_surge"].get("threshold", 50.0)
            surge = self._check_volume_surge(code)
            if surge and surge >= threshold:
                alerts_triggered.append({
                    "type": "volume_surge",
                    "msg": f"{code}{name} 放量{surge:.1f}%",
                    "severity": "medium"
                })
        
        # 5. 趋势判断告警（三次拟合都向下）
        if self.alerts.get("trend_fit", {}).get("enabled"):
            lookback = self.alerts.get("trend_fit", {}).get("lookback", 6)
            trend_result = self._check_trend_fit(code, lookback)
            if trend_result:
                alerts_triggered.append({
                    "type": "trend_fit",
                    "msg": f"{code}{name} {trend_result}",
                    "severity": "high"
                })
        
        return alerts_triggered
    
    def _check_trend_fit(self, code: str, lookback: int = 60) -> str:
        """多函数拟合趋势判断
        
        Args:
            code: 股票代码
            lookback: 看最近多少个数据点（默认60个=1小时）
        """
        data = get_minute_data(code)
        # 至少需要12个数据点才能做有效拟合
        if not data or len(data) < 12:
            return None
        
        # 只取最近N个数据点（短线趋势）
        prices = np.array([d['close'] for d in data[-lookback:]])
        x = np.arange(len(prices))
        
        # 一次拟合
        coef1 = np.polyfit(x, prices, 1)
        linear_down = coef1[0] < 0  # 斜率向下
        
        # 二次拟合
        coef2 = np.polyfit(x, prices, 2)
        quadratic_down = coef2[0] < 0  # 开口向下
        
        # 三次拟合（看首尾）
        cubic_down = prices[-1] < prices[0]  # 收盘低于开盘
        
        # 三个都向下
        if linear_down and quadratic_down and cubic_down:
            return "下跌趋势确认 ⬇️ 可做反T(卖出)"
        
        # 三个都向上
        if not linear_down and not quadratic_down and not cubic_down:
            return "上涨趋势确认 ⬆️ 可做正T(买入)"
        
        return None
    
    def _check_rapid_change(self, code: str, minutes: int) -> float:
        """检查N分钟内的涨跌幅"""
        data = get_minute_data(code)
        if not data or len(data) < 2:
            return None
        
        # 获取N分钟前的价格
        idx = len(data) - minutes
        if idx < 0:
            idx = 0
        
        old_price = data[idx].get("close")
        new_price = data[-1].get("close")
        
        if old_price and new_price and old_price > 0:
            return (new_price - old_price) / old_price * 100
        return None
    
    def _check_volume_surge(self, code: str) -> float:
        """检查成交量是否激增"""
        data = get_minute_data(code)
        if not data or len(data) < 30:
            return None
        
        # 对比最近30分钟和之前30分钟
        recent_volume = sum(d.get("volume", 0) for d in data[-30:])
        earlier_volume = sum(d.get("volume", 0) for d in data[-60:-30]) if len(data) >= 60 else recent_volume
        
        if earlier_volume > 0:
            return (recent_volume - earlier_volume) / earlier_volume * 100
        return None
    
    def _check_continuous_trend(self, code: str, name: str, intervals: list, min_change: float) -> list:
        """检查连续涨/跌"""
        data = get_minute_data(code)
        if not data or len(data) < 5:
            return []
        
        trends = []
        
        for minutes in intervals:
            if len(data) < minutes:
                continue
            
            # 获取时间段开始和结束的价格
            start_price = data[-minutes].get("close")
            end_price = data[-1].get("close")
            
            if start_price and end_price and start_price > 0:
                change_pct = (end_price - start_price) / start_price * 100
                
                # 连续上涨
                if change_pct >= min_change:
                    # 检查是否一直在涨（每个30分钟段都是涨）
                    segments = minutes // 30
                    all_up = True
                    for i in range(segments):
                        seg_start = data[-(i+1)*30].get("close") if len(data) > (i+1)*30 else data[0].get("close")
                        seg_end = data[-(i+1)*30 + 30].get("close") if len(data) > (i+1)*30 + 30 else data[-1].get("close")
                        if seg_start and seg_end and seg_end <= seg_start:
                            all_up = False
                            break
                    
                    if all_up:
                        trends.append({
                            "type": "continuous_up",
                            "msg": f"{code}{name} 连涨{minutes//60}h {change_pct:.2f}%",
                            "severity": "high"
                        })
                
                # 连续下跌
                elif change_pct <= -min_change:
                    trends.append({
                        "type": "continuous_down",
                        "msg": f"{code}{name} 连跌{minutes//60}h {abs(change_pct):.2f}%",
                        "severity": "high"
                    })
        
        return trends
    
    def push_to_quote0(self, message: str, delay: float = 2.0):
        """推送到Quote/0
        
        Args:
            message: 推送内容
            delay: 推送间隔（秒），默认2秒
        """
        import time
        time.sleep(delay)
        if not self.quote0.get("enabled"):
            return
        
        api_key = self.quote0.get("api_key")
        device_id = self.quote0.get("device_id")
        
        if not api_key or not device_id:
            return
        
        try:
            cmd = [
                "node", "quote0.js", "text",
                "--apiKey", api_key,
                "--deviceId", device_id,
                "--title", "",
                "--message", message,
                "--signature", ""
            ]
            result = subprocess.run(
                cmd,
                cwd="/root/.openclaw/workspace/skills/quote0",
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Quote/0 push error: {e}")
            return False


def check_and_push(code: str, realtime_data: dict):
    """检查并推送告警"""
    checker = AlertChecker()
    alerts = checker.check_all(code, realtime_data)
    
    if alerts:
        for alert in alerts:
            print(f"🚨 {alert['msg']}")
            checker.push_to_quote0(alert['msg'])
    
    return alerts


if __name__ == "__main__":
    # 测试
    checker = AlertChecker()
    print("告警配置:", checker.alerts)
