"""
经典技术指标策略
参考Qbot的策略实现
"""
import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple


class TechnicalIndicators:
    """技术指标计算"""
    
    @staticmethod
    def calculate_ma(prices: np.ndarray, period: int) -> Optional[float]:
        """移动平均线"""
        if len(prices) < period:
            return None
        return float(np.mean(prices[-period:]))
    
    @staticmethod
    def calculate_ema(prices: np.ndarray, period: int) -> Optional[float]:
        """指数移动平均线"""
        if len(prices) < period:
            return None
        return float(pd.Series(prices).ewm(span=period, adjust=False).mean().iloc[-1])
    
    @staticmethod
    def calculate_macd(prices: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """
        MACD指标
        返回: {macd, signal, histogram}
        """
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
            'histogram': float(histogram.iloc[-1])
        }
    
    @staticmethod
    def calculate_kdj(high: np.ndarray, low: np.ndarray, close: np.ndarray, 
                     n: int = 9, m1: int = 3, m2: int = 3) -> Dict:
        """
        KDJ指标
        """
        if len(high) < n or len(low) < n or len(close) < n:
            return {'k': None, 'd': None, 'j': None}
        
        lowest_low = pd.Series(low).rolling(window=n).min()
        highest_high = pd.Series(high).rolling(window=n).max()
        
        rsv = (close - lowest_low) / (highest_high - lowest_low) * 100
        
        k = rsv.ewm(com=m1-1, adjust=False).mean()
        d = k.ewm(com=m2-1, adjust=False).mean()
        j = 3 * k - 2 * d
        
        return {
            'k': float(k.iloc[-1]),
            'd': float(d.iloc[-1]),
            'j': float(j.iloc[-1])
        }
    
    @staticmethod
    def calculate_rsi(prices: np.ndarray, period: int = 14) -> Optional[float]:
        """RSI相对强弱指标"""
        if len(prices) < period + 1:
            return None
        
        deltas = np.diff(prices)
        gains = deltas[deltas > 0].sum()
        losses = -deltas[deltas < 0].sum()
        
        if losses == 0:
            return 100.0
        
        rs = gains / losses
        rsi = 100 - (100 / (1 + rs))
        return float(rsi)
    
    @staticmethod
    def calculate_bollinger_bands(prices: np.ndarray, period: int = 20, std_dev: int = 2) -> Dict:
        """布林带指标"""
        if len(prices) < period:
            return {'upper': None, 'middle': None, 'lower': None}
        
        ma = pd.Series(prices).rolling(window=period).mean()
        std = pd.Series(prices).rolling(window=period).std()
        
        upper = ma + std_dev * std
        lower = ma - std_dev * std
        
        return {
            'upper': float(upper.iloc[-1]),
            'middle': float(ma.iloc[-1]),
            'lower': float(lower.iloc[-1])
        }
    
    @staticmethod
    def calculate_volume_ratio(volumes: np.ndarray, period: int = 5) -> float:
        """量比 (近期平均成交量 / 之前平均成交量)"""
        if len(volumes) < period * 2:
            return 1.0
        
        recent_avg = np.mean(volumes[-period:])
        older_avg = np.mean(volumes[-period*2:-period])
        
        if older_avg == 0:
            return 1.0
        return float(recent_avg / older_avg)


class TradingStrategy:
    """交易策略基类"""
    
    def __init__(self):
        self.ti = TechnicalIndicators()
    
    def analyze(self, hist_data: pd.DataFrame) -> Dict:
        """分析返回信号"""
        raise NotImplementedError


class MACDStrategy(TradingStrategy):
    """MACD策略
    
    金叉买入: MACD > Signal 且 histogram 由负转正
    死叉卖出: MACD < Signal 且 histogram 由正转负
    """
    
    def analyze(self, hist_data: pd.DataFrame) -> Dict:
        if hist_data is None or len(hist_data) < 30:
            return {'signal': 'hold', 'reason': '数据不足'}
        
        closes = hist_data['close'].astype(float).values
        
        macd = self.ti.calculate_macd(closes)
        
        if macd['macd'] is None:
            return {'signal': 'hold', 'reason': 'MACD计算失败'}
        
        # 计算前一个MACD
        macd_prev = self.ti.calculate_macd(closes[:-1])
        
        signal = 'hold'
        reason = ''
        
        # 金叉: MACD从下方穿越Signal
        if macd['histogram'] > 0 and (macd_prev['histogram'] is None or macd_prev['histogram'] <= 0):
            if macd['macd'] > macd['signal']:
                signal = 'buy'
                reason = f"MACD金叉买入 (MACD={macd['macd']:.2f}, Signal={macd['signal']:.2f})"
        
        # 死叉: MACD从上方穿越Signal
        elif macd['histogram'] < 0 and (macd_prev['histogram'] is None or macd_prev['histogram'] >= 0):
            if macd['macd'] < macd['signal']:
                signal = 'sell'
                reason = f"MACD死叉卖出 (MACD={macd['macd']:.2f}, Signal={macd['signal']:.2f})"
        
        # MACD多头排列
        elif macd['macd'] > macd['signal'] and macd['histogram'] > 0:
            signal = 'hold'
            reason = f"MACD多头 (继续持有)"
        
        else:
            reason = f"MACD偏弱 (MACD={macd['macd']:.2f})"
        
        return {
            'signal': signal,
            'reason': reason,
            'macd': macd
        }


class KDJStrategy(TradingStrategy):
    """KDJ策略
    
    K线从下往上穿越D线 → 买入
    K线从上往下穿越D线 → 卖出
    J > 100 考虑卖出, J < 0 考虑买入
    """
    
    def analyze(self, hist_data: pd.DataFrame) -> Dict:
        if hist_data is None or len(hist_data) < 20:
            return {'signal': 'hold', 'reason': '数据不足'}
        
        high = hist_data['high'].astype(float).values
        low = hist_data['low'].astype(float).values
        close = hist_data['close'].astype(float).values
        
        kdj = self.ti.calculate_kdj(high, low, close)
        
        if kdj['k'] is None:
            return {'signal': 'hold', 'reason': 'KDJ计算失败'}
        
        # 前一个KDJ
        kdj_prev = self.ti.calculate_kdj(high[:-1], low[:-1], close[:-1])
        
        signal = 'hold'
        reason = ''
        
        # 金叉
        if kdj['k'] > kdj['d'] and (kdj_prev['k'] is None or kdj_prev['k'] <= kdj_prev['d']):
            signal = 'buy'
            reason = f"KDJ金叉 (K={kdj['k']:.2f}, D={kdj['d']:.2f})"
        
        # 死叉
        elif kdj['k'] < kdj['d'] and (kdj_prev['k'] is None or kdj_prev['k'] >= kdj_prev['d']):
            signal = 'sell'
            reason = f"KDJ死叉 (K={kdj['k']:.2f}, D={kdj['d']:.2f})"
        
        # J值超买超卖
        elif kdj['j'] > 90:
            signal = 'sell'
            reason = f"KDJ超买 J={kdj['j']:.2f}"
        elif kdj['j'] < 10:
            signal = 'buy'
            reason = f"KDJ超卖 J={kdj['j']:.2f}"
        
        return {
            'signal': signal,
            'reason': reason,
            'kdj': kdj
        }


class CombinedStrategy(TradingStrategy):
    """组合策略 - 结合MACD、KDJ、均线"""
    
    def __init__(self):
        super().__init__()
        self.macd_strategy = MACDStrategy()
        self.kdj_strategy = KDJStrategy()
    
    def analyze(self, hist_data: pd.DataFrame) -> Dict:
        if hist_data is None or len(hist_data) < 30:
            return {'signal': 'hold', 'reason': '数据不足'}
        
        macd_signal = self.macd_strategy.analyze(hist_data)
        kdj_signal = self.kdj_strategy.analyze(hist_data)
        
        # 综合判断
        buy_signals = 0
        sell_signals = 0
        
        if macd_signal['signal'] == 'buy':
            buy_signals += 1
        if macd_signal['signal'] == 'sell':
            sell_signals += 1
        if kdj_signal['signal'] == 'buy':
            buy_signals += 1
        if kdj_signal['signal'] == 'sell':
            sell_signals += 1
        
        # 均线判断
        closes = hist_data['close'].astype(float).values
        ma5 = self.ti.calculate_ma(closes, 5)
        ma10 = self.ti.calculate_ma(closes, 10)
        ma20 = self.ti.calculate_ma(closes, 20)
        
        if ma5 and ma10 and ma20:
            if ma5 > ma10 > ma20:
                buy_signals += 2  # 多头排列强信号
            elif ma5 < ma10 < ma20:
                sell_signals += 2
        
        # 最终决策
        if buy_signals > sell_signals:
            final_signal = 'buy'
        elif sell_signals > buy_signals:
            final_signal = 'sell'
        else:
            final_signal = 'hold'
        
        reasons = []
        if macd_signal['signal'] != 'hold':
            reasons.append(f"MACD: {macd_signal['reason']}")
        if kdj_signal['signal'] != 'hold':
            reasons.append(f"KDJ: {kdj_signal['reason']}")
        
        return {
            'signal': final_signal,
            'reason': '; '.join(reasons) if reasons else '无明确信号',
            'macd': macd_signal.get('macd'),
            'kdj': kdj_signal.get('kdj'),
            'scores': {
                'buy_signals': buy_signals,
                'sell_signals': sell_signals
            }
        }


def test():
    """测试策略"""
    print("="*60)
    print("🧪 测试交易策略")
    print("="*60)
    
    # 模拟数据
    dates = pd.date_range('2026-03-01', periods=30)
    np.random.seed(42)
    base_price = 20.0
    prices = base_price + np.cumsum(np.random.randn(30) * 0.5)
    
    hist_data = pd.DataFrame({
        'date': dates,
        'open': prices + np.random.randn(30) * 0.2,
        'high': prices + abs(np.random.randn(30) * 0.5),
        'low': prices - abs(np.random.randn(30) * 0.5),
        'close': prices,
        'volume': np.random.randint(1000000, 5000000, 30)
    })
    
    # 测试MACD策略
    print("\n📊 MACD策略分析:")
    macd_strategy = MACDStrategy()
    result = macd_strategy.analyze(hist_data)
    print(f"信号: {result['signal']}")
    print(f"原因: {result['reason']}")
    
    # 测试KDJ策略
    print("\n📊 KDJ策略分析:")
    kdj_strategy = KDJStrategy()
    result = kdj_strategy.analyze(hist_data)
    print(f"信号: {result['signal']}")
    print(f"原因: {result['reason']}")
    
    # 测试组合策略
    print("\n📊 组合策略分析:")
    combined = CombinedStrategy()
    result = combined.analyze(hist_data)
    print(f"信号: {result['signal']}")
    print(f"原因: {result['reason']}")
    print(f"买入信号数: {result['scores']['buy_signals']}")
    print(f"卖出信号数: {result['scores']['sell_signals']}")


if __name__ == "__main__":
    test()
