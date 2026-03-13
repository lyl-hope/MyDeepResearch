from jinja2 import Environment, FileSystemLoader, StrictUndefined
from datetime import datetime

# 1. 加载模板文件夹
env = Environment(
    loader=FileSystemLoader("./prompts"),
    undefined=StrictUndefined  # 未定义变量会报错，防止遗漏
)

# 2. 获取模板
template = env.get_template("search.jinja2")

# 3. 准备上下文数据
render_context = {
    "current_datetime_utc": datetime.utcnow().isoformat() + "Z",
    "conversation_history": [
        
    ]
}

# 4. 渲染
rendered_prompt = template.render(render_context)

print("=== Rendered Prompt ===")
print(rendered_prompt)