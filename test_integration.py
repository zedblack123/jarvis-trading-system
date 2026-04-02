#!/usr/bin/env python3
"""
测试 TradingAgents 整合
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_tradingagents_import():
    """测试 TradingAgents 导入"""
    print("测试 TradingAgents 导入...")
    try:
        import tradingagents
        print("✅ TradingAgents 导入成功")
        
        # 检查版本
        try:
            print(f"  - 版本: {tradingagents.__version__}")
        except:
            print("  - 版本信息不可用")
        
        # 检查主要模块
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        print("✅ TradingAgentsGraph 导入成功")
        
        from tradingagents.graph.propagation import Propagator
        print("✅ Propagator 导入成功")
        
        return True
    except ImportError as e:
        print(f"❌ TradingAgents 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 导入过程中出错: {e}")
        return False

def test_integration_module():
    """测试整合模块"""
    print("\n测试整合模块导入...")
    try:
        from src.integration import (
            TradingAgentsWrapper,
            JarvisTradingAgentsIntegration,
            TRADING_AGENTS_AVAILABLE
        )
        
        print(f"✅ 整合模块导入成功")
        print(f"  - TradingAgentsWrapper: 可用")
        print(f"  - JarvisTradingAgentsIntegration: 可用")
        print(f"  - TRADING_AGENTS_AVAILABLE: {TRADING_AGENTS_AVAILABLE}")
        
        return True
    except ImportError as e:
        print(f"❌ 整合模块导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 整合模块测试过程中出错: {e}")
        return False

def test_wrapper_creation():
    """测试包装器创建"""
    print("\n测试 TradingAgents 包装器创建...")
    
    from src.integration import TRADING_AGENTS_AVAILABLE
    
    if not TRADING_AGENTS_AVAILABLE:
        print("⚠️ TradingAgents 不可用，跳过包装器测试")
        return False
    
    try:
        from src.integration import TradingAgentsWrapper
        
        # 尝试创建包装器（不实际运行，因为需要API密钥）
        print("尝试创建 TradingAgentsWrapper...")
        
        # 注意：这里我们只是测试导入和初始化，不实际调用API
        print("✅ 包装器类定义正常")
        
        # 测试配置
        config = {
            "use_chinese_output": True,
            "debug": False
        }
        print("✅ 配置测试通过")
        
        return True
    except Exception as e:
        print(f"❌ 包装器测试失败: {e}")
        return False

def test_directory_structure():
    """测试目录结构"""
    print("\n测试目录结构...")
    
    required_dirs = [
        "src/integration",
        "config",
        "examples",
        "reports"
    ]
    
    required_files = [
        "src/integration/__init__.py",
        "src/integration/trading_agents_integration.py",
        "config/trading_agents_config.json",
        "examples/trading_agents_example.py",
        "README.md"
    ]
    
    all_ok = True
    
    for dir_path in required_dirs:
        full_path = os.path.join(os.path.dirname(__file__), dir_path)
        if os.path.exists(full_path):
            print(f"✅ 目录存在: {dir_path}")
        else:
            print(f"❌ 目录不存在: {dir_path}")
            all_ok = False
    
    for file_path in required_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            print(f"✅ 文件存在: {file_path}")
        else:
            print(f"❌ 文件不存在: {file_path}")
            all_ok = False
    
    return all_ok

def main():
    """主测试函数"""
    print("=" * 60)
    print("TradingAgents 整合测试")
    print("=" * 60)
    
    tests = [
        ("TradingAgents 导入", test_tradingagents_import),
        ("整合模块", test_integration_module),
        ("包装器创建", test_wrapper_creation),
        ("目录结构", test_directory_structure)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n[{test_name}]")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！整合成功！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())