# Jarvis Trading System 🤖

A股量化交易系统 - 贾维斯驱动 | 为人山先生服务

## 功能特性

- 📊 **实时行情** - 腾讯财经API，秒级获取
- 📈 **K线图** - Plotly交互式K线 + MACD/KDJ/RSI指标
- 🎯 **智能选股** - 多维度评分（涨停、技术、题材）
- 🔥 **热门选股看板** - 实时排名
- 📩 **飞书推送** - 实时消息推送
- 🤖 **多智能体分析** - DeepSeek + MiniMax 高低搭配
- 📈 **周期战法** - 板块轮动，低位潜伏策略

## 安装

### 基础依赖
```bash
pip install flask plotly akshare pandas numpy requests
```

### TradingAgents 集成（可选）
```bash
# 克隆 TradingAgents 仓库
git clone https://github.com/TauricResearch/TradingAgents.git trading_agents_external

# 安装 TradingAgents
cd trading_agents_external
pip install .
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
├── trading_strategies.py   # 策略层 (技术指标)
├── stock_screener.py       # 选股系统
└── integration/
    └── trading_agents_integration.py  # TradingAgents 多智能体集成
templates/
└── index.html     # 前端页面
```

## TradingAgents 多智能体集成

### 功能概述
TradingAgents 是一个多智能体交易框架，模拟真实交易公司的动态。通过部署专门的LLM驱动智能体：
- **分析师团队**：基本面分析师、情绪专家、技术分析师
- **研究员团队**：多头和空头研究员进行结构化辩论
- **交易员智能体**：基于全面市场洞察做出交易决策
- **风险管理与投资组合经理**：评估和调整交易策略

### 使用方法
```python
from src.integration import JarvisTradingAgentsIntegration

# 初始化集成
integration = JarvisTradingAgentsIntegration()
if integration.initialize():
    # 分析单只股票
    result = integration.wrapper.analyze_stock("AAPL", "苹果公司")
    print(f"决策: {result['decision_cn']}")
    
    # 批量分析
    stocks = [("AAPL", "苹果公司"), ("MSFT", "微软公司")]
    results = integration.wrapper.batch_analyze(stocks)
    
    # 生成报告
    report = integration.generate_report(results)
    print(report)
```

### 与选股系统集成
```python
from src.stock_screener import StockScreener
from src.integration import JarvisTradingAgentsIntegration

# 创建选股器
screener = StockScreener()

# 创建集成
integration = JarvisTradingAgentsIntegration()
integration.initialize()

# 获取增强的分析函数
enhanced_analyze = integration.integrate_with_screener(screener)

# 使用增强分析
stock_data = {"ticker": "AAPL", "company_name": "苹果公司"}
result = enhanced_analyze(stock_data)
print(f"综合决策: {result['combined_decision']}")
```

## 🤖 贾维斯多智能体系统 (DeepSeek + MiniMax)

### 模型分工

| 模型 | 角色 | 任务类型 |
|------|------|----------|
| **DeepSeek** | 主力分析师 | 选股、策略、推理、代码、风控 |
| **MiniMax** | 辅助助手 | 情绪分析、舆情监控、推送 |

### Agent 架构

```
┌─────────────────────────────────────────────────────────┐
│               JarvisMultiAgent 多智能体系统              │
├─────────────────────────────────────────────────────────┤
│  📊 基本面分析师 (DeepSeek)  │ 分析财务、估值、竞争力  │
│  📈 技术分析师 (DeepSeek)    │ 分析K线、指标、趋势     │
│  💬 情绪分析师 (MiniMax)     │ 分析舆情、市场情绪     │
│  ⚠️ 风控经理 (DeepSeek)      │ 评估风险、仓位建议     │
│  🎯 交易决策 (DeepSeek)      │ 综合决策、买卖建议     │
└─────────────────────────────────────────────────────────┘
```

### 使用方法

```python
from src.multi_agent import JarvisMultiAgent

# 初始化（需要配置 API Key）
agent = JarvisMultiAgent(
    deepseek_key="your-deepseek-key",
    minimax_key="your-minimax-key"
)

# 综合分析一只股票
result = agent.analyze_stock("002202", "金风科技")

# 格式化输出报告
print(agent.format_report(result))
```

### 快速选股

```python
from src.multi_agent import quick_screen

# 快速分析
result = quick_screen("002202")
print(result)
```

### API Key 配置

在 `/root/.openclaw/workspace/.env` 中配置：

```bash
DEEPSEEK_API_KEY=your-deepseek-api-key
MINIMAX_API_KEY=your-minimax-api-key
```

## 免责声明

本系统仅供学习研究，不构成投资建议。股市有风险，投资需谨慎。

*Sir, I am at your service.* 🤵
