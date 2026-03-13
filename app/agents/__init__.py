# app/agents/__init__.py

from .search import SearchAgent
from .shell import ShellAgent
from .code import CodeAgent
from .report import ReportAgent
from .webpageGeneration import WebpageGenerationAgent
__all__ = [
    "SearchAgent",
    "ShellAgent",
    "CodeAgent",
    "ReportAgent",
    "WebpageGenerationAgent",
]
