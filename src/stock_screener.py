"""
选股系统
基于多维度评分的龙头股筛选
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import SCREENER_CONFIG
from src.data_manager import DataManager


class StockScreener:
    """选股系统"""
    
    def __init__(self):
        self.dm = DataManager()
        self.config = SCREENER_CONFIG
    
    def screen(self, date=None) -> List[Dict]:
        """
        综合选股
        返回评分最高的候选股列表
        """
        if date is None:
            date = datetime.now().strftime('%Y%m%d')
        
        print(f"\n🚀 开始选股... ({date})")
        
        # ==================== 1. 获取候选股池 ====================
        print("📊 获取候选股池...")
        limit_up_df = self.dm.get_limit_up_stocks(date)
        
        if limit_up_df is None or len(limit_up_df) == 0:
            print("⚠️ 今日无涨停股")
            return []
        
        candidates = []
        
        # ==================== 2. 获取板块资金流 ====================
        print("💰 获取板块资金流...")
        hot_sectors = self.dm.get_hot_sectors(10)
        print(f"   热门板块: {hot_sectors[:5]}")
        
        # ==================== 3. 多维度评分 ====================
        print("🎯 开始多维度评分...")
        
        for _, row in limit_up_df.iterrows():
            try:
                code = str(row.get('代码', ''))
                name = str(row.get('名称', ''))
                symbol = f"sz{code}" if code.startswith('0') or code.startswith('3') else f"sh{code}"
                
                # 获取实时行情
                quote = self.dm.get_stock_quote(symbol)
                if quote is None:
                    continue
                
                # 获取K线
                hist = self.dm.get_stock_hist(symbol, days=30)
                
                # 计算各维度得分
                scores = {
                    '涨停板': self._score_limit_up(row, hist),
                    '资金流': self._score_money_flow(name, hot_sectors),
                    '技术面': self._score_technical(hist),
                    '基本面': self._score_fundamental(quote),
                    '题材': self._score_concept(name),
                }
                
                total_score = sum(scores.values())
                
                candidate = {
                    'code': code,
                    'name': name,
                    'symbol': symbol,
                    'price': quote.get('current', 0),
                    'change': (quote.get('current', 0) - quote.get('last_close', 0)) / quote.get('last_close', 1) * 100,
                    'volume': quote.get('volume', 0),
                    'scores': scores,
                    'total_score': total_score,
                }
                
                candidates.append(candidate)
                
            except Exception as e:
                continue
        
        # 按总分排序
        candidates.sort(key=lambda x: x['total_score'], reverse=True)
        
        # 取前N名
        top_candidates = candidates[:self.config['max_candidates']]
        
        print(f"\n✅ 评分完成，共 {len(top_candidates)} 只候选股")
        
        return top_candidates
    
    def _score_limit_up(self, row, hist) -> float:
        """涨停板因子评分"""
        score = 0
        
        # 连板数
        连续板数 = row.get('连板数', 0)
        if 连续板数 == 1:
            score += 20
        elif 连续板数 == 2:
            score += 28
        elif 连续板数 >= 3:
            score += 35
        
        # 成交额
        成交额 = row.get('成交额', 0)
        if 成交额 > 10e8:  # >10亿
            score += 5
        
        return min(score, self.config['limit_up_weight'])
    
    def _score_money_flow(self, name: str, hot_sectors: List[str]) -> float:
        """资金流因子评分"""
        score = 0
        
        # 是否属于热门板块
        for sector in hot_sectors:
            if sector in name:
                score += 10
                break
        
        return min(score, self.config['money_flow_weight'])
    
    def _score_technical(self, hist) -> float:
        """技术面因子评分"""
        if hist is None or len(hist) < 20:
            return 0
        
        score = 0
        
        try:
            closes = hist['close'].astype(float).values
            
            # 均线多头排列
            ma5 = self.dm.calculate_ma(closes, 5)
            ma10 = self.dm.calculate_ma(closes, 10)
            ma20 = self.dm.calculate_ma(closes, 20)
            
            if ma5 and ma10 and ma20:
                if ma5 > ma10 > ma20:
                    score += 15
                elif ma5 > ma10:
                    score += 8
            
            # RSI超卖
            rsi = self.dm.calculate_rsi(closes)
            if rsi and rsi < 40:
                score += 5
            elif rsi and rsi > 70:
                score -= 5
            
            # 放量上涨
            vol = hist['volume'].astype(float).values
            recent_vol = vol[-5:].mean()
            older_vol = vol[:-5].mean()
            if older_vol > 0 and recent_vol / older_vol > 1.5:
                if closes[-1] > closes[-2]:
                    score += 5
            
        except Exception as e:
            pass
        
        return min(max(score, 0), self.config['technical_weight'])
    
    def _score_fundamental(self, quote) -> float:
        """基本面因子评分"""
        score = 0
        
        # 市盈率（越低越好，但不能为负）
        # 这里简化处理，不做详细财务分析
        score += 5
        
        return min(score, self.config['fundamental_weight'])
    
    def _score_concept(self, name: str) -> float:
        """题材因子评分"""
        score = 0
        
        # 热门题材关键词
        hot_concepts = {
            'AI': 10, '人工智能': 10, '新能源': 8, '锂电': 8,
            '芯片': 10, '半导体': 10, '军工': 8, '机器人': 8,
            '医药': 5, '医疗': 5, '消费': 5, '银行': 3,
            '券商': 5, '光伏': 8, '储能': 8,
        }
        
        name_upper = name.upper()
        for concept, weight in hot_concepts.items():
            if concept.upper() in name_upper:
                score += weight
                break
        
        return min(score, self.config['concept_weight'])
    
    def format_report(self, candidates: List[Dict]) -> str:
        """格式化选股报告"""
        if not candidates:
            return "今日无候选股"
        
        lines = []
        lines.append("# 🎯 龙头股精选报告")
        lines.append(f"## {datetime.now().strftime('%Y年%m月%d日')}")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 📊 综合评分 TOP10")
        lines.append("")
        lines.append("| 排名 | 股票 | 代码 | 评分 | 涨停板 | 资金流 | 技术面 | 题材 |")
        lines.append("|------|------|------|------|--------|--------|--------|------|")
        
        for i, c in enumerate(candidates[:10], 1):
            s = c['scores']
            lines.append(
                f"| {i} | **{c['name']}** | {c['code']} | **{c['total_score']}** | "
                f"{s['涨停板']} | {s['资金流']} | {s['技术面']} | {s['题材']} |"
            )
        
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## ⚠️ 风险提示")
        lines.append("")
        lines.append("1. 仓位控制: 单票≤20%，总仓位≤60%")
        lines.append("2. 止损纪律: 亏损≥8%坚决止损")
        lines.append("3. 情绪管理: 不盲目追高")
        lines.append("")
        lines.append(f"*报告生成时间: {datetime.now().strftime('%H:%M:%S')}*")
        
        return "\n".join(lines)


def test():
    """测试选股系统"""
    print("="*60)
    print("🧪 测试选股系统")
    print("="*60)
    
    screener = StockScreener()
    candidates = screener.screen()
    
    print(f"\n找到 {len(candidates)} 只候选股")
    
    if candidates:
        report = screener.format_report(candidates)
        print("\n" + report)


if __name__ == "__main__":
    test()
