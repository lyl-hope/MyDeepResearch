# app/agents/code_agent.py
from app.config.render_prompt import render_jinja_prompt
from langchain.agents import create_agent
from app.config.model import get_llm
from app.agents.base import BaseAgent
from app.graph.state import Task, GraphState

from app.tools.code_tool import ExecCodeTool

class CodeAgent(BaseAgent):
    name = "code"

    def __init__(self):
        llm = get_llm()

        tools = [
            ExecCodeTool(),
        ]

        self.agent = create_agent(
            model=llm,
            tools=tools,
        )

#         self.system_prompt = """
# 你是一个 Python 代码生成与执行 Agent。
# 任务可能涉及生成图表文件或数据处理。

# 要求：
# - 只输出代码调用工具语句，不要手动执行 print 图表,如果使用matplotlib画图，中文字体请用WenQuanYi Micro Hei
# - 不允许对没有来源的数据进行编造
# - 用 exec_code 工具执行 python 代码
# - 如果要生成文件，请写文件到 workspace/code
# - 执行完成后，请返回执行结果（stdout + file paths）
# """

    def run(self, task: Task, state: GraphState) -> str:
        print(f"CodeAgent: {task.content}")

#         memory_text = "\n".join(
#             [f"{k}: {v}" for k, v in state.public_memory.items()]
#         )

#         user_prompt = f"""
# 任务：
# {task.content}

# 当前已有上下文：
# {memory_text if memory_text else "无"}

# 请生成 Python 代码用于完成上述任务，并调用 exec_code 工具执行它。
# 只输出最终执行结果或文件路径列表即可。
# """
        render_context = {
            "user_query": state.user_query,
            "task_title": task.title,
            "task_content":task.content,
            "data": task.data,
            "user_feedback": state.user_feedback,
        }

        system_prompt = render_jinja_prompt(
            context=render_context,
            template_name="code.jinja2"
        )
        response = self.agent.invoke(
            {"messages": [
                {"role": "system", "content": system_prompt},
               # {"role": "user", "content": user_prompt},
            ]}
        )

        if isinstance(response, dict):
            return response.get("output") or str(response)
        return str(response)
