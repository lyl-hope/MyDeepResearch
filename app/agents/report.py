
from langchain.agents import create_agent
from app.config.model import get_llm
from app.agents.base import BaseAgent
from app.graph.state import Task, GraphState
from app.config.render_prompt import render_jinja_prompt
from app.tools.markdown_tool import SaveMarkdownTool
from app.tools.pdf_tool import SavePDFTool
from app.tools.docx_tool import SaveDocxTool


class ReportAgent(BaseAgent):
    name = "report"

    def __init__(self):
        llm = get_llm()

        tools = [
            SaveMarkdownTool(),
            SavePDFTool(),
            SaveDocxTool(),
        ]

        self.agent = create_agent(
            model=llm,
            tools=tools,
           # debug=True
        )

#         self.system_prompt = """
# 你是一个报告生成 Agent。

# 你的职责是：
# 1. 根据给定任务和上下文生成结构清晰的报告内容，有外部信息应当保留引用，不允许编造数据
# 2. 判断最合适的输出格式（markdown / pdf / docx）
# 3. 调用对应工具将报告保存为文件

# 规则：
# - 报告要有清晰结构（标题、小节、要点）
# - 内容应基于已获得信息，不要编造事实
# - 需要有来源出处及其网址内联
# - 默认优先使用 markdown
# - 如果用户明确要求 pdf 或 word，则使用对应工具
# - 保存成功后，只返回工具返回的文件路径说明
# """

    def run(self, task: Task, state: GraphState) -> str:
        print(f"ReportAgent: 生成报告 -> {task.title}")

#         # 把 memory 拼成上下文
#         memory_text = "\n".join(
#             [f"{k}: {v}" for k, v in state.public_memory.items()]
#         )

#         user_prompt = f"""
# 任务：
# {task.content}

# 可用上下文信息：
# {memory_text if memory_text else "暂无"}

# 请生成最终报告并保存为文件。
# """

        render_context = {
            "user_query": state.user_query,
            "plans": state.plans,
            "plan_md":state.plans_md,
            "history_feedback": state.history_feedback,
            "user_feedback": state.user_feedback,
        }
        
        system_prompt = render_jinja_prompt(
            context=render_context,
            template_name="report.jinja2"
        )
        #print("Report System Prompt:" ,system_prompt )
        response = self.agent.invoke(
            {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    #{"role": "user", "content": user_prompt},
                ]
            }
        )

        # 取 output
        if isinstance(response, dict) and "messages" in response:
            out_text = response["messages"][-1].content
        else:
            out_text = str(response)
        print(f"Report Agent 最后输出：{out_text}")
        return out_text   
