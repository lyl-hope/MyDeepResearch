from dotenv import load_dotenv
load_dotenv()

from app.graph import build_graph
from app.graph.state import GraphState
from app.core import build_registry

def main():
    import os

    # os.environ["HTTP_PROXY"]  = "http://127.0.0.1:7890"
    # os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"
    AGENT_REGISTRY = build_registry()
    graph = build_graph()

    init_state = GraphState(
        user_query="上海AI Lab （上海浦江实验室）具身智能近期研究进展情况分析",
    )

    result = graph.invoke(init_state)

    print("\n=== FINAL STATE ===")
    print(result)


if __name__ == "__main__":
    main()
