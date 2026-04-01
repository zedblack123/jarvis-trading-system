# Jarvis Trading System 🤖

A股量化交易系统 - 贾维斯驱动 | 为人山先生服务

## 功能特性

- 📊 **实时行情** - 腾讯财经API，秒级获取
- 🎯 **智能选股** - 多维度评分（涨停、技术、题材）
- 🤖 **技术分析** - MACD/KDJ/RSI/均线
- 🔥 **舆情监控** - 热门关键字实时监控
- 📈 **DeepSeek分析** - AI深度市场分析
- 📩 **飞书推送** - 实时消息推送

## 快速开始

```bash
# 安装依赖
pip install akshare pandas numpy requests

# 运行
python main.py --mode report     # 每日报告
python main.py --mode analyze --code 002202  # 分析个股
python main.py --mode screen      # 选股
python main.py --mode hot        # 热门涨停
```

## 架构

```
src/
├── data_manager.py    # 数据层 (实时/K线/板块)
└── strategies.py      # 策略引擎 (技术指标)
```

## 免责声明

本系统仅供学习研究，不构成投资建议。股市有风险，投资需谨慎。

*Sir, I am at your service.* 🤵
