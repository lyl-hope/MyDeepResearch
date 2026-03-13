from jinja2 import Environment, FileSystemLoader, StrictUndefined
from datetime import datetime


def render_jinja_prompt(
    context: dict,
    template_name: str,
    template_dir: str = "./prompts",
) -> str:
    """
    渲染 Jinja2 prompt 模板
    :param context: 渲染上下文（dict / json）
    :param template_name: 模板文件名，如 'search.jinja2'
    :return: 渲染后的字符串
    """

    # # 自动补充时间（如果模板需要）
    # if auto_add_utc_time and "current_datetime_utc" not in context:
    #     context["current_datetime_utc"] = datetime.utcnow().isoformat() + "Z"

    env = Environment(
        loader=FileSystemLoader(template_dir),
        undefined=StrictUndefined,  # 未定义变量直接报错
        trim_blocks=True,
        lstrip_blocks=True,
    )

    template = env.get_template(template_name)
    return template.render(context)
