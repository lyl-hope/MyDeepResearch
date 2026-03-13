import subprocess
import uuid
import os
from pathlib import Path
from langchain.tools import BaseTool

TIMEOUT = 12  # 秒
WORKSPACE = "/data/lyl/DeepResearch/workspace/code"

# 确保存在工作目录
os.makedirs(WORKSPACE, exist_ok=True)

class ExecCodeTool(BaseTool):
    name :str = "exec_code"
    description :str = (
        "执行 Python 代码片段。"
        "输入为 Python 代码 (str)，工具会在隔离的临时文件中执行它，"
        "并收集所有生成的输出文件路径（如图表 png/svg/pdf）。\n"
        "返回格式统一包含 'stdout' and 'files'."
    )

    def _run(self, code: str) -> str:
        # 写代码到临时文件
        script_path = os.path.join(WORKSPACE, f"script_{uuid.uuid4().hex[:8]}.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)

        try:
            result = subprocess.run(
                ["python3", script_path],
                capture_output=True,
                text=True,
                timeout=TIMEOUT,
            )
            stdout = result.stdout
            stderr = result.stderr

        except subprocess.TimeoutExpired:
            return f"Error: 代码执行超时 (>{TIMEOUT}s)"

        # 收集生成的图表 / 文件
        generated_files = []
        for ext in ["png", "svg", "pdf", "jpg", "jpeg"]:
            for p in Path(WORKSPACE).glob(f"*.{ext}"):
                generated_files.append(str(p))

        # 输出结果结构
        return {
            "stdout": stdout.strip(),
            "stderr": stderr.strip(),
            "files": generated_files,
        }

    async def _arun(self, code: str) -> str:
        raise NotImplementedError("exec_code only supports synchronous")
