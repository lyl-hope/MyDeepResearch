from app.agents import SearchAgent, ShellAgent, CodeAgent, ReportAgent, WebpageGenerationAgent
class AgentRegistry:
    def __init__(self):
        self.agents = {}

    def register(self, name: str, agent):
        self.agents[name] = agent

    def get(self, name: str):
        #print(self.agents)
        if name not in self.agents:
            raise ValueError(f"Unknown agent type: {name}")
        return self.agents[name]

    def list_agents(self):
        return list(self.agents.keys())

registry = AgentRegistry()

def build_registry():
    registry.register("search", SearchAgent())
    registry.register("shell", ShellAgent())
    registry.register("code", CodeAgent())
    registry.register("report", ReportAgent())
    registry.register("webpageGeneration", WebpageGenerationAgent())

    return registry