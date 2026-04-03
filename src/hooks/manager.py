"""
钩子管理器
用于在关键阶段执行自定义逻辑
"""

from typing import Dict, List, Callable, Any
import asyncio


class HookManager:
    """钩子管理器"""
    
    # 预定义阶段
    STAGES = [
        'pre_analysis',      # 分析前
        'post_analysis',     # 分析后
        'pre_decision',      # 决策前
        'post_decision',     # 决策后
        'on_error',          # 错误时
        'before_tool_execute',  # 工具执行前
        'after_tool_execute',   # 工具执行后
        'before_model_call',    # 模型调用前
        'after_model_call',     # 模型调用后
    ]
    
    def __init__(self):
        self._hooks: Dict[str, List[Callable]] = {stage: [] for stage in self.STAGES}
    
    def register(self, stage: str, func: Callable) -> None:
        """
        注册钩子函数
        
        Args:
            stage: 钩子阶段
            func: 钩子函数，必须接受 context 参数并返回 bool 或 None
        """
        if stage not in self._hooks:
            raise ValueError(f"无效的钩子阶段: {stage}，可用阶段: {self.STAGES}")
        
        self._hooks[stage].append(func)
        print(f"✅ 注册钩子: {stage} -> {func.__name__}")
    
    def unregister(self, stage: str, func: Callable) -> None:
        """取消注册钩子"""
        if stage in self._hooks:
            try:
                self._hooks[stage].remove(func)
                print(f"🗑️ 取消注册钩子: {stage} -> {func.__name__}")
            except ValueError:
                pass
    
    async def execute(self, stage: str, context: Dict[str, Any]) -> bool:
        """
        执行指定阶段的所有钩子
        
        Args:
            stage: 钩子阶段
            context: 上下文数据
        
        Returns:
            True: 所有钩子执行成功
            False: 有钩子返回 False 或抛出异常
        """
        if stage not in self._hooks:
            raise ValueError(f"无效的钩子阶段: {stage}")
        
        hooks = self._hooks.get(stage, [])
        if not hooks:
            return True
        
        print(f"🔧 执行钩子阶段: {stage} ({len(hooks)} 个钩子)")
        
        for hook in hooks:
            try:
                # 执行钩子
                result = await hook(context) if asyncio.iscoroutinefunction(hook) else hook(context)
                
                # 如果钩子返回 False，则中断执行链
                if result is False:
                    print(f"⚠️ 钩子 {hook.__name__} 返回 False，中断执行链")
                    return False
                
                # 更新上下文（如果钩子返回了新的上下文）
                if isinstance(result, dict):
                    context.update(result)
                    
            except Exception as e:
                print(f"❌ 钩子 {hook.__name__} 执行失败: {str(e)}")
                # 错误钩子阶段不中断，其他阶段中断
                if stage != 'on_error':
                    return False
        
        return True
    
    def get_hook_count(self, stage: str = None) -> int:
        """获取钩子数量"""
        if stage:
            return len(self._hooks.get(stage, []))
        else:
            return sum(len(hooks) for hooks in self._hooks.values())
    
    def list_hooks(self) -> Dict[str, List[str]]:
        """列出所有钩子"""
        result = {}
        for stage, hooks in self._hooks.items():
            if hooks:
                result[stage] = [func.__name__ for func in hooks]
        return result
    
    def clear(self, stage: str = None) -> None:
        """清空钩子"""
        if stage:
            if stage in self._hooks:
                self._hooks[stage].clear()
                print(f"🧹 清空钩子阶段: {stage}")
        else:
            for stage in self._hooks:
                self._hooks[stage].clear()
            print("🧹 清空所有钩子")


# ==================== 内置钩子示例 ====================

async def log_hook(context: Dict) -> None:
    """日志钩子"""
    print(f"📝 钩子日志: {context.get('stage', 'unknown')}")
    return True

async def timing_hook(context: Dict) -> Dict:
    """计时钩子"""
    import time
    if 'start_time' not in context:
        context['start_time'] = time.time()
    else:
        elapsed = time.time() - context['start_time']
        context['elapsed_time'] = elapsed
        print(f"⏱️ 执行时间: {elapsed:.2f}秒")
    return context

async def validation_hook(context: Dict) -> bool:
    """验证钩子"""
    # 检查必要参数
    required = context.get('required_fields', [])
    for field in required:
        if field not in context:
            print(f"❌ 缺少必要字段: {field}")
            return False
    return True

async def error_handler_hook(context: Dict) -> None:
    """错误处理钩子"""
    error = context.get('error')
    if error:
        print(f"🚨 错误处理: {error}")
        # 可以在这里记录错误、发送通知等
    return True


# ==================== 钩子管理器单例 ====================

_hook_manager_instance = None

def get_hook_manager() -> HookManager:
    """获取钩子管理器单例"""
    global _hook_manager_instance
    if _hook_manager_instance is None:
        _hook_manager_instance = HookManager()
        # 注册内置钩子
        _hook_manager_instance.register('pre_analysis', log_hook)
        _hook_manager_instance.register('post_analysis', timing_hook)
        _hook_manager_instance.register('on_error', error_handler_hook)
    return _hook_manager_instance