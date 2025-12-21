"""
Research Assistant Agent Implementation

Creates standard and deep agents for context distraction evaluation.
"""

from langchain.agents import create_agent
from deepagents import create_deep_agent

from context_distraction.tools import all_research_tools
from context_distraction.instructions import DETAILED_RESEARCH_INSTRUCTIONS


def create_standard_agent(llm, tools=None, system_prompt=None):
    """
    Create a standard agent using create_agent.
    
    This agent accumulates all tool call results in context,
    leading to context distraction as tasks get larger.
    """
    if tools is None:
        tools = all_research_tools
    if system_prompt is None:
        system_prompt = DETAILED_RESEARCH_INSTRUCTIONS
    
    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt
    )


def create_deep_agent_instance(llm, tools=None, system_prompt=None):
    """
    Create a deep agent using create_deep_agent.
    
    This agent stores tool results in virtual filesystem to reduce context length,
    mitigating context distraction for large tasks.
    """
    if tools is None:
        tools = all_research_tools
    if system_prompt is None:
        system_prompt = DETAILED_RESEARCH_INSTRUCTIONS
    
    return create_deep_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt
    )
