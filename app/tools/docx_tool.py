# app/tools/save_docx_tool.py

import os
import uuid
from langchain.tools import BaseTool
from docx import Document

OUTPUT_DIR = "workspace/outputs"


class SaveDocxTool(BaseTool):
    name : str = "save_docx"
    description :str = (
        "将给定的报告内容保存为 Word (.docx) 文件。"
        "输入为纯文本或 Markdown 文本。"
        "输出为生成的 Word 文件路径。"
    )

    def _run(self, content: str) -> str:
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        filename = f"report_{uuid.uuid4().hex[:8]}.docx"
        path = os.path.join(OUTPUT_DIR, filename)

        doc = Document()
        for line in content.split("\n"):
            doc.add_paragraph(line)

        doc.save(path)

        return f"Word 报告已生成：{path}"

    async def _arun(self, content: str) -> str:
        raise NotImplementedError("save_docx 不支持异步")
