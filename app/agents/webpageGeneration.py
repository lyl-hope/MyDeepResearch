from langchain.agents import create_agent
from app.config.model import get_llm
from app.agents.base import BaseAgent
from app.graph.state import Task, GraphState

from app.tools.html_tool import SaveHTMLTool


class WebpageGenerationAgent(BaseAgent):
    name = "webpage"

    def __init__(self):
        llm = get_llm()

        tools = [
            SaveHTMLTool(),
        ]

        self.agent = create_agent(
            model=llm,
            tools=tools,
        )

        self.system_prompt = """
你是一个网页生成 Agent。

你的职责是：
1. 根据给定任务和上下文信息生成一个完整 HTML 页面
2. 页面应结构清晰、美观、可直接在浏览器中打开
3. 使用内联 CSS 或 <style> 标签提供基础样式
4. 内容必须基于已知上下文，不要编造事实
5. 生成完成后，调用 save_html 工具保存页面

规则：
- 必须输出完整 HTML 文本（包含 <html> <head> <body>）
- 默认语言：中文
- 页面应包含标题、若干小节、要点列表
- 默认风格：简洁、现代、可读性强
- 不要在最终回复中直接输出 HTML
- 只通过工具保存 HTML 文件
"""

    def run(self, task: Task, state: GraphState) -> str:
        print(f"WebpageAgent: 生成网页 -> {task.content}")

        # 拼上下文
        memory_text = "\n".join(
            [f"{k}: {v}" for k, v in state.public_memory.items()]
        )

        user_prompt = f"""
任务：
{task.content}

可用上下文信息：
{memory_text if memory_text else "暂无"}

请生成一个网页并保存为 HTML 文件。
"""

        result = self.agent.invoke(
            {
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt},
                ]
            }
        )

        if isinstance(result, dict):
            return result.get("output", str(result))
        else:
            return str(result)