import os
import requests
from langchain.tools import tool

def bocha_search(query: str, max_results: int = 5) -> dict:
    """
    调用博查 AI Search API（国内结构化搜索），返回 JSON
    """
    url = "https://api.bocha.cn/v1/web-search"  
    api_key = os.getenv("BOCHA_API_KEY")
    if not api_key:
        raise ValueError("BOCHA_API_KEY 未设置")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    body = {
        "query": query,
        "count": max_results,
    }

    resp = requests.post(url, json=body, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()

def extract_bocha_webpages(raw: dict) -> list[dict]:
    pages = raw.get("data", {}) \
               .get("webPages", {}) \
               .get("value", [])

    results = []
    for p in pages:
        results.append({
            "title": p.get("name"),
            "url": p.get("url"),
            "snippet": p.get("snippet"),
            "site": p.get("siteName"),
            "date": p.get("datePublished"),
        })
    return results


def jina_reader_toolssssss(url: str, max_chars: int = 6000) -> dict:
    """
    使用 jina.ai 抽取网页正文，并做长度控制
    """
    reader_url = f"https://r.jina.ai/{url}"

    resp = requests.get(reader_url, timeout=20)
    text = resp.text.strip()

    # 简单防御
    if not text or len(text) < 200:
        return {
            "type": "webpage_content",
            "url": url,
            "content": "",
            "error": "empty or unreadable content"
        }

    # 控制最大长度（避免炸 agent）
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[Content Truncated]"

    return {
        "type": "webpage_content",
        "url": url,
        "content": text,
        "length": len(text),
    }
import re

def remove_markdown_links_block(text: str) -> str:

    lines = text.splitlines()
    cleaned = []

    link_line_pattern = re.compile(r'^\s*[-*]?\s*\[.+?\]\(.+?\)')

    consecutive_link_lines = 0

    for line in lines:
        if link_line_pattern.match(line):
            consecutive_link_lines += 1
            # 连续 3 行以上链接，视为导航块，直接跳过
            if consecutive_link_lines >= 3:
                continue
        else:
            consecutive_link_lines = 0
            cleaned.append(line)

    return "\n".join(cleaned)
def remove_low_density_lines(text: str) -> str:
    lines = text.splitlines()
    result = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 太短的行通常是按钮、标签
        if len(line) < 20:
            continue

        # 链接比例过高的行
        link_ratio = line.count('http') / max(len(line), 1)
        if link_ratio > 0.05:
            continue

        result.append(line)

    return "\n".join(result)
def clean_jina_markdown(text: str) -> str:
    text = remove_markdown_links_block(text)
    text = remove_low_density_lines(text)
    return text.strip()

@tool("read_webpage",description="""
用于读取指定网页的详细内容。
当你已经有网页 URL，需要获取文章正文、技术细节或事实信息时使用。
返回已清洗的网页正文，不包含导航和无关链接。
参数说明：
- url：完整网页 URL（必须以 http 或 https 开头）                                                                                                                               
""")
def jina_reader_tool(url: str, max_chars: int = 5000) -> dict:
    reader_url = f"https://r.jina.ai/{url}"
    resp = requests.get(reader_url, timeout=200)

    raw_text = resp.text
    cleaned = clean_jina_markdown(raw_text)

    # if len(cleaned) > max_chars:
    #     cleaned = cleaned[:max_chars] + "\n\n[Content Truncated]"

    return {
        "type": "webpage_content",
        "url": url,
        "content": cleaned,
        "length": len(cleaned),
    }
from typing import List, Optional, Dict, Any
import os
@tool(
    "web_search",
    description="""
用于通过百度搜索引擎查找与用户问题相关的网页信息。
当你需要获取事实信息、最新资料或查找可靠来源时使用。
返回网页数量，默认 5
参数说明：
- query：自然语言搜索问题或关键词，不是 URL
- sites：限定搜索的网站域名列表，例如 ["baike.baidu.com"]
- recency：按发布时间过滤，可选值为 week / month / semiyear / year
"""
)
def web_search_tool(
    query: str,
    sites: Optional[List[str]] = None,
    recency: Optional[str] = None,
) -> Dict[str, Any]:
    """
    百度千帆 Web Search Tool
    """
    url = "https://qianfan.baidubce.com/v2/ai_search/web_search"
    top_k = 10
    API_KEY=os.getenv("BAIDU_API_KEY")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload: Dict[str, Any] = {
        "messages": [
            {
                "role": "user",
                "content": query
            }
        ],
        "search_source": "baidu_search_v2",
        "resource_type_filter": [
            {
                "type": "web",
                "top_k": min(top_k, 50)
            }
        ]
    }

    # 站点过滤（暂时免费）
    if sites:
        payload["search_filter"] = {
            "match": {
                "site": sites
            }
        }

    # 时效过滤
    if recency:
        payload["search_recency_filter"] = recency

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()
@tool("task_done",description="""
任务结束                                                                                                                              
""")
def task_done_search():
    print("SearchAgent 执行结束")
    return 