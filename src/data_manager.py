"""
数据管理器
统一管理AKShare、Tushare数据源
"""
import os
import sys
import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import (
    DATA_DIR, CACHE_DIR, TUSHARE_TOKEN, TUSHARE_API_URL,
    CACHE_EXPIRY_MINUTES, CACHE_EXPIRY_MINUTES
)


class DataManager:
    """数据管理器"""
    
    def __init__(self, use_cache=True):
        self.use_cache = use_cache
        self.cache_dir = Path(CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化AKShare
        try:
            import akshare as ak
            self.ak = ak
            print("✅ AKShare 初始化成功")
        except ImportError:
            print("⚠️ AKShare 未安装")
            self.ak = None
        
        # 初始化Tushare
        self.ts_token = TUSHARE_TOKEN
        self.ts_api_url = TUSHARE_API_URL
    
    def _get_cache(self, key):
        """获取缓存"""
        if not self.use_cache:
            return None
        
        cache_file = self.cache_dir / f"{key}.json"
        if not cache_file.exists():
            return None
        
        with open(cache_file, 'r') as f:
            data = json.load(f)
        
        cache_time = datetime.fromisoformat(data['timestamp'])
        if (datetime.now() - cache_time).seconds > CACHE_EXPIRY_MINUTES * 60:
            return None
        
        return data.get('value')
    
    def _set_cache(self, key, value):
        """设置缓存"""
        cache_file = self.cache_dir / f"{key}.json"
        data = {
            'timestamp': datetime.now().isoformat(),
            'value': value
        }
        with open(cache_file, 'w') as f:
            json.dump(data, f)
    
    # ==================== 指数数据 ====================
    
    def get_index_quote(self, symbol="000001.SH"):
        """获取指数行情"""
        cache_key = f"index_{symbol}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return pd.DataFrame(cached)
        
        if self.ak is None:
            return None
        
        try:
            df = self.ak.stock_zh_index_spot_em()
            if df is not None:
                result = df[df['代码'] == symbol[2:]].to_dict('records')
                self._set_cache(cache_key, result)
                return pd.DataFrame(result)
        except Exception as e:
            print(f"获取指数失败: {e}")
        
        return None
    
    # ==================== 个股数据 ====================
    
    def get_stock_quote(self, symbol):
        """获取个股行情（腾讯接口）"""
        # symbol: e.g., "sz002202" or "sh600519"
        url = f"https://qt.gtimg.cn/q={symbol}"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Referer': 'https://stock.tencent.com/'
            }
            resp = requests.get(url, headers=headers, timeout=5)
            data = resp.content.decode('gbk')
            
            if '~' in data:
                data = data.split('="')[1].strip('";')
                parts = data.split('~')
                
                if len(parts) >= 35:
                    return {
                        'name': parts[1],
                        'symbol': symbol,
                        'current': float(parts[3]) if parts[3] else 0,
                        'last_close': float(parts[4]) if parts[4] else 0,
                        'open': float(parts[5]) if parts[5] else 0,
                        'high': float(parts[33]) if parts[33] else 0,
                        'low': float(parts[34]) if parts[34] else 0,
                        'volume': float(parts[6]) if parts[6] else 0,
                        'amount': float(parts[7]) if parts[7] else 0,
                    }
        except Exception as e:
            print(f"获取个股行情失败 {symbol}: {e}")
        
        return None
    
    def get_stock_hist(self, symbol, days=30):
        """获取个股历史K线"""
        if self.ak is None:
            return None
        
        # 转换symbol格式
        if symbol.startswith('sz'):
            ts_symbol = symbol[2:] + '.SZ'
        elif symbol.startswith('sh'):
            ts_symbol = symbol[2:] + '.SH'
        else:
            ts_symbol = symbol
        
        end = datetime.now().strftime('%Y%m%d')
        start = (datetime.now() - timedelta(days=days*2)).strftime('%Y%m%d')
        
        try:
            df = self.ak.stock_zh_a_hist(symbol=ts_symbol[:6], period='daily', 
                                        start_date=start, end_date=end, adjust='qfq')
            return df
        except Exception as e:
            print(f"获取K线失败 {symbol}: {e}")
        
        return None
    
    # ==================== 涨停板 ====================
    
    def get_limit_up_stocks(self, date=None):
        """获取涨停股池"""
        if date is None:
            date = datetime.now().strftime('%Y%m%d')
        
        cache_key = f"limit_up_{date}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return pd.DataFrame(cached)
        
        if self.ak is None:
            return None
        
        try:
            df = self.ak.stock_zt_pool_em(date=date)
            if df is not None and len(df) > 0:
                # 排除ST
                df = df[~df.get('名称', '').str.contains('ST', na=False)]
                result = df.to_dict('records')
                self._set_cache(cache_key, result)
                return df
        except Exception as e:
            print(f"获取涨停股失败: {e}")
        
        return None
    
    # ==================== 板块资金流 ====================
    
    def get_sector_flow(self):
        """获取板块资金流"""
        cache_key = "sector_flow"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return pd.DataFrame(cached)
        
        if self.ak is None:
            return None
        
        try:
            df = self.ak.stock_sector_fund_flow_rank(indicator="今日")
            if df is not None and len(df) > 0:
                result = df.to_dict('records')
                self._set_cache(cache_key, result)
                return df
        except Exception as e:
            print(f"获取板块资金流失败: {e}")
        
        return None
    
    def get_hot_sectors(self, top_n=10):
        """获取热门板块"""
        df = self.get_sector_flow()
        if df is None or len(df) == 0:
            return []
        
        # 按主力净流入排序
        if '今日主力净流入-净额' in df.columns:
            top = df.nlargest(top_n, '今日主力净流入-净额')
            return top['名称'].tolist()[:top_n]
        
        return []
    
    # ==================== 工具方法 ====================
    
    def calculate_ma(self, prices, period):
        """计算移动平均线"""
        if len(prices) < period:
            return None
        return np.mean(prices[-period:])
    
    def calculate_rsi(self, prices, period=14):
        """计算RSI"""
        if len(prices) < period + 1:
            return None
        
        deltas = np.diff(prices)
        gains = deltas[deltas > 0].sum()
        losses = -deltas[deltas < 0].sum()
        
        if losses == 0:
            return 100
        
        rs = gains / losses
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def detect_ma多头排列(self, df, periods=[5, 10, 20]):
        """检测均线多头排列"""
        if df is None or len(df) < max(periods):
            return False
        
        closes = df['close'].astype(float).values
        
        mas = []
        for p in periods:
            ma = self.calculate_ma(closes, p)
            if ma is None:
                return False
            mas.append(ma)
        
        # 多头排列：短期 > 中期 > 长期
        return mas[0] > mas[1] > mas[2]


def test():
    """测试数据管理器"""
    dm = DataManager()
    
    print("\n=== 测试1: 获取金风科技行情 ===")
    quote = dm.get_stock_quote("sz002202")
    if quote:
        print(f"名称: {quote['name']}")
        print(f"现价: {quote['current']}")
        print(f"涨跌幅: {(quote['current'] - quote['last_close']) / quote['last_close'] * 100:.2f}%")
    
    print("\n=== 测试2: 获取涨停股 ===")
    zt = dm.get_limit_up_stocks()
    if zt is not None:
        print(f"涨停股数量: {len(zt)}")
    
    print("\n=== 测试3: 获取板块资金流 ===")
    sectors = dm.get_hot_sectors(5)
    print(f"热门板块: {sectors}")
    
    print("\n✅ 数据管理器测试完成")


if __name__ == "__main__":
    test()
