"""
TradingAgents 整合模块
将 TradingAgents 多智能体交易框架整合到贾维斯量化系统
"""

import os
import json
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Tuple
import logging

# 导入 TradingAgents
try:
    from tradingagents.graph.trading_graph import TradingAgentsGraph
    from tradingagents.graph.propagation import Propagator
    from tradingagents.default_config import DEFAULT_CONFIG
    TRADING_AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"警告: 无法导入 TradingAgents: {e}")
    print("请确保已安装 TradingAgents: pip install tradingagents")
    TRADING_AGENTS_AVAILABLE = False
    TradingAgentsGraph = None
    Propagator = None
    DEFAULT_CONFIG = {}

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradingAgentsWrapper:
    """
    TradingAgents 包装器
    将 TradingAgentsGraph 封装为适合贾维斯量化系统的接口
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        debug: bool = False,
        use_chinese_output: bool = True,
        llm_provider: str = "openai",
        deep_think_llm: str = "gpt-4",
        quick_think_llm: str = "gpt-3.5-turbo"
    ):
        """
        初始化 TradingAgents 包装器
        
        Args:
            config: TradingAgents 配置字典
            debug: 是否启用调试模式
            use_chinese_output: 是否使用中文输出
            llm_provider: LLM 提供商 (openai, anthropic, google, etc.)
            deep_think_llm: 深度思考模型
            quick_think_llm: 快速思考模型
        """
        if not TRADING_AGENTS_AVAILABLE:
            raise ImportError("TradingAgents 未安装，请先安装: pip install tradingagents")
        
        self.debug = debug
        self.use_chinese_output = use_chinese_output
        self.config = config or DEFAULT_CONFIG.copy()
        
        # 更新配置以支持中文输出
        if use_chinese_output:
            self._configure_for_chinese()
        
        # 设置 LLM 提供商
        self.config["llm_provider"] = llm_provider
        self.config["deep_think_llm"] = deep_think_llm
        self.config["quick_think_llm"] = quick_think_llm
        
        # 初始化 TradingAgentsGraph
        self.graph = TradingAgentsGraph(
            selected_analysts=["market", "social", "news", "fundamentals"],
            debug=debug,
            config=self.config
        )
        
        logger.info("TradingAgents 包装器初始化完成")
        logger.info(f"配置: LLM提供商={llm_provider}, 深度模型={deep_think_llm}, 快速模型={quick_think_llm}")
    
    def _configure_for_chinese(self):
        """配置 TradingAgents 以支持中文输出"""
        # 在系统提示中添加中文要求
        if "system_prompts" not in self.config:
            self.config["system_prompts"] = {}
        
        # 添加中文指令到系统提示
        chinese_instruction = "请使用中文进行所有分析和报告。所有输出必须是中文。"
        
        # 更新各个代理的系统提示
        for agent_type in ["market", "social", "news", "fundamentals", "bull", "bear", "trader"]:
            if agent_type in self.config["system_prompts"]:
                self.config["system_prompts"][agent_type] += f"\n\n{chinese_instruction}"
            else:
                self.config["system_prompts"][agent_type] = chinese_instruction
    
    def propagate(
        self,
        company_name: str,
        trade_date: Optional[str] = None,
        ticker: Optional[str] = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        执行 TradingAgents 的传播分析
        
        Args:
            company_name: 公司名称
            trade_date: 交易日期 (格式: YYYY-MM-DD)，默认为今天
            ticker: 股票代码，可选
            
        Returns:
            tuple: (最终状态字典, 处理后的信号字典)
        """
        if trade_date is None:
            trade_date = date.today().isoformat()
        
        # 设置股票代码
        if ticker:
            self.graph.ticker = ticker
        
        logger.info(f"开始分析: 公司={company_name}, 日期={trade_date}, 股票代码={ticker}")
        
        try:
            # 执行 TradingAgents 分析
            final_state, processed_signal = self.graph.propagate(company_name, trade_date)
            
            logger.info(f"分析完成: 最终决策={processed_signal.get('decision', '未知')}")
            
            # 转换为中文友好的格式
            if self.use_chinese_output:
                final_state = self._translate_to_chinese(final_state)
                processed_signal = self._translate_signal_to_chinese(processed_signal)
            
            return final_state, processed_signal
            
        except Exception as e:
            logger.error(f"TradingAgents 分析失败: {e}")
            raise
    
    def _translate_to_chinese(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """将状态字典中的关键字段翻译为中文（如果可能）"""
        # 这里可以添加具体的翻译逻辑
        # 目前只是标记为已翻译
        state["_translated_to_chinese"] = True
        return state
    
    def _translate_signal_to_chinese(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """将信号字典翻译为中文"""
        if not signal:
            return signal
        
        # 翻译决策类型
        decision_map = {
            "BUY": "买入",
            "SELL": "卖出", 
            "HOLD": "持有",
            "STRONG_BUY": "强烈买入",
            "STRONG_SELL": "强烈卖出"
        }
        
        if "decision" in signal:
            signal["decision_cn"] = decision_map.get(signal["decision"], signal["decision"])
        
        signal["_translated_to_chinese"] = True
        return signal
    
    def analyze_stock(
        self,
        ticker: str,
        company_name: str,
        trade_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        分析股票的综合方法
        
        Args:
            ticker: 股票代码
            company_name: 公司名称
            trade_date: 交易日期
            
        Returns:
            包含分析结果的字典
        """
        logger.info(f"开始股票分析: {ticker} ({company_name})")
        
        try:
            # 执行 TradingAgents 分析
            final_state, processed_signal = self.propagate(
                company_name=company_name,
                trade_date=trade_date,
                ticker=ticker
            )
            
            # 提取关键信息
            analysis_result = {
                "ticker": ticker,
                "company_name": company_name,
                "trade_date": trade_date or date.today().isoformat(),
                "decision": processed_signal.get("decision", "未知"),
                "decision_cn": processed_signal.get("decision_cn", "未知"),
                "confidence": processed_signal.get("confidence", 0.5),
                "reasoning": self._extract_reasoning(final_state),
                "reports": {
                    "market": final_state.get("market_report", ""),
                    "sentiment": final_state.get("sentiment_report", ""),
                    "news": final_state.get("news_report", ""),
                    "fundamentals": final_state.get("fundamentals_report", ""),
                },
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"股票分析完成: {ticker} -> {analysis_result['decision_cn']}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"股票分析失败 {ticker}: {e}")
            return {
                "ticker": ticker,
                "company_name": company_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_reasoning(self, state: Dict[str, Any]) -> str:
        """从状态中提取推理过程"""
        reasoning_parts = []
        
        # 添加各个报告
        for report_type in ["market_report", "sentiment_report", "news_report", "fundamentals_report"]:
            if report_type in state and state[report_type]:
                reasoning_parts.append(f"{report_type.replace('_report', '')}: {state[report_type][:200]}...")
        
        # 添加交易者决策
        if "trader_investment_plan" in state:
            reasoning_parts.append(f"交易者计划: {state['trader_investment_plan'][:200]}...")
        
        # 添加最终决策
        if "final_trade_decision" in state:
            reasoning_parts.append(f"最终决策: {state['final_trade_decision'][:200]}...")
        
        return "\n\n".join(reasoning_parts)
    
    def batch_analyze(
        self,
        stock_list: List[Tuple[str, str]],
        trade_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        批量分析多个股票
        
        Args:
            stock_list: 股票列表，每个元素为 (ticker, company_name)
            trade_date: 交易日期
            
        Returns:
            分析结果列表
        """
        results = []
        
        logger.info(f"开始批量分析 {len(stock_list)} 只股票")
        
        for ticker, company_name in stock_list:
            try:
                result = self.analyze_stock(ticker, company_name, trade_date)
                results.append(result)
                logger.info(f"完成: {ticker} -> {result.get('decision_cn', '未知')}")
            except Exception as e:
                logger.error(f"分析失败 {ticker}: {e}")
                results.append({
                    "ticker": ticker,
                    "company_name": company_name,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        logger.info(f"批量分析完成: {len(results)}/{len(stock_list)} 成功")
        return results


class JarvisTradingAgentsIntegration:
    """
    贾维斯量化系统与 TradingAgents 的集成类
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化集成
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.wrapper = None
        self.initialized = False
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加载配置"""
        config = {
            "use_chinese_output": True,
            "llm_provider": "openai",
            "deep_think_llm": "gpt-4",
            "quick_think_llm": "gpt-3.5-turbo",
            "debug": False
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    config.update(user_config)
            except Exception as e:
                logger.warning(f"无法加载配置文件 {config_path}: {e}")
        
        return config
    
    def initialize(self):
        """初始化 TradingAgents 包装器"""
        if not TRADING_AGENTS_AVAILABLE:
            logger.error("TradingAgents 不可用，请先安装")
            return False
        
        try:
            self.wrapper = TradingAgentsWrapper(
                config=None,  # 使用默认配置
                debug=self.config.get("debug", False),
                use_chinese_output=self.config.get("use_chinese_output", True),
                llm_provider=self.config.get("llm_provider", "openai"),
                deep_think_llm=self.config.get("deep_think_llm", "gpt-4"),
                quick_think_llm=self.config.get("quick_think_llm", "gpt-3.5-turbo")
            )
            self.initialized = True
            logger.info("TradingAgents 集成初始化成功")
            return True
        except Exception as e:
            logger.error(f"TradingAgents 集成初始化失败: {e}")
            return False
    
    def integrate_with_screener(self, screener):
        """
        与贾维斯选股系统集成
        
        Args:
            screener: 选股系统实例
            
        Returns:
            集成后的分析函数
        """
        if not self.initialized:
            if not self.initialize():
                raise RuntimeError("TradingAgents 集成未初始化")
        
        def enhanced_analyze(stock_data):
            """
            增强的股票分析函数
            """
            # 使用原有选股系统分析
            base_analysis = screener.analyze_stock(stock_data)
            
            # 使用 TradingAgents 进行多智能体分析
            ticker = stock_data.get("ticker")
            company_name = stock_data.get("company_name", ticker)
            
            try:
                ta_analysis = self.wrapper.analyze_stock(ticker, company_name)
                
                # 合并分析结果
                enhanced_result = {
                    **base_analysis,
                    "trading_agents_analysis": ta_analysis,
                    "combined_decision": self._combine_decisions(base_analysis, ta_analysis),
                    "analysis_timestamp": datetime.now().isoformat()
                }
                
                return enhanced_result
                
            except Exception as e:
                logger.error(f"TradingAgents 分析失败 {ticker}: {e}")
                return {
                    **base_analysis,
                    "trading_agents_error": str(e),
                    "analysis_timestamp": datetime.now().isoformat()
                }
        
        return enhanced_analyze
    
    def _combine_decisions(self, base_analysis: Dict, ta_analysis: Dict) -> str:
        """结合基础分析和 TradingAgents 分析的决策"""
        base_decision = base_analysis.get("decision", "HOLD")
        ta_decision = ta_analysis.get("decision", "HOLD")
        
        # 简单的决策结合逻辑
        decision_scores = {
            "STRONG_BUY": 2,
            "BUY": 1,
            "HOLD": 0,
            "SELL": -1,
            "STRONG_SELL": -2
        }
        
        base_score = decision_scores.get(base_decision, 0)
        ta_score = decision_scores.get(ta_decision, 0)
        
        total_score = base_score + ta_score
        
        # 根据总分决定最终决策
        if total_score >= 3:
            return "STRONG_BUY"
        elif total_score >= 1:
            return "BUY"
        elif total_score <= -3:
            return "STRONG_SELL"
        elif total_score <= -1:
            return "SELL"
        else:
            return "HOLD"
    
    def generate_report(self, analysis_results: List[Dict[str, Any]]) -> str:
        """
        生成分析报告
        
        Args:
            analysis_results: 分析结果列表
            
        Returns:
            报告字符串
        """
        if not analysis_results:
            return "没有分析结果"
        
        report_lines = ["# TradingAgents 多智能体分析报告"]
        report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"分析股票数量: {len(analysis_results)}")
        report_lines.append("")
        
        for i, result in enumerate(analysis_results, 1):
            report_lines.append(f"## {i}. {result.get('ticker', '未知')} - {result.get('company_name', '未知公司')}")
            report_lines.append(f"- **最终决策**: {result.get('decision_cn', '未知')}")
            report_lines.append(f"- **置信度**: {result.get('confidence', '未知')}")
            
            if "error" in result:
                report_lines.append(f"- **错误**: {result['error']}")
            else:
                # 添加简要推理
                reasoning = result.get("reasoning", "")
                if reasoning and len(reasoning) > 200:
                    reasoning = reasoning[:200] + "..."
                report_lines.append(f"- **分析摘要**: {reasoning}")
            
            report_lines.append("")
        
        # 统计决策分布
        decisions = [r.get("decision_cn", "未知") for r in analysis_results if "error" not in r]
        if decisions:
            from collections import Counter
            decision_counts = Counter(decisions)
            report_lines.append("## 决策分布统计")
            for decision, count in decision_counts.items():
                report_lines.append(f"- {decision}: {count} 只股票")
        
        return "\n".join(report_lines)


# 使用示例
if __name__ == "__main__":
    # 示例：如何使用 TradingAgents 集成
    print("=== TradingAgents 集成模块测试 ===")
    
    if not TRADING_AGENTS_AVAILABLE:
        print("TradingAgents 未安装，跳过测试")
    else:
        try:
            # 创建包装器
            wrapper = TradingAgentsWrapper(
                debug=False,
                use_chinese_output=True,
                llm_provider="openai",  # 需要设置相应的 API 密钥
                deep_think_llm="gpt-4",
                quick_think_llm="gpt-3.5-turbo"
            )
            
            print("TradingAgents 包装器创建成功")
            
            # 示例股票分析
            test_stocks = [
                ("AAPL", "苹果公司"),
                ("MSFT", "微软公司"),
            ]
            
            print(f"\n准备分析 {len(test_stocks)} 只股票...")
            print("注意: 需要设置相应的 API 密钥才能实际运行")
            print("示例代码演示完成")
            
        except Exception as e:
            print(f"示例运行出错: {e}")