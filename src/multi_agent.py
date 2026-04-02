"""
多智能体选股系统 - 贾维斯
使用 DeepSeek + MiniMax 高低搭配

DeepSeek: 选股、策略、推理、代码
MiniMax: 日常对话、信息推送
"""

import json
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# ==================== 模型配置 ====================

class ModelConfig:
    """模型配置"""
    # DeepSeek - 用于复杂推理和选股分析
    DEEPSEEK_API_KEY = "your-deepseek-api-key"
    DEEPSEEK_BASE_URL = "https://api.deepseek.com"
    DEEPSEEK_MODEL = "deepseek-chat"
    
    # MiniMax - 用于日常对话和快速任务
    MINIMAX_API_KEY = "your-minimax-api-key"
    MINIMAX_BASE_URL = "https://api.minimaxi.com/anthropic"
    MINIMAX_MODEL = "MiniMax-M2.7"
    
    @classmethod
    def from_env(cls):
        """从环境变量加载配置"""
        import os
        cls.DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", cls.DEEPSEEK_API_KEY)
        cls.MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", cls.MINIMAX_API_KEY)
        return cls


# ==================== 模型路由 ====================

class ModelRouter:
    """模型路由器 - 根据任务类型选择合适的模型"""
    
    # 需要 DeepSeek 的任务
    DEEPSEEK_TASKS = [
        "选股", "筛选", "量化", "策略", "战法",
        "分析", "推理", "预判", "判断",
        "代码", "Python", "编程", "回测",
        "技术指标", "K线", "财务报表"
    ]
    
    # 需要 MiniMax 的任务
    MINIMAX_TASKS = [
        "推送", "发送", "通知",
        "闲聊", "日常", "问候",
        "查询", "获取", "查看"
    ]
    
    @staticmethod
    def route(task_description: str) -> str:
        """
        判断任务应该使用哪个模型
        返回: 'deepseek' 或 'minimax'
        """
        task_lower = task_description.lower()
        
        for keyword in ModelRouter.DEEPSEEK_TASKS:
            if keyword in task_lower:
                return "deepseek"
        
        for keyword in ModelRouter.MINIMAX_TASKS:
            if keyword in task_lower:
                return "minimax"
        
        # 默认使用 DeepSeek（用于分析任务）
        return "deepseek"


# ==================== DeepSeek 客户端 ====================

class DeepSeekClient:
    """DeepSeek API 客户端"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or ModelConfig.DEEPSEEK_API_KEY
        self.base_url = ModelConfig.DEEPSEEK_BASE_URL
        self.model = ModelConfig.DEEPSEEK_MODEL
    
    def chat(self, messages: List[Dict], system: str = None) -> str:
        """发送聊天请求"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)
        
        payload = {
            "model": self.model,
            "messages": full_messages,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"DeepSeek API 调用失败: {str(e)}"


# ==================== MiniMax 客户端 ====================

class MiniMaxClient:
    """MiniMax API 客户端"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or ModelConfig.MINIMAX_API_KEY
        self.base_url = ModelConfig.MINIMAX_BASE_URL
        self.model = ModelConfig.MINIMAX_MODEL
    
    def chat(self, messages: List[Dict], system: str = None) -> str:
        """发送聊天请求"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)
        
        payload = {
            "model": self.model,
            "messages": full_messages,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/text/chatcompletion_v2",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"MiniMax API 调用失败: {str(e)}"


# ==================== 多智能体系统 ====================

class JarvisMultiAgent:
    """
    贾维斯多智能体选股系统
    
    Agent 架构:
    - 基本面分析师 (DeepSeek): 分析公司财务、业绩
    - 技术分析师 (DeepSeek): 分析K线、技术指标
    - 情绪分析师 (MiniMax): 分析市场情绪、消息面
    - 风控经理 (DeepSeek): 评估风险、仓位建议
    - 交易决策 (DeepSeek): 综合所有分析给出决策
    """
    
    # Agent 系统提示词
    AGENT_PROMPTS = {
        "fundamental": """你是一位资深基本面分析师，专注于公司财务分析。
关注指标：营收增长、净利润、PE、PB、ROE、现金流、负债率
分析维度：行业地位、竞争力、成长性、风险点""",
        
        "technical": """你是一位技术分析专家，擅长K线和技术指标分析。
分析指标：MACD、KDJ、RSI、布林带、均线系统、成交量
分析维度：趋势判断、支撑阻力、买卖信号""",
        
        "sentiment": """你是一位市场情绪分析师，专注于消息面和情绪分析。
分析维度：政策利好/利空、行业动态、主力动向、舆情监控
判断市场整体情绪：乐观/中性/悲观""",
        
        "risk": """你是一位资深风控专家，专注于风险评估。
评估维度：市场风险、行业风险、个股风险、流动性风险
给出仓位建议：轻仓/半仓/重仓/空仓""",
        
        "trader": """你是一位专业交易员，负责综合决策。
整合基本面、技术面、情绪面、风控分析
给出明确操作建议：买入/卖出/观望
包含目标价位、止损价位、仓位配置"""
    }
    
    def __init__(self, deepseek_key: str = None, minimax_key: str = None):
        self.deepseek = DeepSeekClient(deepseek_key)
        self.minimax = MiniMaxClient(minimax_key)
        self.model_router = ModelRouter()
    
    def analyze_stock(self, stock_code: str, stock_name: str = None) -> Dict:
        """
        综合分析一只股票
        返回完整的分析报告
        """
        name = stock_name or stock_code
        
        print(f"\n{'='*60}")
        print(f"开始分析: {name} ({stock_code})")
        print(f"{'='*60}\n")
        
        # 1. 基本面分析 (DeepSeek)
        print("[1/5] 基本面分析...")
        fundamental = self._fundamental_analysis(stock_code, name)
        
        # 2. 技术面分析 (DeepSeek)
        print("[2/5] 技术面分析...")
        technical = self._technical_analysis(stock_code, name)
        
        # 3. 情绪面分析 (MiniMax)
        print("[3/5] 情绪面分析...")
        sentiment = self._sentiment_analysis(stock_code, name)
        
        # 4. 风险评估 (DeepSeek)
        print("[4/5] 风险评估...")
        risk = self._risk_assessment(stock_code, name, fundamental, technical, sentiment)
        
        # 5. 交易决策 (DeepSeek)
        print("[5/5] 综合决策...")
        decision = self._trading_decision(stock_code, name, fundamental, technical, sentiment, risk)
        
        return {
            "stock_code": stock_code,
            "stock_name": name,
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "fundamental": fundamental,
            "technical": technical,
            "sentiment": sentiment,
            "risk": risk,
            "decision": decision
        }
    
    def _fundamental_analysis(self, code: str, name: str) -> str:
        """基本面分析"""
        prompt = f"""分析 {name} ({code}) 的基本面状况：
        
请从以下维度进行分析：
1. 所处行业及行业地位
2. 营收和净利润增长趋势
3. 主要财务指标（PE、PB、ROE）
4. 竞争优势和风险点
5. 综合评分（1-10分）

请用中文输出分析报告。"""
        
        response = self.deepseek.chat(
            messages=[{"role": "user", "content": prompt}],
            system=self.AGENT_PROMPTS["fundamental"]
        )
        return response
    
    def _technical_analysis(self, code: str, name: str) -> str:
        """技术面分析"""
        prompt = f"""分析 {name} ({code}) 的技术面状况：

请从以下维度进行分析：
1. 当前价格位置（相对历史高低点）
2. 均线系统状态（多头/空头排列）
3. MACD指标信号
4. KDJ指标状态
5. 成交量变化
6. 支撑位和压力位
7. 综合评分（1-10分）

请用中文输出分析报告。"""
        
        response = self.deepseek.chat(
            messages=[{"role": "user", "content": prompt}],
            system=self.AGENT_PROMPTS["technical"]
        )
        return response
    
    def _sentiment_analysis(self, code: str, name: str) -> str:
        """情绪面分析"""
        prompt = f"""分析 {name} ({code}) 相关的市场情绪：

请从以下维度进行分析：
1. 近期是否有重大利好/利空消息
2. 板块整体氛围
3. 主力资金动向
4. 市场关注度
5. 情绪评分（乐观/中性/悲观）

请用中文输出分析报告。"""
        
        # 情绪分析用 MiniMax
        response = self.minimax.chat(
            messages=[{"role": "user", "content": prompt}],
            system=self.AGENT_PROMPTS["sentiment"]
        )
        return response
    
    def _risk_assessment(self, code: str, name: str, fundamental: str, technical: str, sentiment: str) -> str:
        """风险评估"""
        prompt = f"""基于以下分析，评估 {name} ({code}) 的风险：

【基本面分析】
{fundamental[:500]}

【技术面分析】
{technical[:500]}

【情绪面分析】
{sentiment[:500]}

请评估：
1. 市场风险等级（高/中/低）
2. 行业风险等级（高/中/低）
3. 个股风险等级（高/中/低）
4. 建议仓位（0-100%）
5. 止损位建议

请用中文输出。"""
        
        response = self.deepseek.chat(
            messages=[{"role": "user", "content": prompt}],
            system=self.AGENT_PROMPTS["risk"]
        )
        return response
    
    def _trading_decision(self, code: str, name: str, fundamental: str, technical: str, 
                          sentiment: str, risk: str) -> str:
        """交易决策"""
        prompt = f"""综合以下分析，给出 {name} ({code}) 的交易决策：

【基本面分析摘要】
{fundamental[:300]}

【技术面分析摘要】
{technical[:300]}

【情绪面分析摘要】
{sentiment[:300]}

【风险评估摘要】
{risk[:300]}

请给出：
1. 最终操作建议：买入/卖出/观望
2. 目标价位
3. 止损价位
4. 仓位建议
5. 持有周期建议
6. 操作理由（简明扼要）

请用中文输出。"""
        
        response = self.deepseek.chat(
            messages=[{"role": "user", "content": prompt}],
            system=self.AGENT_PROMPTS["trader"]
        )
        return response
    
    def format_report(self, result: Dict) -> str:
        """格式化分析报告"""
        report = f"""
{'='*60}
📊 贾维斯多智能体分析报告
{'='*60}

股票: {result['stock_name']} ({result['stock_code']})
分析时间: {result['analysis_time']}

{'='*60}
📈 基本面分析
{'='*60}
{result['fundamental']}

{'='*60}
📉 技术面分析
{'='*60}
{result['technical']}

{'='*60}
💬 情绪面分析
{'='*60}
{result['sentiment']}

{'='*60}
⚠️ 风险评估
{'='*60}
{result['risk']}

{'='*60}
🎯 交易决策
{'='*60}
{result['decision']}

{'='*60}
🤵 贾维斯出品 | 仅供参考，不构成投资建议
{'='*60}
"""
        return report


# ==================== 快速选股接口 ====================

def quick_screen(stock_code: str) -> str:
    """
    快速选股接口 - 使用 DeepSeek
    返回分析结果
    """
    router = ModelRouter()
    model = router.route(f"选股分析 {stock_code}")
    
    if model == "deepseek":
        client = DeepSeekClient()
    else:
        client = MiniMaxClient()
    
    prompt = f"""请分析股票 {stock_code}：

1. 基本面评分（1-10）
2. 技术面评分（1-10）
3. 当前趋势判断
4. 操作建议

请用简洁的中文输出。"""
    
    return client.chat(
        messages=[{"role": "user", "content": prompt}],
        system="你是一位专业股票分析师，简洁高效地给出分析。"
    )


# ==================== 主程序 ====================

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════╗
    ║     贾维斯多智能体选股系统 v1.0           ║
    ║     DeepSeek + MiniMax 高低搭配          ║
    ╚══════════════════════════════════════════╝
    """)
    
    # 初始化
    ModelConfig.from_env()
    agent = JarvisMultiAgent()
    
    # 测试
    test_code = "002202"  # 金风科技
    result = agent.analyze_stock(test_code)
    print(agent.format_report(result))
