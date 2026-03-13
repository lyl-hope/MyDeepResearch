import os
from datetime import datetime
from app.graph.state import GraphState, Task
from app.tools.search_tool import web_search_tool,jina_reader_tool,task_done_search
from app.config.model import get_llm
from app.agents.base import BaseAgent
from app.config.render_prompt import render_jinja_prompt
from langchain.agents import create_agent
# from langchain_community.tools.you import YouSearchTool
# from langchain_community.utilities.you import YouSearchAPIWrapper
from langchain_tavily import TavilySearch
class SearchAgent(BaseAgent):
    name = "search"

    def __init__(self):
        llm = get_llm()

        # # ---- YouSearch 工具 ----
        # api_wrapper = YouSearchAPIWrapper(ydc_api_key=os.getenv("YDC_API_KEY"),num_web_results=3)
        # search_tool = YouSearchTool(api_wrapper=api_wrapper)


        # # ---- TavilySearch 工具 ----
        # tavily_search_tool = TavilySearch(
        #     max_results=5,
        #     topic="general",
        # )

        # ---- BaiduSearch 工具 ----
        # tools = [
        #         web_search_tool,
        #         jina_reader_tool,
        #         task_done_search
        #     ]
        # # ---- LangGraph ReAct Agent----
        # self.agent = create_agent(
        #     model=llm,
        #     tools=tools,
        #     debug=True
        # )

        # ---- Prompt ----
        from jinja2 import Environment, FileSystemLoader, StrictUndefined
        from datetime import datetime

        
#         self.system_prompt = """
# 【Role】
# 你是一个“搜索专家 Agent（Search Agent）”。

# 你只负责通过联网搜索获取信息，并对搜索结果进行筛选、整理与简要总结。
# 你不是分析型或报告型 Agent，不进行深入推理或长文本写作。

# ---

# 【Task】
# 根据给定的检索任务，完成以下目标：
# 1. 判断是否需要进行联网搜索或网页读取
# 2. 调用合适的工具获取信息
# 3. 提取与任务最相关的关键信息
# 4. 输出简要、结构化的搜索结果摘要

# ---

# 【Context / Tools】
# 你可以使用以下工具：

# - web_search  
#   用于获取**最新信息或整体背景**（例如新闻、近期事件、概览性资料）

# - read_webpage  
#   用于获取**某个具体网页的详细内容**

# 使用规则：
# - 当问题需要“最新信息”或“外部事实”时，优先使用 web_search
# - 当需要某个链接或页面的具体内容时，使用 read_webpage
# - 如果无需搜索即可完成任务，可以不调用工具

# ---

# 【Reasoning】
# 你必须遵循 ReAct 架构，但不要输出冗长思考过程：

# 1. Thought（内部判断）  
#    - 判断是否需要搜索  
#    - 判断使用哪个工具  
#    （此部分保持简短，不要展开长推理）

# 2. Action  
#    - 调用 web_search 或 read_webpage（如需要）

# 3. Observation  
#    - 基于工具返回结果进行信息筛选与整理

# 4. Final Answer  
#    - 以规定的 JSON 格式输出最终结果

# ---

# 【Rules】
# 1. 只做搜索与信息整理，不撰写长报告或深入分析
# 2. 严禁编造、猜测或补充未在搜索结果中出现的信息
# 3. 如果信息不足或未找到明确结果，应如实说明
# 4. 输出内容必须简洁、信息密度高、结构清晰
# 5. 除工具调用外，不要输出多余解释性文本
# 6.最多使用web_search和read_webpage两次，当你已经获得足够信息可以完成任务时，必须立即停止搜索。
# ---

# 【Output Format】
# 当你完成搜索任务后，**必须且只能**以 JSON 形式输出 Final Answer，涉及外部信息，final_answer 中的result以内联方式标注（如 [1]、[2]）
# 格式如下：

# ```json
# {
#   "task": "检索任务的简要描述",
#   "execution": "执行过程概述（如：使用了 web_search / read_webpage，搜索了哪些方向）",
#   "results": [
#     "搜索要点摘要 1 [0](表示sources中的第一个网址来源)",
#     "搜索要点摘要 2",
#     "搜索要点摘要 3"
#   ],
#   "sources": [
#     "上述要点的来源，需要一一对应"
#   ]
# }
# """

    def run(self, task: Task, state: GraphState) -> str:
        print(f"SearchAgent: {task.content}")
        tools = [
                web_search_tool,
                jina_reader_tool,
                task_done_search
            ]
        # ---- LangGraph ReAct Agent----
        agent = create_agent(
            model=get_llm(),
            tools=tools,
            # debug=True
        )

        render_context = {
            "current_datetime_utc": datetime.utcnow().isoformat() + "Z",
            "task_title": task.title,
            "task_content":task.content,
            "user_feedback": state.user_feedback,
        }
        system_prompt = render_jinja_prompt(
            context=render_context,
            template_name="search.jinja2"
        )
        try:
            response = agent.invoke(
                {
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        # {"role": "user", "content": task.content},
                    ]
                },
                {
                    "recursion_limit": 20,  # 防止死循环
                },
            )
        except Exception as e:
            raise RuntimeError(f"SearchAgent 执行失败: {e}")

        # ---- 抽取最终输出 ----
        if isinstance(response, dict) and "messages" in response:
            out_text = response["messages"][-1].content
        else:
            out_text = str(response)
        print(f"Search Agent 最后输出：{out_text}")
        return out_text
    
    
# def search_agent(state: GraphState) -> GraphState:
#     print("Bocha Search")

#     task = next(t for t in state.tasks if t.id == state.current_task_id)
#     raw = bocha_search(task.content)
    
#     #print(raw)
    
#     pages = extract_bocha_webpages(raw)

#     if not pages:
#         task.status = "done"
#         return state

#     snippets = [
#         f"【{p['site']}】{p['title']}\n{p['snippet']}"
#         for p in pages[:5]
#     ]

#     llm = get_llm()
#     print(snippets)
    
#     # 用 LLM 整理结果
#     llm = get_llm()
#     snippets_text = "\n".join(snippets)
#     prompt = f"""
# 根据以下国内搜索结果，提取与任务最相关的信息（保留关键点）：

# 任务：
# {task.content}

# 搜索结果：
# {snippets_text}
#     """
#     summary = llm.invoke(prompt).content.strip()

#     state.public_memory["search"] = {
#         "query": task.content,
#         "summary": summary,
#         "raw": raw,
#     }

#     task.status = "done"
#     state.current_agent = None
#     state.current_task_id = None
#     return state
