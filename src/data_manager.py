"""
贾维斯量化交易系统 v3.0
参考Qbot架构，结合A股市场特点
"""
import os
import sys
import json
import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# ==================== 配置 ====================

@dataclass
class Config:
    """全局配置"""
    WORKSPACE: str = "/root/.openclaw/workspace"
    DATA_DIR: str = ""
    CACHE_DIR: str = ""
    TUSHARE_TOKEN: str = ""
    DEEPSEEK_API_KEY: str = ""
    STOP_LOSS: float = 0.08
    TAKE_PROFIT: float = 0.15
    MAX_POSITION: float = 0.2
    MAX_TOTAL_POSITION: float = 0.6
    FEISHU_USER_OPEN_ID: str = "ou_636754d2a4956be2f5928918767a62e7"
    
    def __post_init__(self):
        self.DATA_DIR = os.path.join(self.WORKSPACE, "data")
        self.CACHE_DIR = os.path.join(self.DATA_DIR, "cache")
        os.makedirs(self.DATA_DIR, exist_ok=True)
        os.makedirs(self.CACHE_DIR, exist_ok=True)
        
        deepseek_key_file = os.path.join(self.WORKSPACE, ".deepseek_key")
        if os.path.exists(deepseek_key_file):
            with open(deepseek_key_file, 'r') as f:
                self.DEEPSEEK_API_KEY = f.read().strip()

CONFIG = Config()

class Signal(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    WATCH = "watch"

class DataManager:
    """数据管理器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.cache = {}
        self.cache_ttl = 60
    
    def _get_cache(self, key):
        if key in self.cache:
            data, ts = self.cache[key]
            if time.time() - ts < self.cache_ttl:
                return data
        return None
    
    def _set_cache(self, key, data):
        self.cache[key] = (data, time.time())
    
    def get_realtime_quote(self, symbol):
        """获取实时行情"""
        cache_key = f"quote_{symbol}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        url = f"https://qt.gtimg.cn/q={symbol}"
        try:
            resp = self.session.get(url, timeout=5)
            data = resp.content.decode('gbk')
            if '~' not in data:
                return None
            parts = data.split('="')[1].strip('";').split('~')
            if len(parts) < 35:
                return None
            current = float(parts[3]) if parts[3] else 0
            last_close = float(parts[4]) if parts[4] else 0
            change_pct = ((current - last_close) / last_close * 100) if last_close > 0 else 0
            return {
                'symbol': symbol,
                'name': parts[1],
                'current': current,
                'last_close': last_close,
                'open': float(parts[5]) if parts[5] else 0,
                'volume': float(parts[6]) if parts[6] else 0,
                'amount': float(parts[7]) if parts[7] else 0,
                'high': float(parts[33]) if parts[33] else 0,
                'low': float(parts[34]) if parts[34] else 0,
                'change_pct': change_pct
            }
        except Exception as e:
            print(f"获取行情失败 {symbol}: {e}")
            return None
    
    def get_kline(self, symbol, days=30):
        """获取K线"""
        cache_key = f"kline_{symbol}_{days}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        try:
            import akshare as ak
            if symbol.startswith('sz'):
                ts_symbol = symbol[2:] + '.SZ'
            elif symbol.startswith('sh'):
                ts_symbol = symbol[2:] + '.SH'
            else:
                ts_symbol = symbol
            end = datetime.now().strftime('%Y%m%d')
            start = (datetime.now() - timedelta(days=days*2)).strftime('%Y%m%d')
            df = ak.stock_zh_a_hist(symbol=ts_symbol[:6], period='daily',
                                   start_date=start, end_date=end, adjust='qfq')
            if df is not None and len(df) > 0:
                self._set_cache(cache_key, df)
                return df
        except Exception as e:
            print(f"获取K线失败: {e}")
        return None
    
    def get_limit_up_pool(self, date=None):
        """获取涨停股池"""
        if date is None:
            date = datetime.now().strftime('%Y%m%d')
        cache_key = f"limit_up_{date}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        try:
            import akshare as ak
            df = ak.stock_zt_pool_em(date=date)
            if df is not None and len(df) > 0:
                df = df[~df.get('名称', '').str.contains('ST', na=False)]
                self._set_cache(cache_key, df)
                return df
        except Exception as e:
            print(f"获取涨停股池失败: {e}")
        return None
    
    def get_sector_flow(self):
        """获取板块资金流"""
        cache_key = "sector_flow"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        try:
            import akshare as ak
            df = ak.stock_sector_fund_flow_rank(indicator="今日")
            if df is not None and len(df) > 0:
                self._set_cache(cache_key, df)
                return df
        except Exception as e:
            print(f"获取板块资金流失败: {e}")
        return None
    
    def get_hot_sectors(self, top_n=10):
        """获取热门板块"""
        df = self.get_sector_flow()
        if df is None or len(df) == 0:
            return []
        if '今日主力净流入-净额' in df.columns:
            top = df.nlargest(top_n, '今日主力净流入-净额')
            return top['名称'].tolist()[:top_n]
        return []
    
    @staticmethod
    def calculate_ma(prices, period):
        if len(prices) < period:
            return None
        return float(np.mean(prices[-period:]))
    
    @staticmethod
    def calculate_macd(prices, fast=12, slow=26, signal=9):
        if len(prices) < slow:
            return {'macd': None, 'signal': None, 'histogram': None}
        ema_fast = pd.Series(prices).ewm(span=fast, adjust=False).mean()
        ema_slow = pd.Series(prices).ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return {
            'macd': float(macd_line.iloc[-1]),
            'signal': float(signal_line.iloc[-1]),
            'histogram': float(histogram.iloc[-1]),
            'histogram_prev': float(histogram.iloc[-2]) if len(histogram) > 1 else 0
        }
    
    @staticmethod
    def calculate_kdj(high, low, close, n=9, m1=3, m2=3):
        if len(high) < n or len(low) < n or len(close) < n:
            return {'k': None, 'd': None, 'j': None}
        lowest_low = pd.Series(low).rolling(window=n).min()
        highest_high = pd.Series(high).rolling(window=n).max()
        rsv = (close - lowest_low) / (highest_high - lowest_low) * 100
        rsv = rsv.fillna(50)
        k = rsv.ewm(com=m1-1, adjust=False).mean()
        d = k.ewm(com=m2-1, adjust=False).mean()
        j = 3 * k - 2 * d
        return {
            'k': float(k.iloc[-1]),
            'd': float(d.iloc[-1]),
            'j': float(j.iloc[-1]),
            'k_prev': float(k.iloc[-2]) if len(k) > 1 else 50,
            'd_prev': float(d.iloc[-2]) if len(d) > 1 else 50
        }
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        if len(prices) < period + 1:
            return None
        deltas = np.diff(prices)
        gains = deltas[deltas > 0].sum()
        losses = -deltas[deltas < 0].sum()
        if losses == 0:
            return 100.0
        rs = gains / losses
        return float(100 - (100 / (1 + rs)))


class StrategyEngine:
    """策略引擎"""
    
    def __init__(self, dm):
        self.dm = dm
    
    def analyze_technical(self, symbol):
        """技术分析"""
        df = self.dm.get_kline(symbol, days=60)
        if df is None or len(df) < 30:
            return {'signal': Signal.HOLD, 'reason': '数据不足'}
        
        closes = df['close'].astype(float).values
        highs = df['high'].astype(float).values
        lows = df['low'].astype(float).values
        
        macd = self.dm.calculate_macd(closes)
        kdj = self.dm.calculate_kdj(highs, lows, closes)
        rsi = self.dm.calculate_rsi(closes)
        ma5 = self.dm.calculate_ma(closes, 5)
        ma10 = self.dm.calculate_ma(closes, 10)
        ma20 = self.dm.calculate_ma(closes, 20)
        
        buy_signals = 0
        sell_signals = 0
        reasons = []
        
        # MACD
        if macd['histogram'] and macd['histogram_prev'] is not None:
            if macd['histogram'] > 0 and macd['histogram_prev'] <= 0 and macd['macd'] > macd['signal']:
                buy_signals += 2
                reasons.append(f"MACD金叉")
            elif macd['histogram'] < 0 and macd['histogram_prev'] >= 0 and macd['macd'] < macd['signal']:
                sell_signals += 2
                reasons.append(f"MACD死叉")
            elif macd['histogram'] > 0:
                buy_signals += 1
                reasons.append("MACD多头")
        
        # KDJ
        if kdj['k'] and kdj['d']:
            if kdj['k'] > kdj['d'] and kdj['k_prev'] <= kdj['d_prev']:
                buy_signals += 2
                reasons.append("KDJ金叉")
            elif kdj['k'] < kdj['d'] and kdj['k_prev'] >= kdj['d_prev']:
                sell_signals += 2
                reasons.append("KDJ死叉")
            if kdj['j'] > 90:
                sell_signals += 1
                reasons.append(f"KDJ超买")
            elif kdj['j'] < 10:
                buy_signals += 1
                reasons.append(f"KDJ超卖")
        
        # RSI
        if rsi:
            if rsi > 70:
                sell_signals += 1
                reasons.append(f"RSI超买({rsi:.1f})")
            elif rsi < 30:
                buy_signals += 1
                reasons.append(f"RSI超卖({rsi:.1f})")
        
        # MA
        if ma5 and ma10 and ma20:
            if ma5 > ma10 > ma20:
                buy_signals += 2
                reasons.append("均线多头")
            elif ma5 < ma10 < ma20:
                sell_signals += 2
                reasons.append("均线空头")
        
        if buy_signals > sell_signals + 1:
            signal = Signal.BUY
        elif sell_signals > buy_signals + 1:
            signal = Signal.SELL
        else:
            signal = Signal.HOLD
        
        return {
            'signal': signal,
            'reason': '; '.join(reasons) if reasons else '无明确信号',
            'macd': macd,
            'kdj': kdj,
            'rsi': rsi,
            'ma': {'ma5': ma5, 'ma10': ma10, 'ma20': ma20},
            'scores': {'buy': buy_signals, 'sell': sell_signals}
        }
    
    def screen_stocks(self, date=None):
        """选股"""
        print("开始选股...")
        limit_up_df = self.dm.get_limit_up_pool(date)
        if limit_up_df is None or len(limit_up_df) == 0:
            print("无涨停股数据")
            return []
        
        hot_sectors = self.dm.get_hot_sectors(10)
        candidates = []
        
        for _, row in limit_up_df.iterrows():
            code = str(row.get('代码', ''))
            name = str(row.get('名称', ''))
            symbol = f"sz{code}" if not code.startswith('6') else f"sh{code}"
            
            if 'ST' in name or '*ST' in name:
                continue
            
            quote = self.dm.get_realtime_quote(symbol)
            if quote is None:
                continue
            
            tech = self.analyze_technical(symbol)
            
            score = 0
            score_details = {}
            
            # 涨停板因子
            连板数 = row.get('连板数', 0)
            if 连板数 == 1:
                score += 20
            elif 连板数 == 2:
                score += 28
            elif 连板数 >= 3:
                score += 35
            score_details['涨停'] = score
            
            # 技术因子
            tech_score = min(tech.get('scores', {}).get('buy', 0) * 3, 25)
            score += tech_score
            score_details['技术'] = tech_score
            
            # 题材
            concept_keywords = {'AI': 10, '新能源': 8, '芯片': 10, '军工': 8, '机器人': 8, '医药': 5}
            for kw, w in concept_keywords.items():
                if kw in name:
                    score += w
                    score_details['题材'] = w
                    break
            if '题材' not in score_details:
                score_details['题材'] = 0
            
            candidates.append({
                'code': code,
                'name': name,
                'symbol': symbol,
                'price': quote.get('current', 0),
                'change_pct': quote.get('change_pct', 0),
                'volume': quote.get('volume', 0),
                'amount': quote.get('amount', 0),
                'score': score,
                'score_details': score_details,
                'signal': tech['signal'],
                'tech_reason': tech['reason']
            })
        
        candidates.sort(key=lambda x: x['score'], reverse=True)
        print(f"选股完成: {len(candidates)} 只候选股")
        return candidates[:20]


class JarvisTradingSystem:
    """贾维斯量化交易系统"""
    
    def __init__(self):
        print("贾维斯量化交易系统 v3.0 初始化...")
        self.dm = DataManager()
        self.strategy = StrategyEngine(self.dm)
        print("系统就绪")
    
    def get_realtime(self, code):
        """获取实时行情"""
        symbol = f"sh{code}" if code.startswith('6') else f"sz{code}"
        return self.dm.get_realtime_quote(symbol)
    
    def analyze_stock(self, code):
        """分析单只股票"""
        quote = self.get_realtime(code)
        if not quote:
            return {'error': '获取行情失败'}
        symbol = f"sh{code}" if code.startswith('6') else f"sz{code}"
        tech = self.strategy.analyze_technical(symbol)
        return {
            'code': code,
            'name': quote['name'],
            'price': quote['current'],
            'change_pct': quote['change_pct'],
            'open': quote['open'],
            'high': quote['high'],
            'low': quote['low'],
            'volume': quote['volume'],
            'technical': tech
        }
    
    def screen(self):
        """选股"""
        return self.strategy.screen_stocks()


if __name__ == "__main__":
    system = JarvisTradingSystem()
    
    # Test
    print("\n=== 实时行情 ===")
    quote = system.get_realtime('002202')
    if quote:
        print(f"金风科技: {quote['name']} 现价:{quote['current']:.2f} ({quote['change_pct']:+.2f}%)")
    
    print("\n=== 选股结果 ===")
    candidates = system.screen()
    for c in candidates[:5]:
        print(f"{c['name']}({c['code']}): 评分={c['score']} 信号={c['signal'].value}")
