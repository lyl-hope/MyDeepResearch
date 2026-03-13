import gradio as gr
from dotenv import load_dotenv
load_dotenv()


from app.graph import build_graph
from app.graph.state import GraphState
from app.core import build_registry

graph = build_graph()

# 简单会话状态（单用户 demo 足够用）
SESSION = {
    "state": None,
    "running": False,
}

def submit_query(user_query):
    """
    第一次提交：只跑到 planner -> confirm
    """
    state = GraphState(user_query=user_query)
    result = graph.invoke(state)
    SESSION["state"] = result
    print("Planner 输出的 state：", result)
    plan_md = result["plans_md"] or "（Planner 未输出 plans_md）"
    status = f"⏸ 已生成计划，等待确认 "
    return plan_md, status


def revise_plan(feedback):
    """
    用户不满意当前计划 → 打回 planner 重写（再次需要确认）
    """
    state = SESSION["state"]
    if not state:
        return "⚠️ 请先提交问题", ""

    state["user_feedback"] = feedback
    state['need_user_confirm'] = True
    state["user_confirmed"] = False

    new_state = graph.invoke(state)
    SESSION["state"] = new_state

    plan_md = new_state["plans_md"] or "（Planner 未输出 plans_md）"
    status = f"🔁 已根据反馈重写计划 "
    return plan_md, status

def confirm_and_run():
    """
    用户确认 → graph 自动执行（stream）- 实时刷新日志（Markdown）
    """
    state = SESSION["state"]
    if not state:
        yield "**错误**：请先提交问题"
        return

    state["user_confirmed"] = True
    state["need_user_confirm"] = False

    logs = []
    last_state = None

    logs.append("## 执行开始")
    yield "\n\n".join(logs)

    for event in graph.stream(state):
        for node, s in event.items():
            last_state = s

            # planner 节点：显示一次当前计划
            if node == "planner":
                logs.append(f"### 进入节点：{node}")
                if s.get("current_plan"):
                    logs.append("**当前计划：**")
                    logs.append(f"- {s['current_plan'].title}")

            # assign 节点：如果 overallsummary 不为空，显示本次日志
            elif node == "assign":
                logs.append(f"### 进入节点：{node}")
                summary = s.get("overall_summary")
                if summary:
                    logs.append("**本次执行摘要：**")
                    logs.append(summary)

            # 其他节点：只显示进入了哪个节点
            else:
                logs.append(f"### 进入节点：{node}")

            yield "\n\n".join(logs)

    if last_state:
        SESSION["state"] = last_state

    logs.append("## 执行结束")
    yield "\n\n".join(logs)

# def confirm_and_run():
#     """
#     用户确认 → graph 自动执行（stream）- 实时刷新日志
#     """
#     state = SESSION["state"]
#     if not state:
#         yield "⚠️ 请先提交问题"
#         return

#     state['user_confirmed'] = True
#     state['need_user_confirm'] = False

#     logs = []
#     last_state = None

#     yield "🚀 开始执行...\n"

#     for event in graph.stream(state):
#         for node, s in event.items():
#             last_state = s
#             logs.append(f"➡️ 进入节点: {node}")
#             if s.get("current_plan"):
#                 logs.append(f"   📌 当前计划: {s['current_plan'].title}")
#             logs.append(f"   🔁 Round: {s['round']}")
#             logs.append("-" * 30)

#             # ⭐ 每一步 yield，一刷新 UI
#             yield "\n".join(logs)

#     if last_state:
#         SESSION["state"] = last_state

#     yield "\n".join(logs) + "\n✅ 执行完成"


def continue_run():
    """
    后续轮次：无需确认，直接让 graph 继续跑
    """
    state = SESSION["state"]
    if not state:
        return "⚠️ 尚无会话状态"

    logs = []
    last_state = None

    for event in graph.stream(state):
        for node, s in event.items():
            last_state = s
            logs.append(f"➡️ 进入节点: {node}")
            if s.current_plan:
                logs.append(f"   📌 当前计划: {s.current_plan.title}")
            logs.append(f"   🔁 Round: {s.round}")
            logs.append("-" * 30)

    if last_state:
        SESSION["state"] = last_state

    return "\n".join(logs)


with gr.Blocks(title="LangGraph 可视化前端 Demo") as demo:
    gr.Markdown("# 🧠 LangGraph 可视化前端 Demo")
    gr.Markdown("**流程：生成计划 → 用户确认 → 自动执行 → 可随时打回修改计划**")

    with gr.Row():
        user_input = gr.Textbox(label="用户需求", placeholder="请输入你的任务需求…")
        submit_btn = gr.Button("🧩 生成计划")

    plans_md = gr.Markdown(label="📋 当前计划（Planner 输出）")

    feedback = gr.Textbox(
        label="✏️ 对当前计划的反馈（不满意时填写）",
        placeholder="例如：步骤太粗了，请拆细一点…"
    )

    with gr.Row():
        revise_btn = gr.Button("🔁 打回重写计划")
        confirm_btn = gr.Button("✅ 确认并开始执行")
        continue_btn = gr.Button("▶️ 继续执行下一轮")

    logs = gr.Textbox(label="🧭 执行日志 / 当前节点", lines=18)

    submit_btn.click(
        submit_query,
        inputs=user_input,
        outputs=[plans_md, logs]
    )

    revise_btn.click(
        revise_plan,
        inputs=feedback,
        outputs=[plans_md, logs]
    )

    confirm_btn.click(
        confirm_and_run,
        outputs=logs
    )

    continue_btn.click(
        continue_run,
        outputs=logs
    )

demo.launch(server_name="0.0.0.0", server_port=7888)