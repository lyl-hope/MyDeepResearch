from typing import Optional, List, Type
import os
import shlex
import subprocess

from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool


class ShellInput(BaseModel):
    command: str = Field(..., description="要执行的 shell 命令")


class SafeShellTool(BaseTool):
    name: str = "shell"
    description: str = "在受限 workspace 目录下执行安全的 shell 命令"
    args_schema: Type[BaseModel] = ShellInput

    # 给所有“运行时字段”提供默认值
    workspace_root: str = ""
    timeout: float = 60.0
    allowed_commands: List[str] = []
    block_keywords: List[str] = []

    def __init__(
        self,
        workspace_root: str,
        timeout: float = 60.0,
        allowed_commands: Optional[List[str]] = None,
        **kwargs,
    ):
        # 不要把这些字段交给 Pydantic 校验
        super().__init__(**kwargs)

        self.workspace_root = os.path.abspath(workspace_root)
        self.timeout = timeout

        self.allowed_commands = allowed_commands or [
            "ls", "cat", "pwd", "echo", "head", "tail",
            "wc", "grep", "find", "sed", "awk",
            "python", "pip", "pytest",
            "mkdir", "touch", "cp", "mv",
            "curl", "wget",
        ]

        self.block_keywords = [
            "rm -rf /",
            "rm -rf /*",
            "shutdown",
            "reboot",
            "mkfs",
            "dd if=",
            ":(){",
            "kill -9 1",
            "killall",
            "poweroff",
            "halt",
            "> /dev/sda",
        ]

    def _is_command_safe(self, command: str) -> None:
        cmd = command.strip().lower()

        for kw in self.block_keywords:
            if kw in cmd:
                raise RuntimeError(f"检测到危险指令关键字: {kw}")

        try:
            parts = shlex.split(command)
        except Exception:
            raise RuntimeError("命令解析失败（非法 shell 语法）")

        if not parts:
            raise RuntimeError("空命令")

        exe = parts[0]

        if exe not in self.allowed_commands:
            raise RuntimeError(
                f"不允许的命令: {exe}\n"
                f"仅允许: {', '.join(self.allowed_commands)}"
            )

        for p in parts[1:]:
            if ".." in p:
                raise RuntimeError("检测到路径逃逸: ..")

    def _run(self, command: str) -> str:
        self._is_command_safe(command)

        try:
            proc = subprocess.run(
                command,
                shell=True,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env={**os.environ, "PWD": self.workspace_root},
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("命令执行超时")

        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()

        if proc.returncode != 0:
            raise RuntimeError(
                f"命令执行失败 (code={proc.returncode})\n"
                f"{stderr or stdout}"
            )

        return stdout or "（无输出）"
