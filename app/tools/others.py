import re
import json

def extract_tool_block(text: str) -> dict:
    """
        识别<tool>,转为json
    """
    pattern = r"<tool>\s*(\{.*?\})\s*</tool>"
    match = re.search(pattern, text, re.S)
    if not match:
        raise ValueError("No <tool> JSON block found")

    json_str = match.group(1)
    return json.loads(json_str)
def parse_llm_output(text: str):
    """
    {
        'think': '- 还缺少用户输入的文件路径\n- 下一步子任务：获取文件路径\n- Agent: UserAgent',
        'tool': {
            'function': 'search',
            'parameters': {
            'query': 'python 正则 解析'
            }
        }
    }
    """
    think_pattern = re.compile(r"<think>(.*?)</think>", re.S)
    tool_pattern = re.compile(r"<tool>(.*?)</tool>", re.S)

    think_match = think_pattern.search(text)
    tool_match = tool_pattern.search(text)

    think_content = think_match.group(1).strip() if think_match else None
    tool_raw = tool_match.group(1).strip() if tool_match else None

    tool_json = None
    if tool_raw:
        try:
            tool_json = json.loads(tool_raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"Tool JSON 解析失败: {e}\n解析内容:\n{tool_raw}\n\n 原始内容:\n{text}")

    return {
        "think": think_content,
        "tool": tool_json
    }
