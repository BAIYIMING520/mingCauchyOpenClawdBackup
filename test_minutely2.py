#!/usr/bin/env python3
"""测试分时数据 - 多种接口名"""
import tushare as ts

token = "06b07a5b6ee5b96af290ea97248202825fc8d633c312f323f03b6b589424"

pro = ts.pro_api(token)
pro._DataApi__token = token
pro._DataApi__http_url = 'http://lianghua.nanyangqiankun.top'

# 尝试不同的接口名
interfaces = ['minutely', 'minute', 'kline', ' Kline', 'stock_kline', 'daily_kline']

for iface in interfaces:
    print(f"\n尝试接口: {iface}")
    try:
        # 尝试获取1分钟K线
        df = pro.kline(ts_code='000001.SZ', start_date='20240129', end_date='20240130', freq='1')
        print(f"  ✅ kline成功! 返回 {len(df)} 条")
        print(df.head())
        break
    except Exception as e:
        print(f"  ❌ {e}")

# 也试试用 ts 直接调
print("\n" + "="*50)
print("尝试 ts.pro_bar (分钟线)")
print("="*50)
try:
    df = ts.pro_bar(ts_code='000001.SZ', start_date='20240129', end_date='20240130', freq='5')
    print(f"✅ 成功! 返回 {len(df)} 条")
    print(df.head())
except Exception as e:
    print(f"❌ 失败: {e}")
