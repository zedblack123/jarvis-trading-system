"""
TradingAgents 集成模块
将 TradingAgents 多智能体交易框架整合到贾维斯量化系统
"""

from .trading_agents_integration import (
    TradingAgentsWrapper,
    JarvisTradingAgentsIntegration,
    TRADING_AGENTS_AVAILABLE
)

__all__ = [
    "TradingAgentsWrapper",
    "JarvisTradingAgentsIntegration",
    "TRADING_AGENTS_AVAILABLE"
]

__version__ = "1.0.0"