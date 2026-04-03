"""
多智能体选股系统 - 贾维斯
使用 DeepSeek + MiniMax 高低搭配

DeepSeek: 选股、策略、推理、代码
MiniMax: 日常对话、信息推送

改进版本：集成工具系统、钩子系统、分析追踪
"""

import json
import requests
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# 导入新模块
from tools import ToolRegistry, StockDataTool, TechnicalAnalysisTool
from hooks import get_hook_manager
from analytics import get_analytics, track_agent_performance


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
        self.hook_manager = get_hook_manager()
    
    @track_agent_performance("deepseek_client")
    def chat(self, messages: List[Dict], system: str = None) -> str:
        """发送聊天请求"""
        # 执行钩子：模型调用前
        context = {
            "stage": "before_model_call",
            "model": "deepseek",
            "messages": messages,
            "system": system
        }
        
        if not self.hook_manager.execute("before_model_call", context):
            return "钩子中断了模型调用"
        
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
            result = response.json()["choices"][0]["message"]["content"]
            
            # 执行钩子：模型调用后
            context.update({
                "stage": "after_model_call",
                "response": result,
                "success": True
            })
            self.hook_manager.execute("after_model_call", context)
            
            return result
        except Exception as e:
            # 执行钩子：错误处理
            context.update({
                "stage": "on_error",
                "error": str(e),
                "success": False
            })
            self.hook_manager.execute("on_error", context)
            
            return f"DeepSeek API 调用失败: {str(e)}"


# ==================== MiniMax 客户端 ====================

class MiniMaxClient:
    """MiniMax API 客户端"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or ModelConfig.MINIMAX_API_KEY
        self.base_url = ModelConfig.MINIMAX_BASE_URL
        self.model = ModelConfig.MINIMAX_MODEL
        self.hook_manager = get_hook_manager()
    
    @track_agent_performance("minimax_client")
    def chat(self, messages: List[Dict], system: str = None) -> str:
        """发送聊天请求"""
        # 执行钩子：模型调用前
        context = {
            "stage": "before_model_call",
            "model": "minimax",
            "messages": messages,
            "system": system
        }
        
        if not self.hook_manager.execute("before_model_call", context):
            return "钩子中断了模型调用"
        
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
            result = response.json()["choices"][0]["message"]["content"]
            
            # 执行钩子：模型调用后
            context.update({
                "stage": "after_model_call",
                "response": result,
                "success": True
            })
            self.hook_manager.execute("after_model_call", context)
            
            return result
        except Exception as e:
            # 执行钩子：错误处理
            context.update({
                "stage": "on_error",
                "error": str(e),
                "success": False
            })
            self.hook_manager.execute("on_error", context)
            
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
        
        # 集成工具系统
        self.tool_registry = ToolRegistry.get_instance()
        self._init_tools()
        
        # 集成钩子系统
        self.hook_manager = get_hook_manager()
        
        # 集成分析系统
        self.analytics = get_analytics()
    
    def _init_tools(self):
        """初始化工具"""
        # 注册股票数据工具
        stock_tool = StockDataTool()
        self.tool_registry.register(stock_tool)
        
        # 注册技术分析工具
        tech_tool = TechnicalAnalysisTool()
        self.tool_registry.register(tech_tool)
        
        print(f"🛠️ 已注册工具: {self.tool_registry.list_tool_names()}")
    
    @track_agent_performance("jarvis_multi_agent")
    def analyze_stock(self, stock_code: str, stock_name: str = None) -> Dict:
        """
        综合分析一只股票
        返回完整的分析报告
        """
        name = stock_name or stock_code
        
        print(f"\n{'='*60}")
        print(f"开始分析: {name} ({stock_code})")
        print(f"{'='*60}\n")
        
        # 执行钩子：分析前
        context = {
            "stage": "pre_analysis",
            "stock_code": stock_code,
            "stock_name": name,
            "start_time": time.time()
        }
        
        if not self.hook_manager.execute("pre_analysis", context):
            return {"error": "分析被钩子中断"}
        
        try:
            # 1. 使用工具获取股票数据
            print("[1/6] 获取股票数据...")
            stock_data = self._get_stock_data(stock_code)
            
            # 2. 基本面分析 (DeepSeek)
            print("[2/6] 基本面分析...")
            fundamental = self._fundamental_analysis(stock_code, name, stock_data)
            
            # 3. 技术面分析 (DeepSeek)
            print("[3/6] 技术面分析...")
            technical = self._technical_analysis(stock_code, name, stock_data)
            
            # 4. 情绪面分析 (MiniMax)
            print("[4/6] 情绪面分析...")
            sentiment = self._sentiment_analysis(stock_code, name)
            
            # 5. 风险评估 (DeepSeek)
            print("[5/6] 风险评估...")
            risk = self._risk_assessment(stock_code, name, fundamental, technical, sentiment)
            
            # 6. 交易决策 (DeepSeek)
            print("[6/6] 综合决策...")
            decision = self._trading_decision(stock_code, name, fundamental, technical, sentiment, risk)
            
            # 执行钩子：分析后
            context.update({
                "stage": "post_analysis",
                "analysis_results": {
                    "fundamental": fundamental[:100],
                    "technical": technical[:100],
                    "sentiment": sentiment[:100],
                    "risk": risk[:100],
                    "decision": decision[:100]
                },
                "end_time": time.time(),
                "success": True
            })
            self.hook_manager.execute("post_analysis", context)
            
            return {
                "stock_code": stock_code,
                "stock_name": name,
                "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "fundamental": fundamental,
                "technical": technical,
                "sentiment": sentiment,
                "risk": risk,
                "decision": decision,
                "stock_data_summary": stock_data.get("summary", {}) if isinstance(stock_data, dict) else {}
            }
            
        except Exception as e:
            # 执行钩子：错误处理
            context.update({
                "stage": "on_error",
                "error": str(e),
                "success": False
            })
            self.hook_manager.execute("on_error", context)
            
            return {
                "stock_code": stock_code,
                "stock_name": name,
                "error": f"分析失败: {str(e)}"
            }
    
    def _get_stock_data(self, stock_code: str) -> Dict:
        """使用工具获取股票数据"""
        try:
            # 执行钩子：工具执行前
            context = {
                "stage": "before_tool_execute",
                "tool_name": "stock_data",
                "stock_code": stock_code
            }
            self.hook_manager.execute("before_tool_execute", context)
            
            # 调用股票数据工具
            result = self.tool_registry.execute_tool(
                "stock_data",
                stock_code=stock_code,
                data_type="history",
                period="daily"
            )
            
            # 执行钩子：工具执行后
            context.update({
                "stage": "after_tool_execute",
                "result": result,
                "success": "error" not in result
            })
            self.hook_manager.execute("after_tool_execute", context)
            
            return result
        except Exception as e:
            return {"error": f"获取股票数据失败: {str(e)}"}
    
    @track_agent_performance("fundamental_agent")
    def _fundamental_analysis(self, code: str, name: str, stock_data: Dict = None) -> str:
        """基本面分析"""
        # 构建提示词，包含工具获取的数据
        data_context = ""
        if stock_data and "error" not in stock_data:
            if "latest_price" in stock_data:
                data_context = f"\n当前价格: {stock_data['latest_price']}"
            if "latest_date" in stock_data:
                data_context += f"\n数据日期: {stock_data['latest_date']}"
        
        prompt = f"""分析 {name} ({code}) 的基本面状况：{data_context}
        
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
    
    @track_agent_performance("technical_agent")
    def _technical_analysis(self, code: str, name: str, stock_data: Dict = None) -> str:
        """技术面分析"""
        # 使用技术分析工具
        tech_indicators = {}
        if stock_data and "error" not in stock_data and "data" in stock_data:
            try:
                # 提取价格数据用于技术分析
                price_data = stock_data.get("data", [])
                if price_data:
                    tech_result = self.tool_registry.execute_tool(
                        "technical",
                        stock_code=code,
                        price_data=price_data,
                        indicators=["MA", "MACD", "KDJ", "RSI", "BOLL"]
                    )
                    
                    if "error" not in tech_result:
                        tech_indicators = tech_result.get("indicator_values", {})
                        signals = tech_result.get("signals", {})
            except Exception as e:
                print(f"⚠️ 技术分析工具失败: {str(e)}")
        
        # 构建提示词
        tech_context = ""
        if tech_indicators:
            tech_context = "\n技术指标数据："
            for key, value in tech_indicators.items():
                if value is not None:
                    tech_context += f"\n  • {key}: {value:.2f}" if isinstance(value, (int, float)) else f"\n  • {key}: {value}"
        
        prompt = f"""分析 {name} ({code}) 的技术面状况：{tech_context}

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
    
    @track_agent_performance("sentiment_agent")
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
    
    @track_agent_performance("risk_agent")
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
    
    @track_agent_performance("trader_agent")
    def _trading_decision(self, code: str, name: str, fundamental: str, technical: str, 
                          sentiment: str, risk: str) -> str:
        """交易决策"""
        # 执行钩子：决策前
        context = {
            "stage": "pre_decision",
            "stock_code": code,
            "stock_name": name,
            "analysis_summary": {
                "fundamental": fundamental[:100],
                "technical": technical[:100],
                "sentiment": sentiment[:100],
                "risk": risk[:100]
            }
        }
        
        if not self.hook_manager.execute("pre_decision", context):
            return "决策被钩子中断"
        
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
        
        # 执行钩子：决策后
        context.update({
            "stage": "post_decision",
            "decision": response[:100],
            "success": True
        })
        self.hook_manager.execute("post_decision", context)
        
        return response
    
    def format_report(self, result: Dict) -> str:
        """格式化分析报告"""
        if "error" in result:
            return f"""
{'='*60}
❌ 分析失败
{'='*60}

股票: {result.get('stock_name', '未知')} ({result.get('stock_code', '未知')})
错误: {result['error']}

{'='*60}
🤵 贾维斯出品
{'='*60}
"""
        
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
📊 分析统计
{'='*60}
工具调用: {len(self.tool_registry.list_tools())} 个工具已注册
钩子数量: {self.hook_manager.get_hook_count()} 个钩子已注册

{'='*60}
🤵 贾维斯出品 | 仅供参考，不构成投资建议
{'='*60}
"""
        return report
    
    def get_system_status(self) -> Dict:
        """获取系统状态"""
        return {
            "tools": {
                "count": len(self.tool_registry.list_tools()),
                "names": self.tool_registry.list_tool_names()
            },
            "hooks": {
                "count": self.hook_manager.get_hook_count(),
                "stages": self.hook_manager.list_hooks()
            },
            "analytics": {
                "report": self.analytics.get_report()
            }
        }


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
    ║     贾维斯多智能体选股系统 v2.0           ║
    ║     DeepSeek + MiniMax 高低搭配          ║
    ║     集成工具系统 + 钩子系统 + 分析追踪    ║
    ╚══════════════════════════════════════════╝
    """)
    
    # 初始化
    ModelConfig.from_env()
    agent = JarvisMultiAgent()
    
    # 显示系统状态
    status = agent.get_system_status()
    print(f"\n🛠️ 系统状态:")
    print(f"  • 工具数量: {status['tools']['count']}")
    print(f"  • 钩子数量: {status['hooks']['count']}")
    
    # 测试
    test_code = "002202"  # 金风科技
    print(f"\n🔍 开始测试分析: {test_code}")
    
    result = agent.analyze_stock(test_code)
    print(agent.format_report(result))
    
    # 显示分析报告
    print("\n📊 性能分析报告:")
    print(agent.analytics.get_report())