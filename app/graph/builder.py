from langgraph.graph import StateGraph, END
from app.graph.state import GraphState
from app.core.planner import PlannerAgent
from app.core.assign import AssignAgent
from app.core import ExecutorAgent,ConfirmNode
from app.core import build_registry
from app.graph.router import assign_router
def build_graph():
    graph = StateGraph(GraphState)
    AGENT_REGISTRY = build_registry()
    # 实例化
    planner = PlannerAgent()
    assign = AssignAgent()
    executor = ExecutorAgent()
    confirm = ConfirmNode()

    graph.add_node("planner", planner.run)   # 负责生成计划 & 判断下一步
    graph.add_node("assign", assign.run)     # 拆当前 step，选 agent
    graph.add_node("confirm", confirm)
    graph.add_node("executor", executor.run)  #统一的executor
    
    graph.set_entry_point("planner")

    # graph.add_conditional_edges(
    #     "planner",
    #     lambda s: "confirm" if s.need_user_confirm else "assign",
    #     {
    #         "confirm": END,
    #         "assign": "assign",
    #     }
    # )

        # ===== Planner 路由 =====
    def planner_router(state: GraphState):
        # 需要用户确认
        if state.need_user_confirm and not state.user_confirmed:
            return "end"

        # 全部计划完成
        if state.finished:
            return "end"

        # 进入 assign 拆解当前 plan step
        return "assign"

    graph.add_conditional_edges(
        "planner",
        planner_router,
        {
            "confirm": "confirm",
            "assign": "assign",
            "end": END,
        }
    )

    # confirm 完成后回 planner
    graph.add_edge("confirm", "planner")

    # ===== Assign → Executor =====
    # assign 只负责生成 tasks 并选定 current_task_id
    #graph.add_edge("assign", "executor")

    # # ===== Executor 执行完成后的路由（核心循环）=====
    # def executor_done_router(state: GraphState):
    #     # 还有未完成 task → 继续 executor（通过 assign 决定下一个）
    #     if state.pending_queue:
    #         return "executor"

    #     # 本 plan step 的所有 task 已完成 → 回 planner 生成下一步
    #     return "planner"

    # graph.add_conditional_edges(
    #     "executor",
    #     executor_done_router,
    #     {
    #         "executor": "executor",
    #         "planner": "planner",
    #     }
    # )
    graph.add_conditional_edges(
        "assign",
        assign_router,
        {
            "search": "executor",
            "shell": "executor",
            "code": "executor",
            "report": "executor",
            "webpageGeneration": "executor",
            "planner": "planner",
        }
    )
    
    graph.add_edge("executor", "assign")
    return graph.compile()