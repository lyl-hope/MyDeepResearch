import uuid
from app.config.render_prompt import render_jinja_prompt
from app.graph.state import GraphState, Task
from app.config.model import get_llm
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field, ValidationError, RootModel
from typing import List, Literal
from app.tools.others import parse_llm_output

import json
import pprint

def get_overall_summary(llm_output):
    try:
        tool = llm_output.get("tool")
        if tool is None:
            raise KeyError("missing key: tool")

        parameters = tool.get("parameters")
        if parameters is None:
            raise KeyError("missing key: tool.parameters")

        result = parameters.get("result")
        if result is None:
            raise KeyError("missing key: tool.parameters.result")

        # 如果 result 是字符串，尝试解析
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except Exception as e:
                raise ValueError(f"result 不是合法 JSON: {result}") from e

        assign = result.get("assign")
        if assign is None:
            raise KeyError("missing key: result.assign")

        overall_summary = assign.get("overall_summary")
        if overall_summary is None:
            raise KeyError("missing key: result.assign.overall_summary")

        return overall_summary

    except Exception as e:
        print("\n 解析 llm_output 出错")
        print("错误原因:", e)

        print("\n llm_output 原始内容:")
        pprint.pprint(llm_output)

        raise    
    
class AssignAgent:
    def __init__(self):
        self.llm = get_llm()

    def run(self, state: GraphState) -> GraphState:
        print("Assigner: 拆解计划并分配 Agent")

        origin_state = copy.deepcopy(state)

        render_context = {
            "current_plan": state.current_plan,
            "plans": state.plans,
            "assign_history":state.assign_history,
            "history_feedback":state.history_feedback,
            "assign_max_steps": state.assign_max_steps,
            "assign_step":state.assign_step
        }
        system_prompt = render_jinja_prompt(
            context=render_context,
            template_name="assign.jinja2"
        )

        messages = [
            SystemMessage(content=system_prompt.strip()),
            # HumanMessage(content=user_prompt.strip()),
        ]

        resp = self.llm.invoke(messages)
        text = resp.content.strip()

        llm_output = parse_llm_output(text)
        print("Assign Agent输出 ",llm_output)
        state.assign_step = state.assign_step + 1
        
        memory_key = f"Assign Round {state.assign_step}"
        print("Assign memory_key",memory_key)
        state.assign_history[memory_key] = {
                "think": llm_output["think"],
                "tool": llm_output["tool"],
                "tool_result": 'None',
            }
        state.last_assign_history=llm_output

        if llm_output['tool'] is not None:
            state.last_tool_result = llm_output['tool']
            if llm_output['tool']['function'] == 'taskdone':
                state.overall_summary = get_overall_summary(llm_output)#llm_output['tool']['parameters']['result']['assign']['overall_summary']
                #清空
                print(state.last_assign_history)
                state.assign_step = 0
                state.assign_history = {}
            else :
                state.overall_summary = None
                state.current_task = Task(
                    title=llm_output['tool']['parameters']['title'],
                    content=llm_output['tool']['parameters']['content'],
                    agent=llm_output['tool']['function'],
                    data=llm_output.get("tool", {}).get("parameters", {}).get("title", None)
                )
            return state    
        else:
            print("Assign解析失败，重新执行")
            return self.run(origin_state)
        