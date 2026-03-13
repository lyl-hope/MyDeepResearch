import gradio as gr
from dotenv import load_dotenv
load_dotenv()


from app.graph import build_graph
from app.graph.state import GraphState
from app.core import build_registry

from pathlib import Path
graph = build_graph()
SESSION = {
    "state": None,
    "running": False,
}

def submit_query(user_query, history):

    if SESSION["running"]:
        return history

    history = history or []

    state = GraphState(user_query=user_query)
    history.append({
        "role": "user",
        "content": user_query
    })
    history.append({
        "role": "assistant",
        "content": "正在生成计划..."
    })
    yield history
    result = graph.invoke(state)
    SESSION["state"] = result

    plan_md = result.get("plans_md", "未生成计划")

    
    history[-1] = ({
        "role": "assistant",
        "content": f"### 已生成计划\n\n{plan_md}\n\n如需修改请输入修改意见，否则点击开始执行。"
    })

    yield history


def revise_plan(feedback, history):

    if SESSION["running"]:
        return history

    state = SESSION["state"]
    if not state:
        return history

    state["user_feedback"] = feedback
    state["need_user_confirm"] = True
    state["user_confirmed"] = False
    history.append({
            "role": "user",
            "content": feedback
        })
    yield history
    new_state = graph.invoke(state)
    SESSION["state"] = new_state

    plan_md = new_state.get("plans_md", "未生成计划")

    

    history.append({
        "role": "assistant",
        "content": f"### 已根据反馈重写计划\n\n{plan_md}\n\n是否开始执行？"
    })

    yield history

timeline_steps = []
def confirm_and_run(history, timeline_html):

    if SESSION["running"]:
        yield history, timeline_html
        return

    SESSION["running"] = True

    state = SESSION["state"]
    state["user_confirmed"] = True
    state["need_user_confirm"] = False

    thinking_log = ""
    timeline_steps = []

    history.append({
        "role": "user",
        "content": "开始执行"
    })

    history.append({
        "role": "assistant",
        "content": "正在执行..."
    })

    yield history, render_timeline(timeline_steps, -1)

    last_state = None

    for event in graph.stream(state):

        for node, s in event.items():

            last_state = s
            
            # -------- planner ----------
            if node == "planner":

                title = s.get("current_plan")

                if title:
                    step = f"Planner: {title.title}"
                    timeline_steps.append(step)

            # -------- assign ----------
            elif node == "assign":
                title = s.get("current_task").title
                status =s.get("current_task").status
                summary = s.get("overall_summary")

                if status=='todo':
                    step = f"Assign: 执行任务 {title}"
                    timeline_steps.append(step)
                else:
                    step = f"Assign: 任务总结 {summary}"
                    timeline_steps.append(step)

            # -------- tool ----------
            else:
                agent = s.get("current_task").agent
                step = f"Tool: {agent}"
                timeline_steps.append(step)

            history[-1] = {
                "role": "assistant",
                "content": "正在执行..."
            }

            yield history, render_timeline(timeline_steps, len(timeline_steps)-1)

    if last_state:
        SESSION["state"] = last_state

    report_path = last_state.get("report_path")

    if report_path and Path(report_path).exists():

        # with open(report_path, "r", encoding="utf-8") as f:
        #     report_md = f.read()

        # history[-1]=({
        #     "role": "assistant",
        #     "content": f"""
        # ### 最终报告

        # <div class="download-box">

        # 报告已生成  
        # 点击下载 Markdown 文件

        # <a href="file={report_path}" download class="download-btn">
        # ⬇ 下载报告
        # </a>

        # </div>

        # ---

        # {report_md}
        # """
        # })
        history[-1]=({
        "role": "assistant",
        "content": "研究完成，生成报告。"
        })
        query = s['user_query']
        history.append({
            "role": "assistant",
            "content": {
                "path": report_path,
                "alt_text": f'执行报告： {query} '
            }
        })
    else:
        history[-1] = {
                    "role": "assistant",
                    "content": "Error！执行失败！"
                }
    SESSION["running"] = False

    yield history, render_timeline(timeline_steps, len(timeline_steps))

# def confirm_and_run(history):

#     if SESSION["running"]:
#         yield history
#         return

#     SESSION["running"] = True

#     state = SESSION["state"]
#     state["user_confirmed"] = True
#     state["need_user_confirm"] = False

#     thinking_log = ""

#     history.append({
#         "role": "user",
#         "content": '开始执行'
#     })
#     history.append({
#         "role": "assistant",
#         "content": "正在执行...\n\n<details><summary>思考过程</summary>\n\n...</details>"
#     })

#     yield history

#     last_state = None

#     for event in graph.stream(state):
#         for node, s in event.items():
#             last_state = s

#             if node == "planner":
#                 if s.get("current_plan"):
#                     thinking_log += f"\n[planner] 当前计划：{s['current_plan'].title}\n"

#             elif node == "assign":
#                 summary = s.get("overallsummary")
#                 if summary:
#                     thinking_log += f"\n[assign] 执行摘要：\n{summary}\n"

#             else:
#                 thinking_log += f"\n进入节点：{node}\n"

#             history[-1] = {
#                 "role": "assistant",
#                 "content": f"正在执行...\n\n<details open><summary>思考过程</summary>\n\n{thinking_log}\n</details>"
#             }

#             yield history

#     if last_state:
#         SESSION["state"] = last_state

#     report_path = last_state.get("report_path")

#     if report_path and Path(report_path).exists():
#         with open(report_path, "r", encoding="utf-8") as f:
#             report_md = f.read()

#         history.append({
#             "role": "assistant",
#             "content": f"## 最终报告\n\n{report_md}"
#         })

#     SESSION["running"] = False
#     yield history


def clear_all():
    SESSION["state"] = None
    SESSION["running"] = False
    return []
def render_timeline(steps, active_index):

    html = """
    <div class="timeline-title">执行进度</div>
    <div class="timeline">
    """

    for i, step in enumerate(steps):

        cls = ""

        if i < active_index:
            cls = "done"
        elif i == active_index:
            cls = "active"

        html += f"""
        <div class="step {cls}">
            <div class="dot"></div>
            <span>{step}</span>
        </div>
        """

    html += "</div>"

    return html
# css = """
# .gr-chatbot {
#     font-family: "Inter", system-ui, sans-serif;
#     font-size: 15px;
# }
# """
# with gr.Blocks(css=css) as demo:

#     with gr.Row():

#         with gr.Column(scale=1):
#             gr.Markdown("## 任务控制")

#             user_input = gr.Textbox(
#                 placeholder="请输入研究目标...",
#                 lines=4
#             )

#             feedback = gr.Textbox(
#                 placeholder="如需修改计划，在此输入...",
#                 lines=3
#             )

#             submit_btn = gr.Button("生成计划")
#             revise_btn = gr.Button("修改计划")
#             confirm_btn = gr.Button("开始执行")
#             clear_btn = gr.Button("清空会话")

#         with gr.Column(scale=3):
#             chatbot = gr.Chatbot(height=720,avatar_images=("assets/user.png", "assets/bot.png"))

#     submit_btn.click(
#         submit_query,
#         inputs=[user_input, chatbot],
#         outputs=chatbot
#     )

#     revise_btn.click(
#         revise_plan,
#         inputs=[feedback, chatbot],
#         outputs=chatbot
#     )

#     confirm_btn.click(
#         confirm_and_run,
#         inputs=chatbot,
#         outputs=chatbot
#     )

#     clear_btn.click(clear_all, outputs=chatbot)

css = """
.gr-chatbot {
    font-family: "Inter", system-ui, sans-serif;
    font-size: 13px;
    line-height:1.5;
}
.message {
    padding:6px 10px !important;
    border-radius:10px !important;
}
.message-wrap {
    max-width: 90%;
}
.timeline {
    border-left: 3px solid #e5e7eb;
    margin-left: 10px;
    padding-left: 20px;
}

.step {
    position: relative;
    margin-bottom: 18px;
    font-size: 14px;
}

.step .dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #d1d5db;
    position: absolute;
    left: -26px;
    top: 4px;
}

.step.done .dot {
    background: #22c55e;
}

.step.active .dot {
    background: #3b82f6;
    box-shadow: 0 0 8px #3b82f6;
}

.step span {
    color: #374151;
}

.timeline-title{
    font-weight:600;
    margin-bottom:10px;
}
.download-box {
    border:1px solid #e5e7eb;
    border-radius:10px;
    padding:12px;
    background:#f9fafb;
    margin:10px 0;
}

.download-btn {
    display:inline-block;
    margin-top:8px;
    padding:6px 12px;
    background:#3b82f6;
    color:white;
    border-radius:6px;
    text-decoration:none;
    font-size:13px;
}

.download-btn:hover {
    background:#2563eb;
}
button {
    border-radius:8px !important;
    font-size:13px !important;
    padding:8px 14px !important;
    transition:all 0.2s;
}

/* 生成计划 */

.btn-primary button{
    background:#3b82f6 !important;
    color:white !important;
}

.btn-primary button:hover{
    background:#2563eb !important;
}

/* 修改计划 */

.btn-secondary button{
    background:#e5e7eb !important;
    color:#374151 !important;
}

.btn-secondary button:hover{
    background:#d1d5db !important;
}

/* 开始执行 */

.btn-run button{
    background:#22c55e !important;
    color:white !important;
    font-weight:600;
}

.btn-run button:hover{
    background:#16a34a !important;
}

/* 清空 */

.btn-clear button{
    background:#ef4444 !important;
    color:white !important;
}

.btn-clear button:hover{
    background:#dc2626 !important;
}
"""
with gr.Blocks() as demo:

    with gr.Row():

        # 左侧控制
        with gr.Column(scale=1):
            gr.Markdown("## 任务控制")

            user_input = gr.Textbox(
                label="研究任务",
                placeholder="请输入研究目标...",
                lines=4
            )

            feedback = gr.Textbox(
                label="修改计划",
                placeholder="如需修改计划，在此输入...",
                lines=3
            )

            submit_btn = gr.Button("生成计划", elem_classes="btn-primary")
            revise_btn = gr.Button("修改计划", elem_classes="btn-secondary")
            confirm_btn = gr.Button("开始执行", elem_classes="btn-run")
            clear_btn = gr.Button("清空会话", elem_classes="btn-clear")

        # 中间聊天
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                height=720,
                avatar_images=("assets/user.png", "assets/bot.png")
            )

        # 右侧timeline
        with gr.Column(scale=1):
            timeline = gr.HTML()
    submit_btn.click(
        submit_query,
        inputs=[user_input, chatbot],
        outputs=chatbot
    )

    revise_btn.click(
        revise_plan,
        inputs=[feedback, chatbot],
        outputs=chatbot
    )

    confirm_btn.click(
    confirm_and_run,
    inputs=[chatbot, timeline],
    outputs=[chatbot, timeline]
    )

    clear_btn.click(clear_all, outputs=chatbot)

demo.launch(server_name="0.0.0.0", server_port=7888,css=css)