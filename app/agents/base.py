from abc import ABC, abstractmethod

from app.graph.state import GraphState, Task
class BaseAgent(ABC):
    """
    所有 Agent 的基类
    """

    name: str = None        # agent 名称
    description: str = ""  # 给 Assign 用的能力描述

    @abstractmethod
    def run(self, task: Task,state: GraphState):
        """
        执行任务核心接口

        instruction: 本任务的自然语言指令
        input:       上一步结果 / 文件 / 数据

        返回: string 或 dict（最终都会进 Plan context）
        """
        return 
