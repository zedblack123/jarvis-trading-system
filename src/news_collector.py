"""
新闻采集器
多源财经新闻采集
"""
import re
import json
import requests
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup


class NewsCollector:
    """多源新闻采集器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        self.cache = {}
        self.cache_valid_minutes = 15
    
    def _is_cache_valid(self, key: str) -> bool:
        if key not in self.cache:
            return False
        elapsed = (datetime.now() - self.cache[key]['time']).total_seconds()
        return elapsed < self.cache_valid_minutes * 60
    
    def _set_cache(self, key: str, data: List[Dict]):
        self.cache[key] = {'data': data, 'time': datetime.now()}
    
    # ==================== 同花顺 ====================
    
    def get_tonghuashun_news(self) -> List[Dict]:
        """同花顺财经新闻"""
        cache_key = 'tonghuashun'
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        news_list = []
        try:
            url = 'https://news.10jqka.com.cn/tapp/news/push/stock/'
            params = {'page': 1, 'tag': '', 'track': 'website', 'pagesize': 20}
            
            resp = self.session.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get('data', {}).get('list', [])
                
                for item in items:
                    news_list.append({
                        'source': '同花顺',
                        'title': item.get('title', ''),
                        'time': datetime.fromtimestamp(int(item.get('ctime', 0))).strftime('%H:%M'),
                        'url': item.get('url', ''),
                        'impact': self._estimate_impact(item.get('title', ''))
                    })
        except Exception as e:
            print(f"同花顺新闻获取失败: {e}")
        
        self._set_cache(cache_key, news_list)
        return news_list
    
    # ==================== CNBC ====================
    
    def get_cnbc_news(self) -> List[Dict]:
        """CNBC美国财经新闻"""
        cache_key = 'cnbc'
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        news_list = []
        try:
            url = 'https://www.cnbc.com/id/100003114/device/rss/rss.html'
            resp = self.session.get(url, timeout=10)
            
            if resp.status_code == 200:
                items = re.findall(r'<item>(.*?)</item>', resp.text, re.DOTALL)
                
                for item in items[:10]:
                    title = re.search(r'<title>(.*?)</title>', item)
                    link = re.search(r'<link>(.*?)</link>', item)
                    
                    if title and title.group(1) != 'US Top News and Analysis':
                        news_list.append({
                            'source': 'CNBC',
                            'title': title.group(1).strip(),
                            'time': datetime.now().strftime('%H:%M'),
                            'url': link.group(1).strip() if link else '',
                            'impact': self._estimate_impact(title.group(1))
                        })
        except Exception as e:
            print(f"CNBC新闻获取失败: {e}")
        
        self._set_cache(cache_key, news_list)
        return news_list
    
    # ==================== BBC World ====================
    
    def get_bbc_news(self) -> List[Dict]:
        """BBC国际新闻"""
        cache_key = 'bbc'
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        news_list = []
        try:
            url = 'https://feeds.bbci.co.uk/news/world/rss.xml'
            resp = self.session.get(url, timeout=10)
            
            if resp.status_code == 200:
                titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', resp.text)
                
                for title in titles[2:12]:  # 跳过前两个(BBC News和标题)
                    if len(title) > 10:
                        news_list.append({
                            'source': 'BBC',
                            'title': title,
                            'time': datetime.now().strftime('%H:%M'),
                            'url': '',
                            'impact': self._estimate_impact(title)
                        })
        except Exception as e:
            print(f"BBC新闻获取失败: {e}")
        
        self._set_cache(cache_key, news_list)
        return news_list
    
    # ==================== Google News ====================
    
    def get_google_news(self) -> List[Dict]:
        """Google News中国新闻"""
        cache_key = 'google_news'
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        news_list = []
        try:
            url = 'https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans'
            resp = self.session.get(url, timeout=10)
            
            if resp.status_code == 200:
                items = re.findall(r'<item>(.*?)</item>', resp.text, re.DOTALL)
                
                for item in items[:15]:
                    title = re.search(r'<title>(.*?)</title>', item)
                    link = re.search(r'<link>(.*?)</link>', item)
                    
                    if title:
                        t = title.group(1).replace('<![CDATA[', '').replace(']]>', '')
                        if 'Google 新闻' not in t and len(t) > 10:
                            news_list.append({
                                'source': 'Google News',
                                'title': t,
                                'time': datetime.now().strftime('%H:%M'),
                                'url': link.group(1) if link else '',
                                'impact': self._estimate_impact(t)
                            })
        except Exception as e:
            print(f"Google新闻获取失败: {e}")
        
        self._set_cache(cache_key, news_list)
        return news_list
    
    # ==================== 工具方法 ====================
    
    def _estimate_impact(self, text: str) -> str:
        """判断新闻影响方向"""
        text_lower = text.lower()
        
        bullish_keywords = ['涨', '涨超', '大涨', '利好', '突破', '增长', '新高', '反弹', '拉升', '买入', '看好',
                          'surge', 'rise', 'gain', 'bullish', 'rally', '上涨']
        bearish_keywords = ['跌', '跌超', '大跌', '利空', '下降', '新低', '跳水', '抛售', '看空', '下跌',
                          'fall', 'drop', 'crash', 'bearish', 'plunge', '暴跌']
        
        bullish_count = sum(1 for k in bullish_keywords if k in text_lower)
        bearish_count = sum(1 for k in bearish_keywords if k in text_lower)
        
        if bullish_count > bearish_count:
            return 'bullish'
        elif bearish_count > bullish_count:
            return 'bearish'
        return 'neutral'
    
    def get_all_news(self) -> List[Dict]:
        """获取所有新闻"""
        all_news = []
        
        print("📰 采集国内新闻...")
        all_news.extend(self.get_tonghuashun_news())
        all_news.extend(self.get_google_news())
        
        print("🌍 采集国际新闻...")
        all_news.extend(self.get_cnbc_news())
        all_news.extend(self.get_bbc_news())
        
        # 按影响排序
        impact_order = {'bearish': 0, 'bullish': 1, 'neutral': 2}
        all_news.sort(key=lambda x: impact_order.get(x.get('impact', 'neutral'), 2))
        
        return all_news
    
    def format_report(self, news_list: List[Dict], title: str = "📰 财经新闻汇总") -> str:
        """格式化新闻报告"""
        now = datetime.now().strftime('%Y年%m月%d日 %H:%M')
        
        lines = []
        lines.append(f"{title}")
        lines.append(f"📅 {now}")
        lines.append("="*50)
        lines.append("")
        
        # 按来源分组
        by_source = {}
        for n in news_list:
            src = n.get('source', '其他')
            if src not in by_source:
                by_source[src] = []
            by_source[src].append(n)
        
        for source, items in by_source.items():
            lines.append(f"【{source}】")
            for item in items[:5]:
                impact_icon = {
                    'bullish': '🟢',
                    'bearish': '🔴',
                    'neutral': '🟡'
                }.get(item.get('impact', 'neutral'), '•')
                lines.append(f"{impact_icon} {item.get('title', '')[:60]}")
            lines.append("")
        
        lines.append("="*50)
        lines.append(f"📊 共 {len(news_list)} 条新闻")
        
        return "\n".join(lines)


def test():
    """测试新闻采集器"""
    print("="*60)
    print("📰 测试新闻采集器")
    print("="*60)
    
    collector = NewsCollector()
    news = collector.get_all_news()
    
    print(f"\n共采集到 {len(news)} 条新闻")
    
    report = collector.format_report(news)
    print("\n" + report)


if __name__ == "__main__":
    test()
