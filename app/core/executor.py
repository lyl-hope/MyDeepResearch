from app.graph.state import GraphState
from app.core import registry
import re, json



class ExecutorAgent:
    def __init__(self):
        self.registry = registry


    def run(self, state: GraphState) -> GraphState:
        # # 1. 如果当前没有任务，从队列取一个
        # if state.current_task_id is None:
        #     if not state.pending_queue:
        #         print("\nExecutor: 没有待执行任务，返回 Planner")
        #         return state

        #     state.current_task_id = state.pending_queue.popleft()

        # 2. 定位任务
        #task = next(t for t in state.tasks if t.id == state.current_task_id)
        task = state.current_task
        agent_name = task.agent
        agent = self.registry.get(agent_name)

        print(f"\nExecutor: 使用 [{agent_name}] 执行任务：{task.content}")

        # 3. 标记 running
        task.status = "running"

        # 4. 执行
        try:
            result = agent.run(task, state)

            # 5. 写入历史
            memory_key = f"Assign Round {state.assign_step}"
            print("Executor memory_key",memory_key)
            # state.public_memory[memory_key] = {
            #     "task": task.content,
            #     "agent": agent_name,
            #     "result": result,
            # }
            state.assign_history[memory_key]["tool_result"] = result
            plan_key = f'Plan: {state.current_plan}'
            state.history_feedback.append({
                plan_key: result
            })
            task.status = "done"
            
            #6.reportpath写入
            match = re.search(r"\{.*\}", result, re.S)
            if not match:
                return

            try:
                data = json.loads(match.group())
            except json.JSONDecodeError:
                return

            if isinstance(data, dict) and "report_path" in data:
                state.report_path = data["report_path"]
            
            print(f"Executor: 任务完成 -> {task.content}")

        except Exception as e:
            task.status = "failed"
            print(f"Executor: Agent [{agent_name}] 执行失败: {e}")
            raise e

        # 6. 清空 current，下一轮取新任务
        #state.current_task_id = None

        return state