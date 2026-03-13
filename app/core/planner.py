from app.graph.state import GraphState,PlanItem
from app.config.model import get_llm
from app.config.render_prompt import render_jinja_prompt
import json
class PlannerAgent:
    def __init__(self):
        self.llm = get_llm()

    def run(self, state: GraphState) -> GraphState:
        """
        根据当前状态 + memory + 已完成结果，生成下一步计划
        """
        print(f"\nPlanner Round {state.round}")

        history_text = "\n".join(state.plan_history[-3:])

        memory_text = "\n".join(
            [f"{k}: {v}" for k, v in state.public_memory.items()]
        )

        #   system prompt

#         system_prompt = """
# 你是一个多步骤任务规划控制器（Planner Agent）。

# 你的职责是：
# - 根据用户最终目标、历史计划和已获得的信息
# - 判断当前任务是否已经完成
# - 如果未完成，只输出“当前最重要的下一步计划”，一句话即可

# 规则：
# 1. 如果你认为目标已经完成，只输出：DONE
# 2. 如果未完成，只输出一句“下一步要做的事”，不要解释，不要列出多步
# 3. 每一轮只能给出一步计划
# 4. 不要重复历史中已经完成的步骤
# 5. 不要输出多余文字、序号或标点说明
# """

#         #   user prompt（当前上下文）
#         user_prompt = f"""
# 用户最终目标：
# {state.user_query}

# 历史计划：
# {history_text if history_text else "无"}

# 已获得的信息：
# {memory_text if memory_text else "暂无"}

# 请基于以上信息判断当前状态，并给出结果。
# """
        render_context = {
            "user_query": state.user_query,
            "existing_plan": state.plans,
            "current_plan":state.current_plan,
            "history_feedback": state.history_feedback,
            "last_assign_history": state.last_assign_history,
            "user_feedback": state.user_feedback,
        }
        print("Planner history_feedback:",state.history_feedback)
        system_prompt = render_jinja_prompt(
            context=render_context,
            template_name="planner.jinja2"
        )
        #print("System: ",system_prompt)
        messages = [
            {"role": "system", "content": system_prompt.strip()}
            # {"role": "user", "content": user_prompt.strip()},
        ]

        resp = self.llm.invoke(messages)
        plan_text = resp.content.strip()

        # # Done
        # if plan_text.upper().startswith("DONE"):
        #     print("Planner 任务完成")
        #     state.finished = True
        #     return state

        # # Update
        # state.current_plan = plan_text
        # state.plan_history.append(plan_text)
        planner_output = json.loads(plan_text)
        print("Planner 输出：", planner_output)
        # ===== 结束 =====
        if planner_output["decision"] == 'terminate':
            print("Planner 任务完成")
            state.finished = True
            return state

        # ===== 更新 plan =====
        if planner_output["decision"] in ("new_plan", "revise_plan"):
            raw_plans = planner_output.get("plans", [])

            # ✅ dict -> PlanItem
            state.plans = [PlanItem(**p) for p in raw_plans]

            state.plans_md = planner_output.get("plans_md")

        # ===== 更新 current_plan =====
        current_plan_id = planner_output.get("current_plan_id")
        if current_plan_id is not None:
            state.current_plan_id = current_plan_id

            state.current_plan = next(
                (t for t in state.plans if t.plan_id == current_plan_id),
                None
            )

            if state.current_plan is None:
                raise ValueError(f"current_plan_id={current_plan_id} 不存在于 plans 中")
        state.round += 1

        print("当前计划：", state.current_plan)
        print("当前md: ",state.plans_md)
        # # ✅ 逻辑核心：
        # if not state.has_confirmed_once or state.user_feedback:
        #     # 第一次 or 被用户打回 → 要确认
        #     state.need_user_confirm = True
        #     state.user_confirmed = False
        # else:
        #     # 已经确认过 & 没有新的反馈 → 直接执行
        #     state.need_user_confirm = False
        #     state.user_confirmed = True

        # # 消费掉反馈
        # state.user_feedback = None
        return state
