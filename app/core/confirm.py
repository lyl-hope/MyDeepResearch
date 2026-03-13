from app.graph.state import GraphState
class ConfirmNode:
    name = "confirm"

    def __call__(self, state: GraphState) -> GraphState:
        state.current_node = "confirm"

        # 如果用户已经点了确认
        if state.user_confirmed:
            state.has_confirmed_once = True

        return state