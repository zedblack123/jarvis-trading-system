# Jarvis Trading System

A股量化交易系统 - 由贾维斯驱动

## 功能特性

- 📊 **智能选股** - 基于多维度评分（涨停、资金流、技术面、题材）
- 📰 **多源新闻** - 同花顺、CNBC、BBC、Google News
- 🔥 **舆情监控** - 实时热门关键字监控
- 🤖 **DeepSeek分析** - AI驱动的深度市场分析
- 📈 **回测框架** - 策略历史验证
- 📩 **飞书推送** - 微信/飞书实时推送报告

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

编辑 `config/settings.py`：

```python
# 飞书配置
FEISHU_USER_OPEN_ID = "your_open_id"

# DeepSeek API
DEEPSEEK_API_KEY = "your_api_key"

# Tushare Token (可选)
TUSHARE_TOKEN = "your_token"
```

### 3. 运行

```bash
# 每日早间报告
python main.py --mode morning

# 热点推送
python main.py --mode hot

# 舆情监控
python main.py --mode sentiment

# 完整一日流程
python main.py --mode daily

# 回测
python main.py --mode backtest --start 20260101 --end 20260331
```

## 项目结构

```
jarvis-trading-system/
├── src/
│   ├── __init__.py
│   ├── data_manager.py      # 数据管理
│   ├── stock_screener.py    # 选股系统
│   ├── news_collector.py   # 新闻采集
│   ├── sentiment_monitor.py # 舆情监控
│   ├── trading_signals.py  # 交易信号
│   ├── report_generator.py  # 报告生成
│   └── backtester.py       # 回测框架
├── config/
│   └── settings.py          # 配置
├── tests/
│   └── test_screener.py    # 测试
├── data/                   # 数据缓存
├── reports/                # 报告输出
├── main.py                 # 入口
└── requirements.txt        # 依赖
```

## 策略说明

### 选股策略

1. **涨停板因子** - 昨日涨停股优先
2. **资金流因子** - 主力净流入
3. **技术面因子** - 均线多头排列
4. **题材因子** - 热点概念匹配

### 风控原则

- 单票仓位 ≤ 20%
- 总仓位 ≤ 60%
- 止损线 -8%

## 免责声明

本系统仅供学习和研究使用，不构成投资建议。股市有风险，投资需谨慎。

## 作者

贾维斯 - 为人山先生服务 🤵
