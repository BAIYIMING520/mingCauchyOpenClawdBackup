#!/usr/bin/env python3
"""探测三方渠道支持的接口"""
import tushare as ts

token = "06b07a5b6ee5b96af290ea97248202825fc8d633c312f323f03b6b589424"

pro = ts.pro_api(token)
pro._DataApi__token = token
pro._DataApi__http_url = 'http://lianghua.nanyangqiankun.top'

# 常见接口列表
interfaces = [
    'daily', 'weekly', 'monthly',  # K线
    'adj_factor', 'basic', 'margin', 'margin_detail',  # 基础数据
    'stock_company', 'stock_basic',  # 股票基本信息
    'index_daily', 'index_basic',  # 指数
    'moneyflow_hsgt', 'hk_hold',  # 沪深港通
    'fina_indicator', 'fina_mainbz', 'fina_audit',  # 财务
    'news', 'news_detail',  # 新闻
    'trade_cal',  # 交易日历
    'suspend', 'stk_recover', 'stk_relate',  # 停复牌
    'profit forecast', 'express',  # 业绩预告
]

print("探测支持的接口:")
for iface in interfaces:
    try:
        # 用最简单的参数测试
        if iface == 'daily':
            df = pro.daily(ts_code='000001.SZ', start_date='20240101', end_date='20240105')
        elif iface == 'stock_basic':
            df = pro.stock_basic()
        elif iface == 'trade_cal':
            df = pro.trade_cal(exchange='SSE', start_date='20240101', end_date='20240110')
        elif iface == 'index_basic':
            df = pro.index_basic()
        else:
            continue
        print(f"  ✅ {iface}")
    except Exception as e:
        print(f"  ❌ {iface}: {str(e)[:50]}")
