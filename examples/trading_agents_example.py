#!/usr/bin/env python3
"""
TradingAgents 集成使用示例
展示如何将 TradingAgents 多智能体框架整合到贾维斯量化系统
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.integration import JarvisTradingAgentsIntegration, TRADING_AGENTS_AVAILABLE


def main():
    """主函数：演示 TradingAgents 集成功能"""
    
    print("=" * 60)
    print("TradingAgents 集成示例")
    print("=" * 60)
    
    # 检查 TradingAgents 是否可用
    if not TRADING_AGENTS_AVAILABLE:
        print("❌ TradingAgents 不可用")
        print("请先安装 TradingAgents:")
        print("1. git clone https://github.com/TauricResearch/TradingAgents.git")
        print("2. cd TradingAgents && pip install .")
        return
    
    print("✅ TradingAgents 可用")
    
    # 初始化集成
    print("\n1. 初始化 TradingAgents 集成...")
    integration = JarvisTradingAgentsIntegration()
    
    if not integration.initialize():
        print("❌ 集成初始化失败")
        return
    
    print("✅ 集成初始化成功")
    
    # 示例股票列表
    test_stocks = [
        ("AAPL", "苹果公司"),
        ("MSFT", "微软公司"),
        ("GOOGL", "谷歌公司"),
        ("AMZN", "亚马逊公司"),
        ("TSLA", "特斯拉公司")
    ]
    
    print(f"\n2. 分析 {len(test_stocks)} 只示例股票...")
    
    # 批量分析
    results = integration.wrapper.batch_analyze(test_stocks)
    
    # 显示结果
    print("\n3. 分析结果:")
    print("-" * 60)
    
    success_count = 0
    for result in results:
        ticker = result.get("ticker", "未知")
        company = result.get("company_name", "未知公司")
        
        if "error" in result:
            print(f"❌ {ticker} ({company}): 分析失败 - {result['error']}")
        else:
            success_count += 1
            decision = result.get("decision_cn", "未知")
            confidence = result.get("confidence", "未知")
            print(f"✅ {ticker} ({company}): {decision} (置信度: {confidence})")
    
    print(f"\n✅ 成功分析: {success_count}/{len(test_stocks)}")
    
    # 生成报告
    print("\n4. 生成分析报告...")
    report = integration.generate_report(results)
    
    # 保存报告
    report_dir = "./reports"
    os.makedirs(report_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(report_dir, f"trading_agents_report_{timestamp}.md")
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"✅ 报告已保存到: {report_file}")
    
    # 显示报告摘要
    print("\n5. 报告摘要:")
    print("-" * 60)
    report_lines = report.split("\n")
    for line in report_lines[:15]:  # 显示前15行
        print(line)
    
    if len(report_lines) > 15:
        print("... (完整报告请查看文件)")
    
    print("\n" + "=" * 60)
    print("示例完成！")
    print("=" * 60)


def demonstrate_integration_with_screener():
    """演示与选股系统的集成"""
    print("\n" + "=" * 60)
    print("演示：与选股系统集成")
    print("=" * 60)
    
    if not TRADING_AGENTS_AVAILABLE:
        print("TradingAgents 不可用，跳过集成演示")
        return
    
    try:
        # 导入选股系统
        from src.stock_screener import StockScreener
        
        # 创建选股器
        screener = StockScreener()
        print("✅ 选股系统创建成功")
        
        # 创建集成
        integration = JarvisTradingAgentsIntegration()
        if not integration.initialize():
            print("❌ 集成初始化失败")
            return
        
        print("✅ TradingAgents 集成初始化成功")
        
        # 获取增强的分析函数
        enhanced_analyze = integration.integrate_with_screener(screener)
        print("✅ 增强分析函数创建成功")
        
        # 测试增强分析
        print("\n测试增强分析...")
        test_stock = {
            "ticker": "AAPL",
            "company_name": "苹果公司",
            "price": 175.50,
            "change_percent": 1.5,
            "volume": 50000000
        }
        
        print(f"分析股票: {test_stock['ticker']} ({test_stock['company_name']})")
        result = enhanced_analyze(test_stock)
        
        print(f"\n分析结果:")
        print(f"- 基础决策: {result.get('decision', '未知')}")
        print(f"- TradingAgents决策: {result.get('trading_agents_analysis', {}).get('decision_cn', '未知')}")
        print(f"- 综合决策: {result.get('combined_decision', '未知')}")
        
        if "trading_agents_error" in result:
            print(f"- TradingAgents错误: {result['trading_agents_error']}")
        
        print("\n✅ 集成演示完成")
        
    except ImportError as e:
        print(f"❌ 无法导入选股系统: {e}")
    except Exception as e:
        print(f"❌ 集成演示失败: {e}")


if __name__ == "__main__":
    main()
    demonstrate_integration_with_screener()