"""
分析追踪模块
记录Agent性能数据
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from datetime import datetime
import time
import json


@dataclass
class AgentMetrics:
    """Agent性能指标"""
    name: str
    calls: int = 0
    errors: int = 0
    total_latency: float = 0.0
    last_call_time: Optional[str] = None
    avg_latency: float = 0.0
    error_rate: float = 0.0
    
    def record_call(self, latency: float, error: bool = False):
        """记录调用"""
        self.calls += 1
        self.total_latency += latency
        
        if error:
            self.errors += 1
        
        self.last_call_time = datetime.now().isoformat()
        self.avg_latency = self.total_latency / self.calls if self.calls > 0 else 0
        self.error_rate = self.errors / self.calls if self.calls > 0 else 0
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


class Analytics:
    """分析追踪器"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._metrics: Dict[str, AgentMetrics] = {}
            self._initialized = True
    
    def record(self, agent_name: str, latency: float, error: bool = False) -> None:
        """记录Agent调用"""
        if agent_name not in self._metrics:
            self._metrics[agent_name] = AgentMetrics(name=agent_name)
        
        self._metrics[agent_name].record_call(latency, error)
    
    def get_metrics(self, agent_name: str = None) -> Optional[AgentMetrics]:
        """获取指标"""
        if agent_name:
            return self._metrics.get(agent_name)
        return None
    
    def get_all_metrics(self) -> Dict[str, AgentMetrics]:
        """获取所有指标"""
        return self._metrics
    
    def get_report(self) -> str:
        """生成报告"""
        if not self._metrics:
            return "📊 暂无分析数据"
        
        report_lines = ["📊 贾维斯分析报告", "=" * 40]
        
        total_calls = sum(m.calls for m in self._metrics.values())
        total_errors = sum(m.errors for m in self._metrics.values())
        total_latency = sum(m.total_latency for m in self._metrics.values())
        
        report_lines.append(f"📈 总体统计:")
        report_lines.append(f"  • 总调用次数: {total_calls}")
        report_lines.append(f"  • 总错误次数: {total_errors}")
        report_lines.append(f"  • 总错误率: {(total_errors/total_calls*100):.1f}%" if total_calls > 0 else "  • 总错误率: 0.0%")
        report_lines.append(f"  • 平均延迟: {(total_latency/total_calls):.2f}s" if total_calls > 0 else "  • 平均延迟: 0.00s")
        
        report_lines.append("\n🤖 Agent性能排名:")
        
        # 按调用次数排序
        sorted_agents = sorted(
            self._metrics.values(),
            key=lambda x: x.calls,
            reverse=True
        )
        
        for i, agent in enumerate(sorted_agents, 1):
            report_lines.append(f"  {i}. {agent.name}:")
            report_lines.append(f"     • 调用次数: {agent.calls}")
            report_lines.append(f"     • 错误次数: {agent.errors}")
            report_lines.append(f"     • 错误率: {agent.error_rate*100:.1f}%")
            report_lines.append(f"     • 平均延迟: {agent.avg_latency:.2f}s")
            report_lines.append(f"     • 最后调用: {agent.last_call_time or '从未调用'}")
        
        # 性能问题检测
        report_lines.append("\n⚠️ 性能问题检测:")
        
        problem_agents = []
        for agent in self._metrics.values():
            if agent.calls >= 10:  # 至少有10次调用才检测
                if agent.error_rate > 0.3:  # 错误率超过30%
                    problem_agents.append((agent.name, f"错误率过高: {agent.error_rate*100:.1f}%"))
                elif agent.avg_latency > 5.0:  # 平均延迟超过5秒
                    problem_agents.append((agent.name, f"延迟过高: {agent.avg_latency:.2f}s"))
        
        if problem_agents:
            for agent_name, problem in problem_agents:
                report_lines.append(f"  • {agent_name}: {problem}")
        else:
            report_lines.append("  ✅ 未检测到明显性能问题")
        
        report_lines.append("\n" + "=" * 40)
        report_lines.append("🤵 贾维斯分析系统 | 持续优化中")
        
        return "\n".join(report_lines)
    
    def save_to_file(self, filepath: str = None) -> str:
        """保存到文件"""
        if not filepath:
            import os
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"/root/.openclaw/workspace/data/analytics_{timestamp}.json"
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {name: agent.to_dict() for name, agent in self._metrics.items()}
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def load_from_file(self, filepath: str) -> bool:
        """从文件加载"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._metrics.clear()
            for name, metric_data in data.get('metrics', {}).items():
                self._metrics[name] = AgentMetrics(**metric_data)
            
            return True
        except Exception as e:
            print(f"❌ 加载分析数据失败: {str(e)}")
            return False
    
    def clear(self) -> None:
        """清空所有数据"""
        self._metrics.clear()
        print("🧹 已清空所有分析数据")


# ==================== 便捷函数 ====================

_analytics_instance = None

def get_analytics() -> Analytics:
    """获取分析器单例"""
    global _analytics_instance
    if _analytics_instance is None:
        _analytics_instance = Analytics()
    return _analytics_instance


# ==================== 装饰器 ====================

def track_agent_performance(agent_name: str = None):
    """
    追踪Agent性能的装饰器
    
    Args:
        agent_name: Agent名称，如果不提供则使用函数名
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            analytics = get_analytics()
            name = agent_name or func.__name__
            
            start_time = time.time()
            error = False
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error = True
                raise e
            finally:
                latency = time.time() - start_time
                analytics.record(name, latency, error)
        
        async def async_wrapper(*args, **kwargs):
            analytics = get_analytics()
            name = agent_name or func.__name__
            
            start_time = time.time()
            error = False
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error = True
                raise e
            finally:
                latency = time.time() - start_time
                analytics.record(name, latency, error)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper
    
    return decorator


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 测试分析系统
    analytics = get_analytics()
    
    # 记录一些测试数据
    analytics.record("fundamental_agent", 1.2)
    analytics.record("technical_agent", 0.8)
    analytics.record("sentiment_agent", 2.1, error=True)
    analytics.record("fundamental_agent", 1.5)
    analytics.record("risk_agent", 3.2)
    
    # 生成报告
    print(analytics.get_report())
    
    # 保存到文件
    filepath = analytics.save_to_file()
    print(f"\n💾 数据已保存到: {filepath}")