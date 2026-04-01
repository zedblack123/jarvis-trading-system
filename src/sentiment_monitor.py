"""
舆情监控系统
热门关键字实时监控
"""
import time
from datetime import datetime
from typing import List, Dict, Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import SENTIMENT_CONFIG
from src.news_collector import NewsCollector


class SentimentMonitor:
    """舆情监控"""
    
    def __init__(self):
        self.news_collector = NewsCollector()
        self.config = SENTIMENT_CONFIG
        self.hot_keywords = self.config['hot_keywords']
        self.panic_keywords = self.config['panic_keywords']
    
    def check(self) -> Dict:
        """
        检查舆情
        返回: {hot_items, panic_items, all_news}
        """
        all_news = self.news_collector.get_all_news()
        
        hot_items = []
        panic_items = []
        
        for news in all_news:
            title = news.get('title', '').lower()
            
            # 检查热门关键字
            for kw in self.hot_keywords:
                if kw.lower() in title:
                    hot_items.append(news)
                    break
            
            # 检查恐慌关键字
            for kw in self.panic_keywords:
                if kw.lower() in title:
                    panic_items.append(news)
                    break
        
        return {
            'hot_items': hot_items,
            'panic_items': panic_items,
            'all_news': all_news,
            'timestamp': datetime.now()
        }
    
    def should_push(self, result: Dict) -> bool:
        """判断是否需要推送"""
        return len(result['hot_items']) > 0 or len(result['panic_items']) > 0
    
    def format_alert(self, result: Dict) -> str:
        """格式化预警消息"""
        if not self.should_push(result):
            return None
        
        hot_items = result['hot_items']
        panic_items = result['panic_items']
        all_news = result['all_news']
        timestamp = result['timestamp']
        
        # 判断级别
        if panic_items:
            level = "🔴 恐慌舆情预警"
        elif len(hot_items) >= 5:
            level = "🟠 高度活跃"
        elif len(hot_items) >= 3:
            level = "🟡 热门动态"
        else:
            level = "🟢 热门线索"
        
        lines = []
        lines.append(f"{level}")
        lines.append(f"📅 {timestamp.strftime('%Y年%m月%d日 %H:%M')}")
        lines.append("━"*50)
        
        # 恐慌预警
        if panic_items:
            lines.append("\n⚠️ 恐慌/异常预警:")
            for item in panic_items[:3]:
                lines.append(f"🔴 {item.get('title', '')[:50]}")
                lines.append(f"   来源:{item.get('source', '')} | {item.get('time', '')}")
        
        # 热门舆情
        if hot_items:
            lines.append(f"\n🔥 热门关键字 ({len(hot_items)}条):")
            for item in hot_items[:8]:
                impact_icon = {
                    'bullish': '🟢',
                    'bearish': '🔴',
                    'neutral': '🟡'
                }.get(item.get('impact', 'neutral'), '•')
                lines.append(f"{impact_icon} {item.get('title', '')[:50]}")
                lines.append(f"   {item.get('source', '')} | {item.get('time', '')}")
        
        # 统计
        bullish = sum(1 for n in all_news if n.get('impact') == 'bullish')
        bearish = sum(1 for n in all_news if n.get('impact') == 'bearish')
        
        lines.append("\n" + "━"*50)
        lines.append(f"📊 舆情概览: 共{len(all_news)}条 | 🟢{bullish}利好 🔴{bearish}利空")
        lines.append(f"⏰ 检测时间: {timestamp.strftime('%H:%M:%S')}")
        
        return "\n".join(lines)
    
    def run_once(self) -> Optional[str]:
        """运行一次检查"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 检查热门舆情...")
        
        result = self.check()
        print(f"   总新闻: {len(result['all_news'])} | 热门: {len(result['hot_items'])} | 恐慌: {len(result['panic_items'])}")
        
        if self.should_push(result):
            return self.format_alert(result)
        
        print("   ⏭️ 无热门舆情，跳过")
        return None
    
    def run_continuous(self, interval: int = None):
        """持续运行监控"""
        if interval is None:
            interval = self.config['check_interval']
        
        print(f"\n{'='*50}")
        print(f"🔥 舆情监控已启动 (间隔{interval}秒)")
        print(f"{'='*50}")
        
        while True:
            alert = self.run_once()
            if alert:
                print("\n📤 准备推送...")
                print(alert)
            
            time.sleep(interval)
            
            # 只在交易时间检查
            now = datetime.now()
            if now.weekday() >= 5:  # 周末
                continue
            if now.hour < 9 or now.hour >= 15:
                continue


def test():
    """测试舆情监控"""
    monitor = SentimentMonitor()
    alert = monitor.run_once()
    
    if alert:
        print("\n" + alert)


if __name__ == "__main__":
    test()
