"""
智能模型路由
根据任务类型自动选择最合适的模型
- DeepSeek: 推理分析 (股票分析、策略制定、市场研判)
- MiniMax: 其他场景 (简单问答、查询、推送)
"""
import os
import requests
from typing import Dict, Optional
from enum import Enum


class Model(Enum):
    """可用模型"""
    DEEPSEEK = "deepseek/deepseek-chat"
    MINIMAX = "minimax-portal/MiniMax-M2.7"
    # 其他模型可扩展
    # CLAUDE = "claude-3-sonnet"
    # GPT4 = "gpt-4"


class TaskType(Enum):
    """任务类型"""
    # DeepSeek 擅长的推理任务
    STOCK_ANALYSIS = "stock_analysis"      # 股票分析
    MARKET_RESEARCH = "market_research"     # 市场研判
    STRATEGY_FORMULATE = "strategy"          # 策略制定
    TRADING_SIGNALS = "trading_signals"    # 交易信号分析
    PORTFOLIO_OPTIMIZE = "portfolio"      # 组合优化
    RISK_ASSESSMENT = "risk"                # 风险评估
    NEWS_ANALYSIS = "news_analysis"        # 新闻深度分析
    
    # MiniMax 擅长的简单任务
    SIMPLE_QUERY = "query"                   # 简单查询
    NEWS_PUSH = "push"                      # 推送通知
    TEXT_SUMMARY = "summary"               # 简单总结
    GREETING = "greeting"                  # 问候
    SYSTEM_CMD = "system"                   # 系统命令


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
    """模型路由器"""
    
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
    
    def classify_task(self, text: str) -> TaskType:
        """根据文本内容自动识别任务类型"""
        text_lower = text.lower()
        
        # DeepSeek任务关键词
        deepseek_keywords = [
            '分析', '研判', '策略', '推荐', '预测', '评估',
            '选股', '股票', '市场', '走势', '操作建议',
            '板块', '行业', '财报', '基本面', '技术面',
            '买入', '卖出', '止损', '仓位', '风控',
            '投资组合', '收益率', '回测'
        ]
        
        # MiniMax任务关键词
        minimax_keywords = [
            '查询', '查看', '获取', '今天', '现在',
            '推送', '发送', '通知', '提醒',
            '你好', 'hi', 'hello', '早上好', '晚安',
            '多少钱', '是什么', '怎么样'
        ]
        
        # 计算匹配度
        deepseek_score = sum(1 for kw in deepseek_keywords if kw in text_lower)
        minimax_score = sum(1 for kw in minimax_keywords if kw in text_lower)
        
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
        
        # 默认根据分数判断
        if deepseek_score > minimax_score:
            return TaskType.STOCK_ANALYSIS
        else:
            return TaskType.SIMPLE_QUERY
    
    def get_model(self, task_type: TaskType) -> Model:
        """获取任务对应的模型"""
        return TASK_MODEL_MAP.get(task_type, Model.MINIMAX)
    
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


# ==================== 使用示例 ====================

def example_usage():
    """使用示例"""
    router = ModelRouter()
    
    # 示例1: 股票分析 -> 自动使用DeepSeek
    query1 = "分析一下金风科技的走势，推荐操作"
    result1 = router.route(query1)
    print(f"Query: {query1}")
    print(f"Result: {result1}")
    
    # 示例2: 简单查询 -> 使用MiniMax
    query2 = "查询上证指数当前点位"
    task_type = router.classify_task(query2)
    model = router.get_model(task_type)
    print(f"\nQuery: {query2}")
    print(f"Task: {task_type.value}, Model: {model.value}")
    
    # 示例3: 强制使用DeepSeek
    query3 = "简单告诉我上证指数点位"
    result3 = router.route(query3, use_deepseek=True)
    print(f"\nQuery: {query3}")
    print(f"Result: {result3}")


if __name__ == "__main__":
    example_usage()
