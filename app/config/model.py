import os
from langchain_openai import ChatOpenAI

def get_llm():
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "Qwen3-14B"),
        base_url=os.getenv("BASE_URL", "https://www.sophnet.com/api/open-apis"),
        temperature=float(os.getenv("OPENAI_TEMPERATURE", 0.2)),
        api_key=os.getenv("OPENAI_API_KEY"),
        verbose=True,
        max_tokens=8192
    )
