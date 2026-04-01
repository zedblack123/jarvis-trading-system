"""
报告生成器
生成每日投资报告
"""
import os
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import REPORTS_DIR
from src.data_manager import DataManager
from src.stock_screener import StockScreener
from src.news_collector import NewsCollector
from src.sentiment_monitor import SentimentMonitor
from src.trading_signals import TradingSignals


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        self.reports_dir = Path(REPORTS_DIR)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        self.dm = DataManager()
        self.screener = StockScreener()
        self.news_collector = NewsCollector()
        self.sentiment_monitor = SentimentMonitor()
        self.trading_signals = TradingSignals()
    
    def generate_morning_report(self) -> str:
        """生成早间报告"""
        print("\n📝 生成早间报告...")
        
        # 获取新闻
        news = self.news_collector.get_all_news()
        news_report = self.news_collector.format_report(news, "📰 多源财经新闻")
        
        # 获取选股
        candidates = self.screener.screen()
        screener_report = self.screener.format_report(candidates) if candidates else "今日暂无候选股"
        
        # 生成交易信号
        signals = self.trading_signals.generate_signals(candidates, {'sentiment': 'neutral'})
        signals_report = self.trading_signals.format_signals_report(signals)
        
        # 组合报告
        report = f"""# 🌅 A股早间投资策略
## {datetime.now().strftime('%Y年%m月%d日 08:00')}
================================================================================

{news_report}

---

{screener_report}

---

{signals_report}

================================================================================
*本报告由贾维斯自动生成*
*仅供参考，不构成投资建议*
"""        
        
        # 保存
        filename = f"早间报告_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        filepath = self.reports_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 早间报告已保存: {filepath}")
        
        return report
    
    def generate_hot_report(self) -> str:
        """生成热点推送"""
        print("\n📝 生成热点推送...")
        
        # 获取涨停股
        limit_up = self.dm.get_limit_up_stocks()
        sectors = self.dm.get_hot_sectors(10)
        
        # 获取舆情
        sentiment_result = self.sentiment_monitor.check()
        alert = self.sentiment_monitor.format_alert(sentiment_result)
        
        # 组合
        report = f"""# 🔥 A股热点速递
## {datetime.now().strftime('%Y年%m月%d日 09:25')}（集合竞价结束）
================================================================================

📈 涨停股
"""
        
        if limit_up is not None and len(limit_up) > 0:
            report += f"涨停总数: {len(limit_up)}只\n\n"
            report += "热门涨停:\n"
            for _, row in limit_up.head(5).iterrows():
                report += f"• {row.get('名称', '')}({row.get('代码', '')}) 第{int(row.get('连板数', 1))}板\n"
        else:
            report += "暂无数据\n"
        
        report += f"""
🏆 热门板块（按资金流）
"""
        
        for sector in sectors[:8]:
            report += f"• {sector}\n"
        
        if alert:
            report += f"""
{alert}
"""
        
        report += f"""
================================================================================
*数据来源: 东方财富/AKShare*
*仅供参考，不构成投资建议*
"""        
        
        # 保存
        filename = f"热点推送_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        filepath = self.reports_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 热点推送已保存: {filepath}")
        
        return report
    
    def generate_evening_report(self) -> str:
        """生成晚间报告"""
        print("\n📝 生成晚间报告...")
        
        # 获取市场数据
        index_quote = self.dm.get_index_quote("000001.SH")
        
        # 获取涨停股
        limit_up = self.dm.get_limit_up_stocks()
        
        # 获取新闻
        news = self.news_collector.get_all_news()
        
        report = f"""# 🌙 A股晚间总结
## {datetime.now().strftime('%Y年%m月%d日 22:00')}
================================================================================

📊 今日市场回顾
"""
        
        if index_quote is not None and len(index_quote) > 0:
            row = index_quote[0]
            report += f"""
上证指数: {row.get('最新价', 0):.2f}
涨跌: {row.get('涨跌幅', 0):+.2f}%
"""
        
        report += f"""
涨停家数: {len(limit_up) if limit_up is not None else 0}只

📰 重要新闻
"""
        
        # 只显示重大新闻
        for n in news[:5]:
            if n.get('impact') != 'neutral':
                report += f"• {n.get('title', '')[:50]}\n"
        
        report += f"""
🔮 明日展望
• 市场趋势: 震荡
• 操作建议: 控制仓位，逢低布局
• 风险提示: 严格止损

================================================================================
*本报告由贾维斯自动生成*
*仅供参考，不构成投资建议*
"""
        
        # 保存
        filename = f"晚间报告_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        filepath = self.reports_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 晚间报告已保存: {filepath}")
        
        return report


def test():
    """测试"""
    generator = ReportGenerator()
    # generator.generate_morning_report()


if __name__ == "__main__":
    test()
