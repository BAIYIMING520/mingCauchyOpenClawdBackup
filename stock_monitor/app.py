#!/usr/bin/env python3
"""
A股分时监控服务 - Web服务器
功能：前端管理界面 + 实时数据展示 + 分时图表
"""

from flask import Flask, render_template_string, jsonify, request
import threading
import time
import os
from datetime import datetime
import sys

sys.path.append(os.path.dirname(__file__))

from config import load_config, save_config, add_stock, remove_stock, get_stocks, is_trading_time
from client import EastMoneyClient, get_all_realtime
from database import init_db, get_minute_data

app = Flask(__name__)

# 初始化数据库
init_db()

# ==================== HTML模板 ====================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A股分时监控</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e;
            color: #eee;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            text-align: center;
            color: #00d4ff;
            margin-bottom: 20px;
            font-size: 28px;
        }
        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #16213e;
            padding: 15px 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .status-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #666;
        }
        .status-dot.active { background: #00ff88; animation: pulse 2s infinite; }
        .status-dot.inactive { background: #ff4444; }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .add-form {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        input[type="text"] {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 8px;
            background: #16213e;
            color: #fff;
            font-size: 16px;
        }
        input[type="text"]::placeholder { color: #666; }
        button {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s;
        }
        .btn-add { background: #00d4ff; color: #1a1a2e; }
        .btn-add:hover { background: #00b8e6; }
        .btn-delete {
            background: #ff4757;
            color: #fff;
            padding: 6px 12px;
            font-size: 14px;
        }
        .btn-delete:hover { background: #ff3344; }
        .stock-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
        }
        .stock-card {
            background: #16213e;
            border-radius: 12px;
            padding: 20px;
            position: relative;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .stock-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 212, 255, 0.2);
        }
        .stock-card .delete-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            background: transparent;
            color: #666;
            padding: 5px;
            font-size: 20px;
            z-index: 10;
        }
        .stock-card .delete-btn:hover { color: #ff4757; }
        .stock-name {
            font-size: 18px;
            font-weight: bold;
            color: #00d4ff;
            margin-bottom: 5px;
        }
        .stock-code {
            font-size: 14px;
            color: #666;
            margin-bottom: 15px;
        }
        .stock-price {
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .price-up { color: #ff4757; }
        .price-down { color: #00ff88; }
        .stock-change {
            font-size: 16px;
            margin-bottom: 5px;
        }
        .stock-info {
            display: flex;
            gap: 15px;
            align-items: center;
            margin-bottom: 10px;
        }
        .yesterday-close {
            font-size: 14px;
            color: #888;
        }
        .alert-section {
            background: #1a1a2e;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        .alert-section h4 { margin: 0 0 10px 0; color: #00d4ff; }
        .alert-section input[type="number"] {
            background: #16213e;
            border: 1px solid #333;
            color: #fff;
            padding: 5px 10px;
            border-radius: 4px;
            width: 60px;
        }
        .stock-time {
            font-size: 12px;
            color: #666;
        }
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }
        .empty-state h2 { margin-bottom: 10px; }
        .last-update {
            text-align: center;
            color: #666;
            margin-top: 20px;
            font-size: 14px;
        }
        
        /* 弹窗图表 */
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            z-index: 100;
            justify-content: center;
            align-items: center;
        }
        .modal-overlay.show { display: flex; }
        .modal {
            background: #16213e;
            border-radius: 16px;
            padding: 20px;
            width: 90%;
            max-width: 900px;
            max-height: 90vh;
            overflow: auto;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .modal-title {
            font-size: 20px;
            font-weight: bold;
            color: #00d4ff;
        }
        .modal-close {
            background: none;
            border: none;
            color: #666;
            font-size: 28px;
            cursor: pointer;
            padding: 0;
        }
        .modal-close:hover { color: #fff; }
        .chart-container {
            height: 400px;
            position: relative;
        }
        .chart-loading {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📈 A股分时监控</h1>
        
        <div class="status-bar">
            <div class="status-item">
                <div class="status-dot {% if is_trading %}active{% else %}inactive{% endif %}" id="statusDot"></div>
                <span>{% if is_trading %}● 交易中{% else %}○ 休市{% endif %}</span>
            </div>
            <div class="status-item">
                <span>自选股: <strong id="stockCount">0</strong> 只</span>
            </div>
            <div class="status-item">
                <span>刷新: <strong id="interval">-</strong>秒</span>
            </div>
        </div>
        
        <div class="add-form">
            <input type="text" id="stockInput" placeholder="输入股票代码 (如 600519, 000001, 300750)" maxlength="6">
            <button class="btn-add" onclick="addStock()">+ 添加股票</button>
            <button class="btn-add" style="background:#ff6b6b" onclick="openAlertConfig()">⚙️ 告警配置</button>
        </div>
        
        <div class="stock-grid" id="stockGrid">
            <div class="empty-state">
                <h2>暂无自选股</h2>
                <p>添加股票代码开始监控</p>
            </div>
        </div>
        
        <div class="last-update">
            最后更新: <span id="lastUpdate">-</span>
        </div>
    </div>
    
    <!-- 图表弹窗 -->
    <div class="modal-overlay" id="chartModal">
        <div class="modal">
            <div class="modal-header">
                <div class="modal-title" id="chartTitle">分时图</div>
                <button class="modal-close" onclick="closeModal()">×</button>
            </div>
            <div class="chart-container">
                <canvas id="minuteChart"></canvas>
                <div class="chart-loading" id="chartLoading">加载中...</div>
            </div>
        </div>
    </div>
    
    <!-- 告警配置弹窗 -->
    <div class="modal-overlay" id="alertModal">
        <div class="modal" style="max-width:600px">
            <div class="modal-header">
                <div class="modal-title">告警配置</div>
                <button class="modal-close" onclick="closeAlertModal()">×</button>
            </div>
            <div style="padding:20px;max-height:70vh;overflow-y:auto">
                <div class="alert-section">
                    <h4>📈 涨跌幅告警</h4>
                    <label><input type="checkbox" id="alert-price-change-enabled"> 启用</label>
                    <input type="number" id="alert-price-change-threshold" placeholder="阈值%" style="width:80px"> % 以上触发
                </div>
                <div class="alert-section">
                    <h4>⚡ 快速波动告警</h4>
                    <label><input type="checkbox" id="alert-rapid-enabled"> 启用</label>
                    <input type="number" id="alert-rapid-minutes" placeholder="30" style="width:60px"> 分钟内涨跌
                    <input type="number" id="alert-rapid-threshold" placeholder="3" style="width:60px"> % 触发
                </div>
                <div class="alert-section">
                    <h4>📊 放量告警</h4>
                    <label><input type="checkbox" id="alert-volume-enabled"> 启用</label>
                    成交量增加 <input type="number" id="alert-volume-threshold" placeholder="50" style="width:60px"> % 触发
                </div>
                <div class="alert-section">
                    <h4>📉 趋势拟合告警</h4>
                    <label><input type="checkbox" id="alert-trend-enabled"> 启用</label>
                    <small>一次+二次+三次函数拟合，三者同向时触发</small>
                </div>
                <div class="alert-section">
                    <h4">🔄 刷新间隔</h4>
                    <input type="number" id="alert-refresh-interval" placeholder="60" style="width:80px"> 秒
                </div>
                <div class="alert-section">
                    <h4">🔔 开盘/收盘推送</h4>
                    <label><input type="checkbox" id="alert-open-enabled"> 开盘推送</label>
                    <label><input type="checkbox" id="alert-close-enabled"> 收盘推送</label>
                </div>
                <button class="btn-add" onclick="saveAlertConfig()" style="margin-top:20px;width:100%">保存配置</button>
            </div>
        </div>
    </div>
    
    <script>
        let stocks = [];
        let autoRefresh = null;
        let minuteChart = null;
        
        // 加载股票列表
        async function loadStocks() {
            const res = await fetch('/api/stocks');
            stocks = await res.json();
            document.getElementById('stockCount').textContent = stocks.length;
            
            // 获取刷新间隔配置
            const alertsRes = await fetch('/api/alerts');
            const alerts = await alertsRes.json();
            const refreshInterval = (alerts.refresh_interval || 60) * 1000;
            
            document.getElementById('interval').textContent = alerts.refresh_interval || 60;
            
            renderStocks();
            startAutoRefresh(refreshInterval);
        }
        
        // 渲染股票卡片
        function renderStocks() {
            const grid = document.getElementById('stockGrid');
            
            if (stocks.length === 0) {
                grid.innerHTML = `
                    <div class="empty-state">
                        <h2>暂无自选股</h2>
                        <p>添加股票代码开始监控</p>
                    </div>
                `;
                return;
            }
            
            grid.innerHTML = stocks.map(s => `
                <div class="stock-card" onclick="showChart('${s.code}')" id="card-${s.code}">
                    <button class="delete-btn" onclick="event.stopPropagation(); deleteStock('${s.code}')">×</button>
                    <div class="stock-name">${s.name || '-'}</div>
                    <div class="stock-code">${s.code}</div>
                    <div class="stock-price ${s.change_pct >= 0 ? 'price-up' : 'price-down'}">
                        ${s.price || '-'}
                    </div>
                    <div class="stock-info">
                        <span class="yesterday-close">昨收: ${s.yesterday_close || '-'}</span>
                        <span class="stock-change ${s.change_pct >= 0 ? 'price-up' : 'price-down'}">
                            ${s.change >= 0 ? '+' : ''}${s.change || 0} (${s.change_pct >= 0 ? '+' : ''}${s.change_pct || 0}%)
                        </span>
                    </div>
                    <div class="stock-time">${s.time || '-'}</div>
                </div>
            `).join('');
        }
        
        // 添加股票
        async function addStock() {
            const input = document.getElementById('stockInput');
            const code = input.value.trim().toUpperCase();
            
            if (!code) return;
            if (!/^\\d{6}$/.test(code)) {
                alert('请输入6位股票代码');
                return;
            }
            
            const res = await fetch('/api/stocks', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({code})
            });
            
            const result = await res.json();
            if (result.success) {
                input.value = '';
                loadStocks();
            } else {
                alert(result.message || '添加失败');
            }
        }
        
        // 删除股票
        async function deleteStock(code) {
            if (!confirm(`确定删除 ${code}?`)) return;
            
            const res = await fetch(`/api/stocks/${code}`, {method: 'DELETE'});
            const result = await res.json();
            if (result.success) {
                loadStocks();
            }
        }
        
        // 刷新数据
        async function refreshData() {
            const res = await fetch('/api/realtime');
            const data = await res.json();
            
            stocks = data;
            renderStocks();
            
            document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
        }
        
        // 自动刷新
        function startAutoRefresh(intervalMs = 60000) {
            if (autoRefresh) clearInterval(autoRefresh);
            autoRefresh = setInterval(refreshData, intervalMs);
            refreshData();
        }
        
        // 回车添加
        document.getElementById('stockInput').addEventListener('keypress', e => {
            if (e.key === 'Enter') addStock();
        });
        
        // 显示图表
        async function showChart(code) {
            const modal = document.getElementById('chartModal');
            const loading = document.getElementById('chartLoading');
            const title = document.getElementById('chartTitle');
            
            modal.classList.add('show');
            loading.style.display = 'block';
            
            // 获取股票名称和昨日收盘价
            const stock = stocks.find(s => s.code === code);
            const yesterdayClose = stock?.yesterday_close;
            title.textContent = `${stock?.name || code} - 分时图 (昨收: ${yesterdayClose || '-'})`;
            
            // 获取分时数据
            const res = await fetch(`/api/minute/${code}`);
            const data = await res.json();
            
            loading.style.display = 'none';
            
            if (!data || data.length === 0) {
                alert('暂无分时数据');
                return;
            }
            
            // 准备图表数据
            const times = data.map(d => d.time);
            const prices = data.map(d => d.close);
            const volumes = data.map(d => d.volume);
            
            // 渲染图表
            const ctx = document.getElementById('minuteChart').getContext('2d');
            
            if (minuteChart) {
                minuteChart.destroy();
            }
            
            const isUp = prices[prices.length - 1] >= (yesterdayClose || prices[0]);
            const color = isUp ? '#ff4757' : '#00ff88';
            
            minuteChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: times,
                    datasets: [
                        {
                            label: '价格',
                            data: prices,
                            borderColor: color,
                            backgroundColor: color + '20',
                            fill: true,
                            yAxisID: 'y',
                            tension: 0.1
                        },
                        {
                            label: '成交量',
                            data: volumes,
                            type: 'bar',
                            backgroundColor: '#333',
                            yAxisID: 'y1'
                        },
                        ...(yesterdayClose ? [{
                            label: '昨日收盘',
                            data: Array(times.length).fill(yesterdayClose),
                            borderColor: '#888',
                            borderDash: [5, 5],
                            borderWidth: 1,
                            pointRadius: 0,
                            yAxisID: 'y'
                        }] : [])
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    plugins: {
                        legend: { labels: { color: '#999' } }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#666', maxTicksLimit: 20 },
                            grid: { color: '#333' }
                        },
                        y: {
                            type: 'linear',
                            position: 'left',
                            ticks: { color: color },
                            grid: { color: '#333' }
                        },
                        y1: {
                            type: 'linear',
                            position: 'right',
                            ticks: { color: '#666' },
                            grid: { display: false }
                        }
                    }
                }
            });
        }
        
        // 关闭弹窗
        function closeModal() {
            document.getElementById('chartModal').classList.remove('show');
        }
        
        // 打开告警配置
        async function openAlertConfig() {
            const res = await fetch('/api/alerts');
            const config = await res.json();
            
            // 刷新间隔
            document.getElementById('alert-refresh-interval').value = config.refresh_interval || 60;
            
            // 涨跌幅告警
            const pc = config.price_change || {};
            document.getElementById('alert-price-change-enabled').checked = pc.enabled !== false;
            document.getElementById('alert-price-change-threshold').value = pc.threshold || 5;
            
            // 快速波动
            const rc = config.rapid_change || {};
            document.getElementById('alert-rapid-enabled').checked = rc.enabled !== false;
            document.getElementById('alert-rapid-minutes').value = rc.minutes || 30;
            document.getElementById('alert-rapid-threshold').value = rc.threshold || 3;
            
            // 放量
            const vs = config.volume_surge || {};
            document.getElementById('alert-volume-enabled').checked = vs.enabled !== false;
            document.getElementById('alert-volume-threshold').value = vs.threshold || 50;
            
            // 趋势拟合
            const tf = config.trend_fit || {};
            document.getElementById('alert-trend-enabled').checked = tf.enabled !== false;
            
            // 开盘/收盘
            const oc = config.open_close_push || {};
            document.getElementById('alert-open-enabled').checked = oc.push_open !== false;
            document.getElementById('alert-close-enabled').checked = oc.push_close !== false;
            
            document.getElementById('alertModal').classList.add('show');
        }
        
        function closeAlertModal() {
            document.getElementById('alertModal').classList.remove('show');
        }
        
        async function saveAlertConfig() {
            const config = {
                refresh_interval: parseInt(document.getElementById('alert-refresh-interval').value) || 60,
                price_change: {
                    enabled: document.getElementById('alert-price-change-enabled').checked,
                    threshold: parseFloat(document.getElementById('alert-price-change-threshold').value) || 5
                },
                rapid_change: {
                    enabled: document.getElementById('alert-rapid-enabled').checked,
                    minutes: parseInt(document.getElementById('alert-rapid-minutes').value) || 30,
                    threshold: parseFloat(document.getElementById('alert-rapid-threshold').value) || 3
                },
                volume_surge: {
                    enabled: document.getElementById('alert-volume-enabled').checked,
                    threshold: parseFloat(document.getElementById('alert-volume-threshold').value) || 50
                },
                trend_fit: {
                    enabled: document.getElementById('alert-trend-enabled').checked
                },
                open_close_push: {
                    enabled: true,
                    push_open: document.getElementById('alert-open-enabled').checked,
                    push_close: document.getElementById('alert-close-enabled').checked
                }
            };
            
            await fetch('/api/alerts', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(config)
            });
            
            alert('配置已保存！');
            closeAlertModal();
        }
        
        // 点击遮罩关闭
        document.getElementById('chartModal').addEventListener('click', e => {
            if (e.target.id === 'chartModal') closeModal();
        });
        
        document.getElementById('alertModal').addEventListener('click', e => {
            if (e.target.id === 'alertModal') closeAlertModal();
        });
        
        // 初始化
        loadStocks();
    </script>
</body>
</html>
'''

# ==================== API路由 ====================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, is_trading=is_trading_time())

@app.route('/api/stocks', methods=['GET'])
def api_get_stocks():
    """获取自选股列表"""
    stocks = get_stocks()
    return jsonify(stocks)

@app.route('/api/stocks', methods=['POST'])
def api_add_stock():
    """添加股票"""
    data = request.get_json()
    code = data.get('code', '').strip().upper()
    
    if not code:
        return jsonify({'success': False, 'message': '股票代码不能为空'})
    
    if not code.isdigit() or len(code) != 6:
        return jsonify({'success': False, 'message': '请输入6位数字代码'})
    
    success = add_stock(code)
    return jsonify({'success': True, 'message': '添加成功' if success else '股票已存在'})

@app.route('/api/stocks/<code>', methods=['DELETE'])
def api_delete_stock(code):
    """删除股票"""
    success = remove_stock(code)
    return jsonify({'success': True})

@app.route('/api/realtime', methods=['GET'])
def api_realtime():
    """获取实时行情"""
    stocks = get_stocks()
    if not stocks:
        return jsonify([])
    
    client = EastMoneyClient()
    results = []
    
    for code in stocks:
        data = client.get_realtime(code)
        if data:
            results.append(data)
            # 同时获取并保存分时数据
            client.fetch_and_save(code)
        time.sleep(0.1)
    
    return jsonify(results)

@app.route('/api/minute/<code>', methods=['GET'])
def api_minute(code):
    """获取分时数据"""
    data = get_minute_data(code)
    return jsonify(data)

@app.route('/api/alerts', methods=['GET'])
def api_get_alerts():
    """获取告警配置"""
    from config import get_alerts_config
    return jsonify(get_alerts_config())

@app.route('/api/alerts', methods=['POST'])
def api_save_alerts():
    """保存告警配置"""
    from config import save_alerts_config
    data = request.get_json()
    save_alerts_config(data)
    return jsonify({'success': True})

# ==================== 主程序 ====================

def main():
    # 启动后台定时任务
    from scheduler import background_task
    from config import load_config
    config = load_config()
    interval = config.get("refresh_interval", 60)
    background_task.start(interval=interval)
    
    print("=" * 50)
    print("A股分时监控服务启动")
    print("=" * 50)
    print("访问 http://localhost:8000 管理自选股")
    print("点击卡片查看分时图")
    print("后台告警任务: 已启动")
    print("按 Ctrl+C 停止服务")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=8000, debug=False)

if __name__ == '__main__':
    main()
