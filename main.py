#!/usr/bin/env python3
"""
贾维斯量化交易系统 v2.0
改进版 - 基于Qbot最佳实践
- 实时行情获取
- 多策略分析 (MACD/KDJ/布林带)
- 组合信号生成
- 飞书推送
"""
import sys
import argparse
from datetime import datetime
import pandas as pd

# 添加项目路径
sys.path.insert(0, '/root/.openclaw/workspace/jarvis-trading-system')

from config.settings import REPORTS_DIR
from src.data_manager import DataManager
from src.stock_screener import StockScreener
from src.news_collector import NewsCollector
from src.sentiment_monitor import SentimentMonitor
from src.trading_signals import TradingSignals
from src.trading_strategies import CombinedStrategy


class JarvisTradingSystem:
    """贾维斯量化交易系统"""
    
    def __init__(self):
        self.dm = DataManager()
        self.news_collector = NewsCollector()
        self.sentiment_monitor = SentimentMonitor()
        self.strategy = CombinedStrategy()
    
    def get_realtime_quote(self, code: str) -> dict:
        """获取实时行情（今日数据，非昨日）"""
        # 转换代码格式
        if code.startswith('6'):
            symbol = f"sh{code}"
        else:
            symbol = f"sz{code}"
        
        return self.dm.get_stock_quote(symbol)
    
    def analyze_stock(self, code: str) -> dict:
        """综合分析单只股票"""
        print(f"\n📊 分析股票: {code}")
        
        # 获取实时行情
        quote = self.get_realtime_quote(code)
        
        # 获取历史数据
        if code.startswith('6'):
            symbol = f"sh{code}"
        else:
            symbol = f"sz{code}"
        
        hist = self.dm.get_stock_hist(symbol, days=30)
        
        # 策略分析
        strategy_result = self.strategy.analyze(hist)
        
        # 合成结果
        result = {
            'code': code,
            'name': quote.get('name') if quote else code,
            'price': quote.get('current') if quote else 0,
            'change': ((quote.get('current', 0) - quote.get('last_close', 0)) / quote.get('last_close', 1) * 100) if quote else 0,
            'open': quote.get('open') if quote else 0,
            'high': quote.get('high') if quote else 0,
            'low': quote.get('low') if quote else 0,
            'volume': quote.get('volume') if quote else 0,
            'strategy': strategy_result
        }
        
        return result
    
    def get_market_summary(self) -> dict:
        """获取市场实时概况"""
        indices = {
            '上证指数': 'sh000001',
            '深证成指': 'sz399001',
            '创业板': 'sz399006'
        }
        
        summary = {}
        for name, code in indices.items():
            quote = self.get_realtime_quote(code[2:])
            if quote:
                change = ((quote['current'] - quote['last_close']) / quote['last_close'] * 100) if quote['last_close'] else 0
                summary[name] = {
                    'price': quote['current'],
                    'change': change,
                    'status': '📈' if change > 0 else '📉'
                }
        
        return summary
    
    def get_hot_stocks_today(self) -> list:
        """获取今日涨停股（实时数据）"""
        # 获取涨停股数据
        limit_up = self.dm.get_limit_up_stocks()
        
        hot_stocks = []
        if limit_up is not None and len(limit_up) > 0:
            # 按成交额排序取前5
            top = limit_up.nlargest(5, '成交额')
            
            for _, row in top.iterrows():
                code = str(row.get('代码', ''))
                name = str(row.get('名称', ''))
                
                # 获取实时行情
                quote = self.get_realtime_quote(code)
                
                if quote:
                    hot_stocks.append({
                        'code': code,
                        'name': name,
                        'realtime_change': ((quote['current'] - quote['last_close']) / quote['last_close'] * 100) if quote['last_close'] else 0,
                        'current_price': quote['current'],
                        'volume': quote['volume'],
                        'amount': quote['amount']
                    })
        
        return hot_stocks
    
    def generate_daily_report(self) -> str:
        """生成每日报告（使用实时数据）"""
        print("\n" + "="*60)
        print("📋 贾维斯每日报告")
        print("="*60)
        
        # 1. 市场概况
        print("\n【市场概况】")
        market = self.get_market_summary()
        for name, data in market.items():
            print(f"{data['status']} {name}: {data['price']:.2f} ({data['change']:+.2f}%)")
        
        # 2. 今日涨停股实时行情
        print("\n【今日涨停股实时行情】")
        hot = self.get_hot_stocks_today()
        if hot:
            for i, stock in enumerate(hot, 1):
                status = '📈' if stock['realtime_change'] > 0 else '📉'
                print(f"{i}. {status} {stock['name']}({stock['code']}) 现价:{stock['current_price']:.2f} ({stock['realtime_change']:+.2f}%)")
        else:
            print("暂无数据")
        
        # 3. 热门舆情
        print("\n【热门舆情】")
        alert = self.sentiment_monitor.run_once()
        if alert:
            print(alert)
        
        return "报告生成完成"
    
    def analyze_and_report(self, code: str) -> str:
        """分析单只股票并生成报告"""
        result = self.analyze_stock(code)
        
        print(f"\n{'='*60}")
        print(f"📊 {result['name']}({result['code']}) 个股分析")
        print(f"{'='*60}")
        
        print(f"\n【实时行情】")
        print(f"现价: {result['price']:.2f}")
        print(f"涨跌幅: {result['change']:+.2f}%")
        print(f"今开: {result['open']:.2f}")
        print(f"最高: {result['high']:.2f}")
        print(f"最低: {result['low']:.2f}")
        
        print(f"\n【策略分析】")
        strategy = result['strategy']
        print(f"信号: {strategy['signal']}")
        print(f"原因: {strategy['reason']}")
        
        if strategy.get('macd'):
            macd = strategy['macd']
            print(f"MACD: {macd.get('macd', 0):.4f}, Signal: {macd.get('signal', 0):.4f}")
        
        if strategy.get('kdj'):
            kdj = strategy['kdj']
            print(f"KDJ: K={kdj.get('k', 0):.2f}, D={kdj.get('d', 0):.2f}, J={kdj.get('j', 0):.2f}")
        
        return f"分析完成: {result['name']} - {strategy['signal']}"


def run_market_summary():
    """运行市场概况"""
    system = JarvisTradingSystem()
    system.get_market_summary()


def main():
    parser = argparse.ArgumentParser(description='贾维斯量化交易系统 v2.0')
    parser.add_argument('--mode', '-m', default='report',
                      choices=['report', 'analyze', 'hot', 'news', 'sentiment'],
                      help='运行模式')
    parser.add_argument('--code', '-c', help='股票代码(分析模式)')
    
    args = parser.parse_args()
    
    system = JarvisTradingSystem()
    
    if args.mode == 'report':
        system.generate_daily_report()
    
    elif args.mode == 'analyze':
        if not args.code:
            print("请提供股票代码: --code 002202")
            sys.exit(1)
        system.analyze_and_report(args.code)
    
    elif args.mode == 'hot':
        print("\n【今日涨停股实时行情】")
        hot = system.get_hot_stocks_today()
        if hot:
            for i, stock in enumerate(hot, 1):
                status = '📈' if stock['realtime_change'] > 0 else '📉'
                print(f"{i}. {status} {stock['name']}({stock['code']}) 现价:{stock['current_price']:.2f} ({stock['realtime_change']:+.2f}%)")
    
    elif args.mode == 'news':
        news = system.news_collector.get_all_news()
        report = system.news_collector.format_report(news)
        print("\n" + report)
    
    elif args.mode == 'sentiment':
        system.sentiment_monitor.run_once()


if __name__ == "__main__":
    main()
