"""
智能模型路由 - 简化版
使用装饰器方式自动选择模型
"""

import os
import requests
from typing import Dict, Optional, Callable
from enum import Enum
from functools import wraps

# 导入分析追踪
from analytics import get_analytics, track_agent_performance


class Model(Enum):
    """可用模型"""
    DEEPSEEK = "deepseek/deepseek-chat"
    MINIMAX = "minimax-portal/MiniMax-M2.7"


class TaskType(Enum):
    """任务类型"""
    # DeepSeek 擅长的推理任务
    STOCK_ANALYSIS = "stock_analysis"
    MARKET_RESEARCH = "market_research"
    STRATEGY_FORMULATE = "strategy"
    TRADING_SIGNALS = "trading_signals"
    PORTFOLIO_OPTIMIZE = "portfolio"
    RISK_ASSESSMENT = "risk"
    NEWS_ANALYSIS = "news_analysis"
    
    # MiniMax 擅长的简单任务
    SIMPLE_QUERY = "query"
    NEWS_PUSH = "push"
    TEXT_SUMMARY = "summary"
    GREETING = "greeting"
    SYSTEM_CMD = "system"


# 任务类型 -> 模型映射
TASK_MODEL_MAP = {
    TaskType.STOCK_ANALYSIS: Model.DEEPSEEK,
    TaskType.MARKET_RESEARCH: Model.DEEPSEEK,
    TaskType.STRATEGY_FORMULATE: Model.DEEPSEEK,
    TaskType.TRADING_SIGNALS: Model.DEEPSEEK,
    TaskType.PORTFOLIO_OPTIMIZE: Model.DEEPSEEK,
    TaskType.RISK_ASSESSMENT: Model.DEEPSEEK,
    TaskType.NEWS_ANALYSIS: Model.DEEPSEEK,
    
    TaskType.SIMPLE_QUERY: Model.MINIMAX,
    TaskType.NEWS_PUSH: Model.MINIMAX,
    TaskType.TEXT_SUMMARY: Model.MINIMAX,
    TaskType.GREETING: Model.MINIMAX,
    TaskType.SYSTEM_CMD: Model.MINIMAX,
}


class ModelRouter:
    """模型路由器 - 简化版"""
    
    def __init__(self):
        # DeepSeek配置
        self.deepseek_key = os.getenv('DEEPSEEK_API_KEY', '')
        if not self.deepseek_key:
            try:
                with open('/root/.openclaw/workspace/.deepseek_key', 'r') as f:
                    self.deepseek_key = f.read().strip()
            except:
                pass
        
        self.deepseek_url = "https://api.deepseek.com/v1/chat/completions"
        
        # MiniMax配置 - 使用OpenClaw内置
        self.minimax_available = True
        
        # 分析追踪
        self.analytics = get_analytics()
    
    def classify_task(self, text: str) -> TaskType:
        """根据文本内容自动识别任务类型"""
        text_lower = text.lower()
        
        # 特殊模式检测
        if any(word in text_lower for word in ['分析', '推荐', '预测']):
            return TaskType.STOCK_ANALYSIS
        elif any(word in text_lower for word in ['市场', '大盘', '走势']):
            return TaskType.MARKET_RESEARCH
        elif any(word in text_lower for word in ['策略', '操作', '建议']):
            return TaskType.STRATEGY_FORMULATE
        elif any(word in text_lower for word in ['新闻', '舆情', '消息']):
            return TaskType.NEWS_ANALYSIS
        elif any(word in text_lower for word in ['推送', '发送', '通知']):
            return TaskType.NEWS_PUSH
        elif any(word in text_lower for word in ['查询', '获取', '查看']):
            return TaskType.SIMPLE_QUERY
        elif any(word in text_lower for word in ['你好', 'hi', 'hello', '早上', '晚安']):
            return TaskType.GREETING
        
        # 默认使用DeepSeek
        return TaskType.STOCK_ANALYSIS
    
    def get_model(self, task_type: TaskType) -> Model:
        """获取任务对应的模型"""
        return TASK_MODEL_MAP.get(task_type, Model.MINIMAX)
    
    @track_agent_performance("deepseek_model")
    def call_deepseek(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """调用DeepSeek API"""
        if not self.deepseek_key:
            print("⚠️ DeepSeek API Key未配置")
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.deepseek_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': Model.DEEPSEEK.value,
                'messages': [
                    {'role': 'system', 'content': '你是一位资深的A股量化投资顾问贾维斯。'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': max_tokens,
                'temperature': 0.7
            }
            
            resp = requests.post(self.deepseek_url, headers=headers, json=data, timeout=60)
            
            if resp.status_code == 200:
                return resp.json()['choices'][0]['message']['content']
            else:
                print(f"❌ DeepSeek API错误: {resp.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ DeepSeek调用失败: {e}")
            return None
    
    @track_agent_performance("model_router")
    def route(self, text: str, use_deepseek: bool = None) -> str:
        """
        智能路由主函数
        
        Args:
            text: 用户输入
            use_deepseek: 强制使用指定模型 (True=DeepSeek, False=MiniMax, None=自动)
        
        Returns:
            AI回复内容
        """
        if use_deepseek is True:
            # 强制使用DeepSeek
            return self.call_deepseek(text)
        
        if use_deepseek is False:
            # 强制使用MiniMax (通过OpenClaw内置)
            return "[使用MiniMax处理]"
        
        # 自动判断
        task_type = self.classify_task(text)
        model = self.get_model(task_type)
        
        print(f"📋 任务类型: {task_type.value} -> 模型: {model.value}")
        
        if model == Model.DEEPSEEK:
            return self.call_deepseek(text)
        else:
            # MiniMax任务通过OpenClaw内置处理
            return f"[任务类型: {task_type.value} - 建议使用MiniMax模型处理]"


# ==================== 装饰器 ====================

def route_by_task_type(task_type: TaskType = None):
    """
    根据任务类型自动路由的装饰器
    
    Args:
        task_type: 指定任务类型，如果不提供则自动判断
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            router = ModelRouter()
            
            # 获取文本参数
            text = kwargs.get('text') or (args[0] if args else '')
            
            # 确定任务类型
            if task_type:
                actual_task_type = task_type
            else:
                actual_task_type = router.classify_task(text)
            
            # 获取对应模型
            model = router.get_model(actual_task_type)
            
            print(f"🎯 装饰器路由: {func.__name__} -> {actual_task_type.value} -> {model.value}")
            
            # 调用原始函数，传递模型信息
            kwargs['model_info'] = {
                'task_type': actual_task_type,
                'model': model
            }
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def use_deepseek(func):
    """强制使用DeepSeek的装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        router = ModelRouter()
        text = kwargs.get('text') or (args[0] if args else '')
        return router.call_deepseek(text)
    return wrapper


def use_minimax(func):
    """强制使用MiniMax的装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # MiniMax通过OpenClaw内置处理
        return "[使用MiniMax处理]"
    return wrapper


# ==================== 使用示例 ====================

@route_by_task_type()
def analyze_stock(text: str, model_info: Dict = None) -> str:
    """分析股票 - 自动路由"""
    if model_info and model_info['model'] == Model.DEEPSEEK:
        router = ModelRouter()
        return router.call_deepseek(text)
    else:
        return "[使用MiniMax处理股票分析]"


@use_deepseek
def deep_analysis(text: str) -> str:
    """深度分析 - 强制使用DeepSeek"""
    # 函数体不重要，会被装饰器替换
    return text


@use_minimax
def simple_query(text: str) -> str:
    """简单查询 - 强制使用MiniMax"""
    # 函数体不重要，会被装饰器替换
    return text


def example_usage():
    """使用示例"""
    print("🎯 装饰器路由示例:")
    
    # 示例1: 自动路由
    result1 = analyze_stock("分析一下金风科技的走势")
    print(f"自动路由结果: {result1[:50]}...")
    
    # 示例2: 强制DeepSeek
    result2 = deep_analysis("深度分析茅台")
    print(f"强制DeepSeek: {result2[:50]}...")
    
    # 示例3: 强制MiniMax
    result3 = simple_query("查询上证指数")
    print(f"强制MiniMax: {result3}")


if __name__ == "__main__":
    example_usage()
    
    # 显示分析报告
    analytics = get_analytics()
    print("\n📊 路由性能分析:")
    print(analytics.get_report())