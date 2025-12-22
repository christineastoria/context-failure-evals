"""
Research Assistant Agent Implementation

Creates standard and deep agents for context distraction evaluation.
"""

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from context_distraction.tools import all_research_tools
from context_distraction.instructions import (
    STANDARD_RESEARCH_INSTRUCTIONS
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

agent = create_agent(
    model=llm,
    tools=all_research_tools,
    system_prompt=STANDARD_RESEARCH_INSTRUCTIONS
)
