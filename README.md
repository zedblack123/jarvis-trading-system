# Jarvis Trading System 🤖

A股量化交易系统 - 贾维斯驱动 | 为人山先生服务

## 功能特性

- 📊 **实时行情** - 腾讯财经API，秒级获取
- 📈 **K线图** - Plotly交互式K线 + MACD/KDJ/RSI指标
- 🎯 **智能选股** - 多维度评分（涨停、技术、题材）
- 🔥 **热门选股看板** - 实时排名
- 📩 **飞书推送** - 实时消息推送

## 安装

```bash
pip install flask plotly akshare pandas numpy requests
```

## 启动Web界面

```bash
python src/dashboard.py
```

然后打开浏览器访问: http://localhost:5000

## 启动命令行版本

```bash
python main.py --mode report     # 每日报告
python main.py --mode analyze --code 002202  # 分析个股
python main.py --mode screen      # 选股
python main.py --mode hot        # 热门涨停
```

## Web界面功能

- 📊 大盘指数实时行情
- 📈 个股K线图 + 技术指标
- 🔥 热门选股TOP10
- 📝 股票搜索与分析

## 架构

```
src/
├── dashboard.py     # Flask Web界面
├── data_manager.py # 数据层 (实时/K线/板块)
└── strategies.py   # 策略层 (技术指标)
templates/
└── index.html     # 前端页面
```

## 免责声明

本系统仅供学习研究，不构成投资建议。股市有风险，投资需谨慎。

*Sir, I am at your service.* 🤵
