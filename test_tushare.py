#!/usr/bin/env python3
"""测试第三方 Tushare Token"""
import tushare as ts

# 第三方 token
token = "06b07a5b6ee5b96af290ea97248202825fc8d633c312f323f03b6b589424"

pro = ts.pro_api(token)
pro._DataApi__token = token
pro._DataApi__http_url = 'http://lianghua.nanyangqiankun.top'

# 测试获取数据
try:
    print("🔄 尝试获取平安银行(000001.SZ) 2024年1月行情数据...")
    df = pro.daily(ts_code='000001.SZ', start_date='20240101', end_date='20240131')
    print(f"✅ 成功！返回 {len(df)} 条数据")
    print("\n前5条数据:")
    print(df.head())
except Exception as e:
    print(f"❌ 失败: {e}")
