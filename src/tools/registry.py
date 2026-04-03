"""
工具注册表（单例）
统一管理所有工具
"""

from typing import Dict, List, Optional
from .base import BaseTool


class ToolRegistry:
    """工具注册表（单例）"""
    _instance = None
    _tools: Dict[str, BaseTool] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._tools = {}
            self._initialized = True
    
    @classmethod
    def get_instance(cls) -> 'ToolRegistry':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register(self, tool: BaseTool) -> None:
        """注册工具"""
        if not tool.name:
            raise ValueError("工具必须设置 name 属性")
        self._tools[tool.name] = tool
        print(f"✅ 注册工具: {tool.name} - {tool.description}")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """获取工具"""
        return self._tools.get(name)
    
    def list_tools(self) -> List[BaseTool]:
        """列出所有工具"""
        return list(self._tools.values())
    
    def list_tool_names(self) -> List[str]:
        """列出所有工具名称"""
        return list(self._tools.keys())
    
    def get_tool_info(self, name: str) -> Optional[Dict]:
        """获取工具信息"""
        tool = self.get_tool(name)
        if tool:
            return tool.to_dict()
        return None
    
    def execute_tool(self, name: str, **kwargs) -> Dict:
        """执行工具"""
        tool = self.get_tool(name)
        if not tool:
            return {"error": f"工具 '{name}' 未找到"}
        
        try:
            import asyncio
            # 同步调用异步方法
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(tool.execute(**kwargs))
            return result
        except Exception as e:
            return {"error": f"工具执行失败: {str(e)}"}
    
    def clear(self) -> None:
        """清空所有工具"""
        self._tools.clear()
        print("🧹 已清空所有工具")