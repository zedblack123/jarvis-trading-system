# Jarvis Trading System 🤖

A股量化交易系统 - 贾维斯驱动 | 为人山先生服务

## 功能特性

- 📊 **实时行情** - 腾讯财经API，秒级获取个股/指数
- 🎯 **智能选股** - 多维度评分（涨停、资金流、技术面、题材）
- 📰 **多源新闻** - 同花顺、CNBC、BBC、Google News
- 🔥 **舆情监控** - 热门关键字实时监控
- 🤖 **策略分析** - MACD/KDJ/布林带组合策略
- 📈 **DeepSeek分析** - AI驱动的深度市场分析
- 📩 **飞书推送** - 微信/飞书实时推送

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 查看市场概况
python main.py --mode hot

# 分析个股
python main.py --mode analyze --code 002202

# 生成每日报告
python main.py --mode report
```

## 策略说明

### 技术指标策略
- **MACD** - 趋势跟踪，金叉买入/死叉卖出
- **KDJ** - 超买超卖，J值>100卖出/J值<10买入
- **布林带** - 均值回归，触及上轨卖出/触及下轨买入
- **组合策略** - 综合多指标信号

### 选股策略
1. 涨停板因子 - 昨日涨停优先
2. 资金流因子 - 主力净流入
3. 技术面因子 - 均线多头排列
4. 题材因子 - 热点概念匹配

## 项目结构

```
jarvis-trading-system/
├── src/
│   ├── data_manager.py       # 数据管理 (实时API)
│   ├── stock_screener.py     # 选股系统
│   ├── news_collector.py     # 新闻采集
│   ├── sentiment_monitor.py  # 舆情监控
│   ├── trading_strategies.py # 技术指标策略
│   └── trading_signals.py    # 交易信号
├── config/
│   └── settings.py           # 配置
├── main.py                  # 入口
└── requirements.txt
```

## 数据源

| 数据 | 来源 |
|------|------|
| 实时行情 | 腾讯财经API |
| K线数据 | AKShare/Tushare |
| 涨停股 | 东方财富 |
| 新闻 | 同花顺/CNBC/BBC/Google |
| AI分析 | DeepSeek |

## 免责声明

本系统仅供学习和研究使用，不构成投资建议。股市有风险，投资需谨慎。

---

*Sir, I am at your service.* 🤵
