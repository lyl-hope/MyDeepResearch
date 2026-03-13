import os
import uuid
from langchain.tools import BaseTool

OUTPUT_DIR = "workspace/outputs"


class SaveHTMLTool(BaseTool):
    name :str = "save_html"
    description : str  = (
        "将给定的 HTML 内容保存为网页文件。"
        "输入必须是完整 HTML 文本（包含 <html> <head> <body>）。"
        "输出为生成的 HTML 文件路径。"
    )

    def _run(self, content: str) -> str:
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        filename = f"page_{uuid.uuid4().hex[:8]}.html"
        path = os.path.join(OUTPUT_DIR, filename)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"HTML 页面已生成：{path}"

    async def _arun(self, content: str) -> str:
        raise NotImplementedError("save_html 不支持异步")
