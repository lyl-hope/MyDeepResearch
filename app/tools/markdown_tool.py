# app/tools/save_markdown_tool.py

import os
import uuid
from langchain.tools import BaseTool
from typing import Optional
OUTPUT_DIR = "workspace/outputs"


# class SaveMarkdownTool(BaseTool):
#     name :str = "save_markdown"
#     description : str= (
#         "将给定的报告内容保存为 Markdown 文件。"
#         "输入为完整 Markdown 文本。"
#         "输出为生成的文件路径。"
#     )

#     def _run(self, content: str) -> str:
#         os.makedirs(OUTPUT_DIR, exist_ok=True)

#         filename = f"report_{uuid.uuid4().hex[:8]}.md"
#         path = os.path.join(OUTPUT_DIR, filename)

#         with open(path, "w", encoding="utf-8") as f:
#             f.write(content)

#         return f"Markdown 报告已生成：{path}"

#     async def _arun(self, content: str) -> str:
#         raise NotImplementedError("save_markdown 不支持异步")
class SaveMarkdownTool(BaseTool):
    name: str = "save_markdown"
    description: str = (
        "将报告内容以 Markdown 形式保存到文件中，支持分段写入。"
        "输入参数包括：session_id（可选）、content（当前片段）、is_final（是否最后一段）。"
        "返回保存路径。"
    )

    def _run(
        self,
        content: str,
        session_id: Optional[str] = None,
        is_final: bool = False,
    ) -> str:
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        if session_id is None:
            session_id = uuid.uuid4().hex[:8]

        filename = f"report_{session_id}.md"
        path = os.path.join(OUTPUT_DIR, filename)

        # 追加写入（不会覆盖）
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)
            if not content.endswith("\n"):
                f.write("\n")

        if is_final:
            return f"Markdown 报告(session_id {session_id})已完成并保存：{path}"
        return f"Markdown(session_id {session_id}) 片段已追加：{path}"