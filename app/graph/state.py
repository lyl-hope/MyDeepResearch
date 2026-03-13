from typing import List, Optional, Dict, Any, ClassVar
from pydantic import Field
from pydantic import BaseModel
from collections import deque

class Task(BaseModel):
    title:  Optional[str] = None
    content: Optional[str] = None
    data : Optional[str] = None
    agent: Optional[str] = None   # search / write / analyze ...
    status: str = "todo"          # todo / doing / done
    result: Optional[str] = None
class PlanItem(BaseModel):
    plan_id: int = Field(..., description="ID")
    title: str = Field(..., description="标题")
    objective: str = Field(..., description="目标")

class GraphState(BaseModel):
     # 用户输入
    user_query: str

    # Planner 相关
    plans: List[PlanItem] = Field(default_factory=list)
    current_plan: Optional[PlanItem] = None          # 本轮总体计划
    plans_md: Optional[str] = None
    current_plan_id: Optional[int] = None
    plan_history: List[str] = Field(default_factory=list)
    history_feedback: List[Optional[Dict[str, Any]]] = Field(default_factory=list) #assign返回的历史计划，不包括最新的

    # Assign 相关
    assign_max_steps :ClassVar[int] = 3
    assign_step: int = 0
    last_tool_result: Optional[Dict[str, Any]] = None
    #agent_results: Dict[str, Any] = Field(default_factory=dict)
    assign_history: Optional[Dict[str, Any]] = Field(default_factory=dict)
    last_assign_history: Optional[Dict[str, Any]] = None
    overall_summary: Optional[str] = None
    
    # 任务执行
    current_task: Optional[Task] = None
    tasks: List[Task] = Field(default_factory=list)
    current_task_id: Optional[str] = None
    pending_queue: deque[str] = Field(default_factory=deque)
    # Memory
    public_memory: Dict[str, Any] = Field(default_factory=dict)

    # 控制
    round: int = 0
    finished: bool = False

    # 人类在环
    need_user_confirm: bool = True
    user_confirmed: bool = False
    user_feedback: Optional[str] = None
    
    # 前端展示
    report_path: Optional[str] = None
