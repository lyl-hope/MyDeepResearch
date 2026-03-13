from app.graph.state import GraphState
def assign_router(state: GraphState):
    #这里补一个解析
    fn = state.last_tool_result["function"]
    print("last_tool_result",fn)
    if fn == "taskdone":
        return "planner"

    if state.assign_step >= state.assign_max_steps:
        return "planner"   # 强制终止回 Planner
    print("assign_router返回",fn)
    return fn

def executor_router(state: GraphState) -> str:
    if state.finished:
        return "end"

    return state.current_agent or "default"
