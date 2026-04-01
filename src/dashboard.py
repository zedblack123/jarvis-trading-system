"""
贾维斯量化交易系统 - Web可视化界面
Flask + Plotly K线图 + 实时行情
"""
import os
import sys
import json
import time
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify, request

# 添加项目路径
sys.path.insert(0, '/root/.openclaw/workspace/jarvis-trading-system')

from src.data_manager import JarvisTradingSystem, DataManager, Signal

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jarvis-quant-2026'

# 全局数据管理器
jarvis = JarvisTradingSystem()
dm = DataManager()

# ==================== 路由 ====================

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/market')
def api_market():
    """大盘指数"""
    indices = [
        ('sh000001', '上证指数'),
        ('sz399001', '深证成指'),
        ('sz399006', '创业板指')
    ]
    
    data = []
    for symbol, name in indices:
        quote = dm.get_realtime_quote(symbol)
        if quote:
            data.append({
                'name': name,
                'price': quote['current'],
                'change_pct': quote['change_pct'],
                'status': 'up' if quote['change_pct'] > 0 else 'down'
            })
    
    return jsonify({'code': 0, 'data': data})

@app.route('/api/hot_stocks')
def api_hot_stocks():
    """热门涨停股"""
    candidates = jarvis.screen()
    
    stocks = []
    for c in candidates[:10]:
        stocks.append({
            'name': c['name'],
            'code': c['code'],
            'price': c['price'],
            'change_pct': c['change_pct'],
            'score': c['score'],
            'signal': c['signal'].value,
            'reason': c.get('tech_reason', '')[:50]
        })
    
    return jsonify({'code': 0, 'data': stocks})

@app.route('/api/stock/<code>')
def api_stock(code):
    """个股K线数据"""
    # 获取K线
    symbol = f"sh{code}" if code.startswith('6') else f"sz{code}"
    df = dm.get_kline(symbol, days=60)
    
    if df is None or len(df) == 0:
        return jsonify({'code': 1, 'msg': '无数据'})
    
    # 转换为K线格式
    kline = []
    for _, row in df.iterrows():
        kline.append({
            'date': row.get('日期', ''),
            'open': float(row.get('开盘', 0)),
            'high': float(row.get('最高', 0)),
            'low': float(row.get('最低', 0)),
            'close': float(row.get('收盘', 0)),
            'volume': int(row.get('成交量', 0))
        })
    
    # 计算技术指标
    closes = df['close'].astype(float).values
    highs = df['high'].astype(float).values
    lows = df['low'].astype(float).values
    
    macd = dm.calculate_macd(closes)
    kdj = dm.calculate_kdj(highs, lows, closes)
    rsi = dm.calculate_rsi(closes)
    
    # 实时行情
    quote = dm.get_realtime_quote(symbol)
    
    return jsonify({
        'code': 0,
        'data': {
            'kline': kline,
            'quote': quote,
            'indicators': {
                'macd': macd,
                'kdj': kdj,
                'rsi': rsi
            }
        }
    })

@app.route('/api/analysis/<code>')
def api_analysis(code):
    """个股技术分析"""
    result = jarvis.analyze_stock(code)
    return jsonify({'code': 0, 'data': result})

# ==================== 启动 ====================

def run_dashboard(host='0.0.0.0', port=5000):
    """启动Dashboard"""
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║     贾维斯量化交易系统 - Web可视化界面                 ║
║     http://localhost:{port}                              ║
╚═══════════════════════════════════════════════════════════╝
    """)
    app.run(host=host, port=port, debug=False, threaded=True)

if __name__ == '__main__':
    run_dashboard()
