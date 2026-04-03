"""
技术分析工具
计算技术指标
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from .base import BaseTool


class TechnicalAnalysisTool(BaseTool):
    """技术分析工具"""
    name = "technical"
    description = "计算技术指标（MA、MACD、KDJ、RSI、布林带等）"
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        计算技术指标
        
        Args:
            stock_code: 股票代码
            price_data: 价格数据列表（格式：[{'date': '2024-01-01', 'close': 10.0, 'high': 11.0, 'low': 9.0, 'volume': 100000}, ...]）
            indicators: 指标列表，如 ['MA', 'MACD', 'KDJ', 'RSI', 'BOLL']
            ma_periods: MA周期列表，如 [5, 10, 20, 60]
            macd_params: MACD参数 (fast, slow, signal)，默认 (12, 26, 9)
            kdj_params: KDJ参数 (n, m1, m2)，默认 (9, 3, 3)
            rsi_period: RSI周期，默认 14
            boll_period: 布林带周期，默认 20
        
        Returns:
            技术指标数据
        """
        stock_code = kwargs.get('stock_code')
        price_data = kwargs.get('price_data', [])
        indicators = kwargs.get('indicators', ['MA', 'MACD', 'KDJ'])
        
        if not stock_code and not price_data:
            return {"error": "缺少股票代码或价格数据"}
        
        try:
            result = {
                "stock_code": stock_code,
                "indicators": indicators,
                "data": []
            }
            
            if price_data:
                # 将价格数据转换为DataFrame
                df = pd.DataFrame(price_data)
                
                # 确保数据按日期排序
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.sort_values('date')
                
                # 计算指标
                indicator_results = {}
                
                # 1. 移动平均线 (MA)
                if 'MA' in indicators:
                    ma_periods = kwargs.get('ma_periods', [5, 10, 20, 60])
                    if 'close' in df.columns:
                        for period in ma_periods:
                            if len(df) >= period:
                                df[f'MA{period}'] = df['close'].rolling(window=period).mean()
                                indicator_results[f'MA{period}'] = df[f'MA{period}'].iloc[-1] if not pd.isna(df[f'MA{period}'].iloc[-1]) else None
                
                # 2. MACD
                if 'MACD' in indicators and 'close' in df.columns:
                    fast_period = kwargs.get('macd_fast', 12)
                    slow_period = kwargs.get('macd_slow', 26)
                    signal_period = kwargs.get('macd_signal', 9)
                    
                    if len(df) >= slow_period:
                        exp1 = df['close'].ewm(span=fast_period, adjust=False).mean()
                        exp2 = df['close'].ewm(span=slow_period, adjust=False).mean()
                        df['MACD_DIF'] = exp1 - exp2
                        df['MACD_DEA'] = df['MACD_DIF'].ewm(span=signal_period, adjust=False).mean()
                        df['MACD'] = 2 * (df['MACD_DIF'] - df['MACD_DEA'])
                        
                        indicator_results['MACD_DIF'] = df['MACD_DIF'].iloc[-1] if not pd.isna(df['MACD_DIF'].iloc[-1]) else None
                        indicator_results['MACD_DEA'] = df['MACD_DEA'].iloc[-1] if not pd.isna(df['MACD_DEA'].iloc[-1]) else None
                        indicator_results['MACD'] = df['MACD'].iloc[-1] if not pd.isna(df['MACD'].iloc[-1]) else None
                
                # 3. KDJ
                if 'KDJ' in indicators and all(col in df.columns for col in ['high', 'low', 'close']):
                    n = kwargs.get('kdj_n', 9)
                    m1 = kwargs.get('kdj_m1', 3)
                    m2 = kwargs.get('kdj_m2', 3)
                    
                    if len(df) >= n:
                        # 计算RSV
                        low_min = df['low'].rolling(window=n).min()
                        high_max = df['high'].rolling(window=n).max()
                        df['RSV'] = 100 * (df['close'] - low_min) / (high_max - low_min)
                        df['RSV'] = df['RSV'].fillna(50)  # 处理除零情况
                        
                        # 计算K、D、J
                        df['K'] = df['RSV'].ewm(alpha=1/m1, adjust=False).mean()
                        df['D'] = df['K'].ewm(alpha=1/m2, adjust=False).mean()
                        df['J'] = 3 * df['K'] - 2 * df['D']
                        
                        indicator_results['K'] = df['K'].iloc[-1] if not pd.isna(df['K'].iloc[-1]) else None
                        indicator_results['D'] = df['D'].iloc[-1] if not pd.isna(df['D'].iloc[-1]) else None
                        indicator_results['J'] = df['J'].iloc[-1] if not pd.isna(df['J'].iloc[-1]) else None
                
                # 4. RSI
                if 'RSI' in indicators and 'close' in df.columns:
                    rsi_period = kwargs.get('rsi_period', 14)
                    
                    if len(df) >= rsi_period:
                        delta = df['close'].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
                        rs = gain / loss
                        df['RSI'] = 100 - (100 / (1 + rs))
                        
                        indicator_results['RSI'] = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else None
                
                # 5. 布林带 (BOLL)
                if 'BOLL' in indicators and 'close' in df.columns:
                    boll_period = kwargs.get('boll_period', 20)
                    
                    if len(df) >= boll_period:
                        df['BOLL_MID'] = df['close'].rolling(window=boll_period).mean()
                        std = df['close'].rolling(window=boll_period).std()
                        df['BOLL_UPPER'] = df['BOLL_MID'] + 2 * std
                        df['BOLL_LOWER'] = df['BOLL_MID'] - 2 * std
                        
                        indicator_results['BOLL_MID'] = df['BOLL_MID'].iloc[-1] if not pd.isna(df['BOLL_MID'].iloc[-1]) else None
                        indicator_results['BOLL_UPPER'] = df['BOLL_UPPER'].iloc[-1] if not pd.isna(df['BOLL_UPPER'].iloc[-1]) else None
                        indicator_results['BOLL_LOWER'] = df['BOLL_LOWER'].iloc[-1] if not pd.isna(df['BOLL_LOWER'].iloc[-1]) else None
                
                # 生成结果
                result['indicator_values'] = indicator_results
                
                # 添加最新数据点
                if not df.empty:
                    latest_data = {}
                    for col in df.columns:
                        if col != 'date':
                            latest_data[col] = df[col].iloc[-1] if not pd.isna(df[col].iloc[-1]) else None
                    
                    result['latest_data'] = latest_data
                    result['latest_date'] = df['date'].iloc[-1].strftime('%Y-%m-%d') if 'date' in df.columns else None
                
                # 生成信号分析
                signals = self._analyze_signals(df, indicator_results)
                result['signals'] = signals
            
            return result
            
        except Exception as e:
            return {"error": f"技术分析失败: {str(e)}"}
    
    def _analyze_signals(self, df: pd.DataFrame, indicators: Dict) -> Dict[str, Any]:
        """分析技术信号"""
        signals = {}
        
        try:
            # 1. MA信号
            if 'MA5' in df.columns and 'MA10' in df.columns and 'MA20' in df.columns:
                ma5 = df['MA5'].iloc[-1]
                ma10 = df['MA10'].iloc[-1]
                ma20 = df['MA20'].iloc[-1]
                
                if not pd.isna(ma5) and not pd.isna(ma10) and not pd.isna(ma20):
                    # 多头排列
                    if ma5 > ma10 > ma20:
                        signals['ma_trend'] = '多头排列'
                    # 空头排列
                    elif ma5 < ma10 < ma20:
                        signals['ma_trend'] = '空头排列'
                    else:
                        signals['ma_trend'] = '震荡排列'
            
            # 2. MACD信号
            if 'MACD_DIF' in df.columns and 'MACD_DEA' in df.columns:
                dif = df['MACD_DIF'].iloc[-1]
                dea = df['MACD_DEA'].iloc[-1]
                
                if not pd.isna(dif) and not pd.isna(dea):
                    if dif > dea and df['MACD_DIF'].iloc[-2] <= df['MACD_DEA'].iloc[-2]:
                        signals['macd_signal'] = '金叉买入'
                    elif dif < dea and df['MACD_DIF'].iloc[-2] >= df['MACD_DEA'].iloc[-2]:
                        signals['macd_signal'] = '死叉卖出'
                    elif dif > dea:
                        signals['macd_signal'] = '多头'
                    else:
                        signals['macd_signal'] = '空头'
            
            # 3. KDJ信号
            if 'K' in df.columns and 'D' in df.columns:
                k = df['K'].iloc[-1]
                d = df['D'].iloc[-1]
                
                if not pd.isna(k) and not pd.isna(d):
                    if k < 20 and d < 20:
                        signals['kdj_signal'] = '超卖'
                    elif k > 80 and d > 80:
                        signals['kdj_signal'] = '超买'
                    elif k > d and df['K'].iloc[-2] <= df['D'].iloc[-2]:
                        signals['kdj_signal'] = '金叉'
                    elif k < d and df['K'].iloc[-2] >= df['D'].iloc[-2]:
                        signals['kdj_signal'] = '死叉'
                    else:
                        signals['kdj_signal'] = '中性'
            
            # 4. RSI信号
            if 'RSI' in df.columns:
                rsi = df['RSI'].iloc[-1]
                if not pd.isna(rsi):
                    if rsi < 30:
                        signals['rsi_signal'] = '超卖'
                    elif rsi > 70:
                        signals['rsi_signal'] = '超买'
                    else:
                        signals['rsi_signal'] = '中性'
            
            # 5. 布林带信号
            if 'close' in df.columns and 'BOLL_UPPER' in df.columns and 'BOLL_LOWER' in df.columns:
                close = df['close'].iloc[-1]
                upper = df['BOLL_UPPER'].iloc[-1]
                lower = df['BOLL_LOWER'].iloc[-1]
                
                if not pd.isna(close) and not pd.isna(upper) and not pd.isna(lower):
                    if close >= upper:
                        signals['boll_signal'] = '触及上轨'
                    elif close <= lower:
                        signals['boll_signal'] = '触及下轨'
                    else:
                        signals['boll_signal'] = '轨道内'
        
        except Exception as e:
            signals['error'] = f"信号分析失败: {str(e)}"
        
        return signals
    
    def get_permission_level(self) -> int:
        """权限等级：技术分析为低权限"""
        return 1