"""
交易信号生成器
基于选股结果生成交易信号
"""
from datetime import datetime
from typing import List, Dict, Optional


class TradingSignals:
    """交易信号生成器"""
    
    def __init__(self):
        self.position = 0  # 当前持仓
        self.cash = 100000  # 模拟资金10万
        self.stocks = {}  # 持仓明细 {code: {name, shares, cost, entry_price}}
    
    def generate_signals(self, candidates: List[Dict], market_data: Dict) -> List[Dict]:
        """
        生成交易信号
        """
        signals = []
        
        # 市场情绪
        sentiment = market_data.get('sentiment', 'neutral')
        
        for candidate in candidates[:5]:  # 取前5
            signal = self._analyze_stock(candidate, sentiment)
            if signal:
                signals.append(signal)
        
        return signals
    
    def _analyze_stock(self, candidate: Dict, sentiment: str) -> Optional[Dict]:
        """
        分析单只股票
        """
        score = candidate.get('total_score', 0)
        change = candidate.get('change', 0)
        price = candidate.get('price', 0)
        
        # 评分门槛
        if score < 40:
            return None
        
        # 涨幅门槛
        if change > 9.5:  # 接近涨停
            action = "观望"
            reason = "涨幅过大，追高风险高"
        elif change > 5:
            action = "轻仓试探"
            reason = "已有一定涨幅，谨慎参与"
        elif change > 0:
            action = "可以考虑"
            reason = "温和上涨，可择机参与"
        elif change > -3:
            action = "关注"
            reason = "小幅回调，关注企稳信号"
        else:
            action = "观望"
            reason = "下跌趋势，暂不参与"
        
        # 结合市场情绪
        if sentiment == 'bearish':
            if action in ["可以考虑", "关注"]:
                action = "观望"
                reason += "，市场情绪偏弱"
        
        # 计算建议仓位
        position_size = self._calculate_position_size(score, action)
        
        return {
            'code': candidate.get('code'),
            'name': candidate.get('name'),
            'score': score,
            'price': price,
            'change': change,
            'action': action,
            'reason': reason,
            'position_size': position_size,
            'risk_level': self._assess_risk(candidate),
        }
    
    def _calculate_position_size(self, score: int, action: str) -> float:
        """计算建议仓位"""
        if action == "观望":
            return 0
        
        base_size = (score - 40) / 60  # 40-100分对应0-100%
        
        if action == "关注":
            return base_size * 0.3
        elif action == "轻仓试探":
            return base_size * 0.5
        elif action == "可以考虑":
            return base_size * 0.8
        
        return 0
    
    def _assess_risk(self, candidate: Dict) -> str:
        """评估风险等级"""
        scores = candidate.get('scores', {})
        
        # 连板越多，风险越高
        limit_up_score = scores.get('涨停板', 0)
        if limit_up_score >= 30:
            return "🔴 高风险"
        elif limit_up_score >= 20:
            return "🟡 中风险"
        else:
            return "🟢 低风险"
    
    def format_signals_report(self, signals: List[Dict]) -> str:
        """格式化信号报告"""
        if not signals:
            return "今日暂无明确交易信号"
        
        lines = []
        lines.append("# 🎯 交易信号")
        lines.append(f"## {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("| 股票 | 代码 | 评分 | 現价 | 涨跌幅 | 信号 | 建议仓位 | 风险 |")
        lines.append("|------|------|------|------|--------|------|--------|------|")
        
        for s in signals:
            lines.append(
                f"| **{s['name']}** | {s['code']} | {s['score']} | "
                f"{s['price']:.2f} | {s['change']:+.2f}% | {s['action']} | "
                f"{s['position_size']*100:.0f}% | {s['risk_level']} |"
            )
        
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("⚠️ 风险提示：以上仅为信号参考，不构成投资建议")
        
        return "\n".join(lines)


def test():
    """测试"""
    signals = TradingSignals()
    
    # 模拟数据
    candidates = [
        {'code': '002361', 'name': '神剑股份', 'score': 50, 'price': 10.0, 'change': 10.0,
         'scores': {'涨停板': 35}},
        {'code': '000592', 'name': '平潭发展', 'score': 45, 'price': 5.0, 'change': 9.9,
         'scores': {'涨停板': 28}},
    ]
    
    market_data = {'sentiment': 'neutral'}
    
    result = signals.generate_signals(candidates, market_data)
    report = signals.format_signals_report(result)
    print(report)


if __name__ == "__main__":
    test()
