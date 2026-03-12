#!/usr/bin/env python3
"""测试分时/分钟线数据"""
import tushare as ts

token = "06b07a5b6ee5b96af290ea97248202825fc8d633c312f323f03b6b589424"

pro = ts.pro_api(token)
pro._DataApi__token = token
pro._DataApi__http_url = 'http://lianghua.nanyangqiankun.top'

print("=" * 50)
print("测试1: 5分钟线数据")
print("=" * 50)
try:
    df = pro.minutely(ts_code='000001.SZ', start_time='20240129150000', end_time='20240130100000')
    print(f"✅ 成功！返回 {len(df)} 条数据")
    print(df.head(10))
except Exception as e:
    print(f"❌ 失败: {e}")

print("\n" + "=" * 50)
print("测试2: 今日分时数据(实时)")
print("=" * 50)
try:
    df = pro.minutely(ts_code='000001.SZ')
    print(f"✅ 成功！返回 {len(df)} 条数据")
    print(df.head(10))
except Exception as e:
    print(f"❌ 失败: {e}")

print("\n" + "=" * 50)
print("测试3: 逐笔成交tick数据")
print("=" * 50)
try:
    df = pro.tick(ts_code='000001.SZ', trade_date='20240130')
    print(f"✅ 成功！返回 {len(df)} 条数据")
    print(df.head(10))
except Exception as e:
    print(f"❌ 失败: {e}")
