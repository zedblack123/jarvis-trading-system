#!/usr/bin/env python3
"""
TradingAgents 整合演示
展示如何将 TradingAgents 多智能体框架整合到贾维斯量化系统
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_basic_integration():
    """演示基本整合功能"""
    print("=" * 70)
    print("TradingAgents 整合演示")
    print("=" * 70)
    
    print("\n1. 检查 TradingAgents 可用性...")
    from src.integration import TRADING_AGENTS_AVAILABLE
    
    if not TRADING_AGENTS_AVAILABLE:
        print("❌ TradingAgents 不可用")
        return False
    
    print("✅ TradingAgents 可用")
    
    print("\n2. 创建 TradingAgents 包装器...")
    try:
        from src.integration import TradingAgentsWrapper
        
        # 创建包装器（不实际运行，因为需要API密钥）
        wrapper = TradingAgentsWrapper(
            debug=False,
            use_chinese_output=True,
            llm_provider="openai",  # 需要设置相应的 API 密钥
            deep_think_llm="gpt-4",
            quick_think_llm="gpt-3.5-turbo"
        )
        
        print("✅ TradingAgentsWrapper 创建成功")
        print("   配置: 中文输出, OpenAI GPT-4/GPT-3.5")
        
    except Exception as e:
        print(f"❌ 包装器创建失败: {e}")
        print("   注意: 需要设置相应的 API 密钥才能实际运行")
        return False
    
    print("\n3. 演示分析功能（模拟）...")
    
    # 模拟分析结果
    mock_results = [
        {
            "ticker": "AAPL",
            "company_name": "苹果公司",
            "decision": "BUY",
            "decision_cn": "买入",
            "confidence": 0.85,
            "reasoning": "市场分析师: 苹果公司季度财报超预期...\n情绪专家: 社交媒体情绪积极...\n基本面分析师: 财务指标健康...",
            "timestamp": datetime.now().isoformat()
        },
        {
            "ticker": "MSFT",
            "company_name": "微软公司", 
            "decision": "HOLD",
            "decision_cn": "持有",
            "confidence": 0.65,
            "reasoning": "市场分析师: 微软云业务增长稳定...\n情绪专家: 市场情绪中性...\n基本面分析师: 估值合理...",
            "timestamp": datetime.now().isoformat()
        },
        {
            "ticker": "TSLA",
            "company_name": "特斯拉公司",
            "decision": "SELL", 
            "decision_cn": "卖出",
            "confidence": 0.72,
            "reasoning": "市场分析师: 竞争加剧影响市场份额...\n情绪专家: 社交媒体情绪偏负面...\n基本面分析师: 估值偏高...",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    print(f"模拟分析 {len(mock_results)} 只股票:")
    for result in mock_results:
        print(f"  - {result['ticker']} ({result['company_name']}): {result['decision_cn']} (置信度: {result['confidence']})")
    
    print("\n4. 演示报告生成...")
    from src.integration import JarvisTradingAgentsIntegration
    
    integration = JarvisTradingAgentsIntegration()
    report = integration.generate_report(mock_results)
    
    # 显示报告摘要
    print("生成的报告摘要:")
    print("-" * 50)
    report_lines = report.split("\n")
    for line in report_lines[:20]:  # 显示前20行
        print(line)
    
    print("\n5. 演示与选股系统集成...")
    try:
        # 模拟选股系统
        class MockScreener:
            def analyze_stock(self, stock_data):
                return {
                    "decision": "HOLD",
                    "score": 75,
                    "analysis": "基础技术分析结果"
                }
        
        screener = MockScreener()
        integration.initialize()  # 实际使用时需要初始化
        
        print("✅ 集成架构演示完成")
        print("   实际使用时，可以通过 integration.integrate_with_screener() 方法")
        print("   将 TradingAgents 多智能体分析整合到现有选股系统中")
        
    except Exception as e:
        print(f"⚠️ 集成演示部分出错: {e}")
    
    print("\n" + "=" * 70)
    print("演示完成！")
    print("=" * 70)
    
    return True


def demo_actual_usage():
    """演示实际使用方式"""
    print("\n" + "=" * 70)
    print("实际使用方式演示")
    print("=" * 70)
    
    print("\n1. 配置文件使用:")
    config_example = {
        "trading_agents_integration": {
            "enabled": True,
            "use_chinese_output": True,
            "llm_provider": "openai",
            "deep_think_llm": "gpt-4",
            "quick_think_llm": "gpt-3.5-turbo",
            "debug": False
        }
    }
    
    print(json.dumps(config_example, indent=2, ensure_ascii=False))
    
    print("\n2. 代码集成示例:")
    code_example = '''
# 方式1: 直接使用包装器
from src.integration import TradingAgentsWrapper

wrapper = TradingAgentsWrapper(
    use_chinese_output=True,
    llm_provider="openai",
    deep_think_llm="gpt-4",
    quick_think_llm="gpt-3.5-turbo"
)

# 分析单只股票
result = wrapper.analyze_stock("AAPL", "苹果公司")

# 批量分析
stocks = [("AAPL", "苹果公司"), ("MSFT", "微软公司")]
results = wrapper.batch_analyze(stocks)

# 方式2: 使用集成类
from src.integration import JarvisTradingAgentsIntegration

integration = JarvisTradingAgentsIntegration("config/trading_agents_config.json")
if integration.initialize():
    # 与现有选股系统集成
    from src.stock_screener import StockScreener
    screener = StockScreener()
    enhanced_analyze = integration.integrate_with_screener(screener)
    
    # 使用增强分析
    stock_data = {"ticker": "AAPL", "company_name": "苹果公司"}
    enhanced_result = enhanced_analyze(stock_data)
'''
    
    print(code_example)
    
    print("\n3. 输出示例:")
    output_example = '''
# TradingAgents 多智能体分析报告
生成时间: 2026-04-02 14:30:00
分析股票数量: 3

## 1. AAPL - 苹果公司
- **最终决策**: 买入
- **置信度**: 0.85
- **分析摘要**: 市场分析师: 苹果公司季度财报超预期，营收增长15%...
情绪专家: 社交媒体情绪积极，提及量增加25%...
基本面分析师: 财务指标健康，市盈率合理...

## 2. MSFT - 微软公司
- **最终决策**: 持有
- **置信度**: 0.65
- **分析摘要**: 市场分析师: 微软云业务增长稳定，Azure收入增长20%...
情绪专家: 市场情绪中性，无明显负面情绪...
基本面分析师: 估值合理，现金流稳定...

## 决策分布统计
- 买入: 1 只股票
- 持有: 1 只股票
- 卖出: 1 只股票
'''
    
    print(output_example)
    
    print("\n" + "=" * 70)
    print("实际使用方式演示完成")
    print("=" * 70)


def main():
    """主函数"""
    print("\n🎯 TradingAgents 多智能体交易框架整合演示")
    print("📊 将 TradingAgents 整合到贾维斯量化系统")
    print("🤖 多角色协同决策：市场分析师、情绪专家、基本面分析师等")
    
    # 演示基本整合
    if not demo_basic_integration():
        print("\n⚠️ 基本整合演示失败")
        return
    
    # 演示实际使用方式
    demo_actual_usage()
    
    print("\n✅ 整合演示全部完成！")
    print("\n📋 下一步:")
    print("1. 设置 API 密钥 (OpenAI/Anthropic/Google)")
    print("2. 修改 config/trading_agents_config.json 配置文件")
    print("3. 运行 examples/trading_agents_example.py 测试实际功能")
    print("4. 将集成应用到现有选股系统中")
    
    print("\n🔧 文件结构:")
    print("  src/integration/trading_agents_integration.py  # 核心整合模块")
    print("  config/trading_agents_config.json              # 配置文件")
    print("  examples/trading_agents_example.py             # 使用示例")
    print("  test_integration.py                            # 测试脚本")
    
    print("\n🚀 开始使用 TradingAgents 多智能体分析增强您的交易决策！")


if __name__ == "__main__":
    main()