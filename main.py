#!/usr/bin/env python3
"""
贾维斯量化交易系统
主入口
"""
import sys
import argparse
from datetime import datetime

# 添加项目路径
sys.path.insert(0, '/root/.openclaw/workspace/jarvis-trading-system')

from src.report_generator import ReportGenerator
from src.sentiment_monitor import SentimentMonitor
from src.stock_screener import StockScreener
from src.news_collector import NewsCollector
from src.data_manager import DataManager


def run_morning(mode='report'):
    """早间报告"""
    print("="*60)
    print("🌅 贾维斯早间报告")
    print("="*60)
    
    generator = ReportGenerator()
    report = generator.generate_morning_report()
    
    if mode == 'report':
        print("\n" + report)
    
    return report


def run_hot(mode='report'):
    """热点推送"""
    print("="*60)
    print("🔥 集合竞价热点推送")
    print("="*60)
    
    generator = ReportGenerator()
    report = generator.generate_hot_report()
    
    if mode == 'report':
        print("\n" + report)
    
    return report


def run_evening(mode='report'):
    """晚间报告"""
    print("="*60)
    print("🌙 贾维斯晚间报告")
    print("="*60)
    
    generator = ReportGenerator()
    report = generator.generate_evening_report()
    
    if mode == 'report':
        print("\n" + report)
    
    return report


def run_sentiment():
    """舆情监控"""
    print("="*60)
    print("🔥 舆情监控")
    print("="*60)
    
    monitor = SentimentMonitor()
    alert = monitor.run_once()
    
    if alert:
        print("\n" + alert)
        return alert
    
    return None


def run_stock_query(code):
    """查询个股"""
    print("="*60)
    print(f"📊 查询个股: {code}")
    print("="*60)
    
    dm = DataManager()
    
    # 添加交易所前缀
    if code.startswith('6'):
        symbol = f"sh{code}"
    else:
        symbol = f"sz{code}"
    
    quote = dm.get_stock_quote(symbol)
    
    if quote:
        print(f"\n名称: {quote['name']}")
        print(f"代码: {quote['symbol']}")
        print(f"现价: {quote['current']:.2f}")
        print(f"昨收: {quote['last_close']:.2f}")
        change = (quote['current'] - quote['last_close']) / quote['last_close'] * 100
        print(f"涨跌: {change:+.2f}%")
        print(f"今开: {quote['open']:.2f}")
        print(f"最高: {quote['high']:.2f}")
        print(f"最低: {quote['low']:.2f}")
        print(f"成交量: {quote['volume']/10000:.2f}万手")
        print(f"成交额: {quote['amount']/10000:.2f}万")
    else:
        print("获取数据失败")
    
    return quote


def run_news():
    """最新新闻"""
    print("="*60)
    print("📰 最新财经新闻")
    print("="*60)
    
    collector = NewsCollector()
    news = collector.get_all_news()
    
    report = collector.format_report(news)
    print("\n" + report)
    
    return report


def run_screener():
    """选股"""
    print("="*60)
    print("🎯 选股系统")
    print("="*60)
    
    screener = StockScreener()
    candidates = screener.screen()
    
    report = screener.format_report(candidates)
    print("\n" + report)
    
    return candidates


def main():
    parser = argparse.ArgumentParser(description='贾维斯量化交易系统')
    parser.add_argument('--mode', '-m', default='morning',
                      choices=['morning', 'hot', 'evening', 'sentiment', 
                              'query', 'news', 'screener', 'daily'],
                      help='运行模式')
    parser.add_argument('--code', '-c', help='股票代码(查询模式)')
    parser.add_argument('--start', help='回测开始日期')
    parser.add_argument('--end', help='回测结束日期')
    
    args = parser.parse_args()
    
    if args.mode == 'morning':
        run_morning()
    elif args.mode == 'hot':
        run_hot()
    elif args.mode == 'evening':
        run_evening()
    elif args.mode == 'sentiment':
        run_sentiment()
    elif args.mode == 'query':
        if not args.code:
            print("请提供股票代码: --code 002202")
            sys.exit(1)
        run_stock_query(args.code)
    elif args.mode == 'news':
        run_news()
    elif args.mode == 'screener':
        run_screener()
    elif args.mode == 'daily':
        print("\n" + "="*60)
        print("📅 贾维斯每日完整流程")
        print("="*60)
        run_morning()
        run_hot()
        run_evening()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
