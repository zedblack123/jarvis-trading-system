"""
配置文件
"""
import os

# ==================== 路径配置 ====================
WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(WORKSPACE, "data")
REPORTS_DIR = os.path.join(WORKSPACE, "reports")
CACHE_DIR = os.path.join(DATA_DIR, "cache")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# ==================== 飞书配置 ====================
FEISHU_USER_OPEN_ID = "ou_636754d2a4956be2f5928918767a62e7"  # 人山先生
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")

# ==================== DeepSeek配置 ====================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# ==================== Tushare配置 ====================
TUSHARE_TOKEN = os.getenv("TUSHARE_TOKEN", "")
TUSHARE_API_URL = "http://api.tushare.pro"

# ==================== 数据源配置 ====================
DATA_SOURCE = "tushare"  # tushare 或 akshare
CACHE_EXPIRY_MINUTES = 30

# ==================== 选股参数 ====================
SCREENER_CONFIG = {
    # 涨停板因子权重
    "limit_up_weight": 40,
    # 资金流因子权重
    "money_flow_weight": 20,
    # 技术面因子权重
    "technical_weight": 25,
    # 基本面因子权重
    "fundamental_weight": 10,
    # 题材因子权重
    "concept_weight": 15,
    # 最低评分门槛
    "min_score": 40,
    # 最大候选数量
    "max_candidates": 20,
}

# ==================== 风控参数 ====================
RISK_CONTROL = {
    # 单票最大仓位
    "max_single_position": 0.20,  # 20%
    # 总仓位上限
    "max_total_position": 0.60,   # 60%
    # 止损线
    "stop_loss": -0.08,           # -8%
    # 止盈线
    "take_profit": 0.15,          # 15%
}

# ==================== 舆情监控配置 ====================
SENTIMENT_CONFIG = {
    # 热门关键字
    "hot_keywords": [
        "涨停", "跌停", "暴涨", "暴跌", "闪崩", "停牌", "复牌",
        "龙头", "妖股", "牛股", "白马", "降准", "加息",
        "印花税", "证监会", "央行", "财政部", "美联储",
        "非农", "CPI", "战争", "制裁", "新能源", "半导体",
        "人工智能", "芯片", "医药集采", "黑天鹅", "利好", "利好",
        "业绩暴增", "业绩暴雷", "崩盘", "股灾",
        "合约暴跌", "合约大涨", "期货暴跌", "期货涨停",
        "原油暴跌", "原油大涨", "黄金暴跌", "黄金大涨",
        "上期所", "大商所", "郑商所",
    ],
    # 恐慌关键字
    "panic_keywords": [
        "崩盘", "股灾", "清仓", "踩踏", "做空", "爆仓",
        "外资出逃", "主力砸盘", "大规模减持",
        "暴跌", "闪崩", "跌停",
    ],
    # 检查间隔（秒）
    "check_interval": 600,  # 10分钟
}

# ==================== 新闻源配置 ====================
NEWS_SOURCES = {
    "tonghuashun": {
        "enabled": True,
        "url": "https://news.10jqka.com.cn/tapp/news/push/stock/",
        "params": {"page": 1, "tag": "", "track": "website", "pagesize": 20},
    },
    "cnbc": {
        "enabled": True,
        "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    },
    "bbc": {
        "enabled": True,
        "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
    },
    "google_news": {
        "enabled": True,
        "url": "https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
    },
}

# ==================== 推送时间 ====================
PUSH_SCHEDULE = {
    "morning_report": "08:00",      # 早间报告
    "hot_push": "09:25",            # 集合竞价热点
    "sentiment_check": "09:30-15:00",  # 舆情监控时段
    "evening_report": "22:00",      # 晚间报告
}
