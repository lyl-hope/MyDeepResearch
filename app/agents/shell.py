from app.graph.state import GraphState, Task
from app.agents.base import BaseAgent
from app.config.model import get_llm
from app.tools.shell_tool import SafeShellTool
from langchain.agents import create_agent
from app.config.render_prompt import render_jinja_prompt
from datetime import datetime

class ShellAgent(BaseAgent):
    name = "shell"
    description = "在受限目录中执行安全 Shell 命令"

    def __init__(self):
        # ---- 初始化 LLM ----
        llm = get_llm()

        # ---- workspace 根目录 ----
        self.workspace_root = "/data/lyl/DeepResearch"
        #os.makedirs(self.workspace_root, exist_ok=True)

        # ---- Shell Tool（无 Docker，带安全限制）----
        shell_tool = SafeShellTool(
            workspace_root=self.workspace_root,
            timeout=60.0,
            allowed_commands=[
                "ls", "cat", "pwd", "echo", "head", "tail",
                "wc", "grep", "find",
                "python", "pip", "pytest",
                "mkdir", "touch", "cp", "mv",
                "curl", "wget",
            ],
        )

        # ---- 创建 agent（通过 Tool 注入 shell 能力）----
        self.agent = create_agent(
            model=llm,
            tools=[shell_tool],
            debug=True,
        )

        # ---- Agent 运行提示 ----
#         self.system_prompt = f"""
# 你是一个 Shell 操作 Agent。
# 你可以通过 shell 工具在目录中执行命令：

# workspace: {self.workspace_root}

# 规则：
# 1. 只执行用户意图非常明确的命令
# 2. 只能操作 workspace 目录下的文件，路径请使用绝对路径
# 3. 禁止破坏性或高风险命令（rm -rf、mkfs、shutdown、cd 等）
# 4. 输出尽量简洁、可读
# 5. 如果命令被拒绝，解释原因
# """

    def run(self, task: Task, state: GraphState) -> str:
        print(f"ShellAgent 执行命令: {task.content}")

        render_context = {
            "current_datetime_utc": datetime.utcnow().isoformat() + "Z",
            "task_title": task.title,
            "task_content":task.content,
            "user_feedback": state.user_feedback,
        }

        system_prompt = render_jinja_prompt(
            context=render_context,
            template_name="shell.jinja2"
        )
        try:
            response = self.agent.invoke(
                {
                    "messages": [
                        {"role": "system", "content": system_prompt},
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
