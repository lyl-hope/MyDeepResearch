from app.config.model import get_llm
from app.graph.state import GraphState, Task
from app.agents.base import BaseAgent
from langchain.agents.middleware import ShellToolMiddleware, DockerExecutionPolicy
from app.tools import DockerMountExecutionPolicy
from langchain.agents import create_agent
from langchain_core.callbacks.base import BaseCallbackHandler


class DebugHandler(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, **kwargs):
        print("▶️ LLM Start:", prompts)

    def on_llm_end(self, response, **kwargs):
        print("✅ LLM End:", response)

    def on_agent_action(self, action, **kwargs):
        print("🛠️ Agent Action:", action)

    def on_tool_start(self, tool, input_str, **kwargs):
        print(f"🔧 Tool {tool.name} start: {input_str}")

    def on_tool_end(self, tool, output, **kwargs):
        print(f"🔧 Tool {tool.name} end:", output)
class ShellAgent(BaseAgent):
    name = "shell"

    def __init__(self):
        # ---- 初始化 LLM ----
        llm = get_llm()

        # ---- 配置 Docker 执行策略（隔离） ----
        docker_policy = DockerMountExecutionPolicy(
            host_workspace="/data/lyl/DeepResearch/workspace",  # 主机路径
            container_workspace="/tmp/workspace",  # 容器内路径
            image="python:3.11-slim",
            command_timeout=60.0,
        )

        # ---- Shell 中间件 ----
        shell_middleware = ShellToolMiddleware(
            workspace_root="/tmp/workspace",
            execution_policy=docker_policy,
        )

        # ---- 创建 agent（无额外工具，只依赖 Shell） ----
        self.agent = create_agent(
            model=llm,
            tools=[],  # 不需要额外 Tools
            middleware=[shell_middleware],
            debug=True
        )

        # ---- Agent 运行提示 ----
        self.system_prompt = """
你是一个 Shell 操作 Agent。
你能：
- 执行 shell 命令
- 在 /workspace 目录下处理文件、运行脚本
规则：
1. 只执行用户意图明确的命令
2. 不要执行破坏宿主环境的命令
3. 输出尽量简洁清晰
"""

    def run(self, task: Task, state: GraphState) -> str:
        print(f"🖥️ ShellAgent 执行命令: {task.content}")

        try:
            response = self.agent.invoke(
                {
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": task.content},
                    ]
                },
                {
                    "recursion_limit": 5,
                },
            )
        except Exception as e:
            raise RuntimeError(f"ShellAgent 执行失败: {e}")

        if isinstance(response, dict) and "messages" in response:
            out_text = response["messages"][-1].content
        else:
            out_text = str(response)

        return out_text