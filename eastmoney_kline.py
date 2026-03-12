#!/usr/bin/env python3
"""
东方财富A股分时数据获取程序
功能：获取实时+历史分钟K线数据
"""

import requests
import json
import pandas as pd
from datetime import datetime, time
from typing import Optional, List, Dict
import os

class EastMoneyClient:
    """东方财富行情数据客户端"""
    
    BASE_URL = "https://push2.eastmoney.com"
    
    # 市场代码映射
    MARKET_MAP = {
        'sh': '0.',   # 上海
        'sz': '1.',   # 深圳
        'bj': '0.',   # 北京
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _get_secid(self, code: str) -> str:
        """获取市场代码
        上海: 0.xxx (6开头)
        深圳: 1.xxx (0,3开头)
        北京: 0.xxx (8,4开头)
        """
        code = code.strip().lower()
        
        # 已经是完整格式
        if '.' in code:
            return code
        
        # 根据代码判断市场
        if code.startswith('6'):
            return f'0.{code}'  # 上海
        elif code.startswith(('0', '3')):
            return f'1.{code}'  # 深圳
        elif code.startswith(('8', '4')):
            return f'0.{code}'  # 北京
        else:
            return f'0.{code}'  # 默认上海
    
    def get_kline(self, code: str, period: int = 1, 
                  start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取K线数据
        
        Args:
            code: 股票代码 (如 000001, 600519)
            period: K线周期 (1/5/15/30/60 分钟)
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
        
        Returns:
            DataFrame with columns: 时间, 开盘, 收盘, 最高, 最低, 成交量, 成交额, 涨跌幅, 涨跌额, 换手率
        """
        secid = self._get_secid(code)
        
        # 默认今天
        if not start_date:
            start_date = datetime.now().strftime('%Y%m%d')
        if not end_date:
            end_date = start_date
        
        params = {
            'secid': secid,
            'fields1': 'f1,f2,f3,f4,f5,f6',
            'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
            'klt': str(period),
            'fqt': '0',  # 不复权
            'beg': start_date,
            'end': end_date
        }
        
        url = f"{self.BASE_URL}/api/qt/stock/kline/get"
        resp = self.session.get(url, params=params, timeout=10)
        data = resp.json()
        
        if data.get('data') is None:
            print(f"Warning: No data for {code}, response: {data}")
            return pd.DataFrame()
        
        klines = data['data']['klines']
        if not klines:
            return pd.DataFrame()
        
        # 解析数据
        records = []
        for kline in klines:
            parts = kline.split(',')
            records.append({
                '时间': parts[0],
                '开盘': float(parts[1]),
                '收盘': float(parts[2]),
                '最高': float(parts[3]),
                '最低': float(parts[4]),
                '成交量': int(parts[5]),
                '成交额': float(parts[6]),
                '涨跌幅': float(parts[7]) if parts[7] != '-' else 0,
                '涨跌额': float(parts[8]) if parts[8] != '-' else 0,
                '换手率': float(parts[9]) if parts[9] != '-' else 0,
            })
        """获取实时行情"""
        secid = self._get_secid(code)
        
        params = {
            'secid': secid,
            'fields': 'f43,f44,f45,f46,f47,f48,f50,f51,f52,f55,f57,f58,f59,f60,f116,f117,f118,f119,f120,f121,f122,f124'
        }
        
        url = f"{self.BASE_URL}/api/qt/stock/get"
        resp = self.session.get(url, params=params, timeout=10)
        data = resp.json()
        
        if not data.get('data'):
            return {}
        
        d = data['data']
        return {
            'code': d.get('f57'),
            'name': d.get('f58'),
            'price': d.get('f43', 0) / 100,  # 价格需要除以100
            'change': d.get('f44', 0) / 100,
            'change_pct': d.get('f45', 0) / 100,
            'volume': d.get('f47'),
            'amount': d.get('f48'),
        }
    
    def is_trading_time(self) -> bool:
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


def demo():
    """演示"""
    client = EastMoneyClient()
    
    # 测试获取1分钟K线
    print("=" * 50)
    print("获取平安银行(000001) 1分钟K线...")
    print("=" * 50)
    
    df = client.get_kline('000001', period=1, start_date='20260312', end_date='20260312')
    
    if not df.empty:
        print(f"共获取 {len(df)} 条数据")
        print("\n前5条:")
        print(df.head())
        print("\n后5条:")
        print(df.tail())
        
        # 保存到CSV
        df.to_csv('stock_000001_1min.csv', index=False, encoding='utf-8-sig')
        print("\n数据已保存到 stock_000001_1min.csv")
    else:
        print("未获取到数据")
    
    # 测试获取实时行情
    print("\n" + "=" * 50)
    print("获取实时行情...")
    print("=" * 50)
    
    quote = client.get_realtime_quote('000001')
    print(f"股票: {quote.get('name')} ({quote.get('code')})")
    print(f"价格: {quote.get('price')}")
    print(f"涨跌: {quote.get('change')} ({quote.get('change_pct')}%)")
    
    # 测试其他股票
    print("\n" + "=" * 50)
    print("测试多只股票...")
    print("=" * 50)
    
    for code in ['600519', '300033', '000001']:
        df = client.get_kline(code, period=5, start_date='20260312', end_date='20260312')
        print(f"{code}: {len(df)} 条5分钟K线")


if __name__ == '__main__':
    demo()
