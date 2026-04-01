#!/usr/bin/env python3
"""
贾维斯量化交易系统 v3.0 主入口
用法:
    python main.py --mode report      # 生成每日报告
    python main.py --mode analyze --code 002202  # 分析个股
    python main.py --mode screen      # 选股
    python main.py --mode hot        # 热门涨停
"""
import sys
import argparse
import json

from src.data_manager import JarvisTradingSystem, Signal

def main():
    parser = argparse.ArgumentParser(description='贾维斯量化交易系统 v3.0')
    parser.add_argument('--mode', '-m', default='report',
                      choices=['report', 'analyze', 'screen', 'hot'],
                      help='运行模式')
    parser.add_argument('--code', '-c', help='股票代码')
    
    args = parser.parse_args()
    
    system = JarvisTradingSystem()
    
    if args.mode == 'report':
        print("="*60)
        print("📋 贾维斯每日报告")
        print("="*60)
        
        # 指数
        print("\n【大盘概况】")
        indices = [('sh000001', '上证指数'), ('sz399001', '深证成指'), ('sz399006', '创业板')]
        for symbol, name in indices:
            quote = system.dm.get_realtime_quote(symbol)
            if quote:
                status = "📈" if quote['change_pct'] > 0 else "📉"
                print(f"{status} {name}: {quote['current']:.2f} ({quote['change_pct']:+.2f}%)")
        
        # 选股
        print("\n【今日候选股】")
        candidates = system.screen()
        for i, c in enumerate(candidates[:5], 1):
            status = "🟢" if c['signal'] == Signal.BUY else "🟡" if c['signal'] == Signal.HOLD else "🔴"
            print(f"{i}. {status} {c['name']}({c['code']}) 评分:{c['score']}")
            print(f"   现价:{c['price']:.2f} ({c['change_pct']:+.2f}%)")
        
        print("\n" + "="*60)
    
    elif args.mode == 'analyze':
        code = args.code or '002202'
        print(f"分析股票: {code}")
        result = system.analyze_stock(code)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.mode == 'screen':
        candidates = system.screen()
        for c in candidates[:10]:
            print(f"{c['name']}({c['code']}): 评分={c['score']}")
    
    elif args.mode == 'hot':
        print("【热门涨停】")
        candidates = system.screen()
        for i, c in enumerate(candidates[:5], 1):
            status = "🟢" if c['change_pct'] > 0 else "📉"
            print(f"{i}. {status} {c['name']}({c['code']}) {c['change_pct']:+.2f}%")


if __name__ == "__main__":
    main()
