"""
工具基类
所有工具都继承自 BaseTool
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTool(ABC):
    """工具基类"""
    name = ""
    description = ""
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """执行工具"""
        raise NotImplementedError
    
    def get_permission_level(self) -> int:
        """获取权限等级"""
        return 1  # LOW
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "permission_level": self.get_permission_level()
        }