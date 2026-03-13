# app/tools/save_pdf_tool.py

import os
import uuid
from langchain.tools import BaseTool
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

OUTPUT_DIR = "workspace/outputs"


class SavePDFTool(BaseTool):
    name :str = "save_pdf"
    description :str = (
        "将给定的报告内容保存为 PDF 文件。"
        "输入为纯文本或 Markdown 渲染后的文本。"
        "输出为生成的 PDF 文件路径。"
    )

    def _run(self, content: str) -> str:
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        filename = f"report_{uuid.uuid4().hex[:8]}.pdf"
        path = os.path.join(OUTPUT_DIR, filename)

        doc = SimpleDocTemplate(path, pagesize=A4)
        styles = getSampleStyleSheet()

        story = []
        for line in content.split("\n"):
            story.append(Paragraph(line, styles["Normal"]))
            story.append(Spacer(1, 6))

        doc.build(story)

        return f"PDF 报告已生成：{path}"

    async def _arun(self, content: str) -> str:
        raise NotImplementedError("save_pdf 不支持异步")
