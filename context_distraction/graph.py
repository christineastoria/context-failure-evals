"""Simplified LangGraph implementation for research agent."""

from typing import Literal
import asyncio
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langgraph.types import Command
from langchain_openai import ChatOpenAI
from context_distraction.instructions import (
    GRAPH_PLANNER_INSTRUCTIONS,
    GRAPH_SUPERVISOR_INSTRUCTIONS,
    GRAPH_RESEARCHER_INSTRUCTIONS,
    FINAL_REPORT_INSTRUCTIONS
)
from context_distraction.state import ResearchPlan, SupervisorState, ResearcherState
from context_distraction.tools import (
    all_research_tools, 
    finish, 
    general_research, 
    store_deliverable, 
    think_tool,
    create_deep_research_tool,
    research_complete,
)

load_dotenv()

# State definitions (simplified - user will define these)
# AgentState, SupervisorState, ResearcherState
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


researcher_tools_list = all_research_tools + [store_deliverable, finish]
researcher_llm = llm.bind_tools(researcher_tools_list)

async def researcher(state, config):
    """Individual researcher that delivers a key deliverable."""
    researcher_messages = state.get("reseacher_messages", [])
    # Add researcher instructions to the messages
    full_prompt = [SystemMessage(content=GRAPH_RESEARCHER_INSTRUCTIONS)] + researcher_messages
    result = researcher_llm.invoke(full_prompt)
    return {"reseacher_messages": [result]}


def should_continue_research(state: ResearcherState) -> Literal["researcher_tools", "__end__"]:
    """Conditional edge that determines whether to continue to tools or end."""
    researcher_messages = state.get("reseacher_messages", [])
    if not researcher_messages:
        return "__end__"
    last_message = researcher_messages[-1]
    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
        return "__end__"
    else:
        return "researcher_tools"


def check_research_finished(state: ResearcherState) -> Literal["researcher", "__end__"]:
    """Check if the last tool called was finish and route accordingly."""
    researcher_messages = state.get("reseacher_messages", [])
    if not researcher_messages:
        return "researcher"
    
    # Find the last AIMessage with tool_calls (should be the one that just executed tools)
    for i in range(len(researcher_messages) - 1, -1, -1):
        msg = researcher_messages[i]
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            # Check if any tool call was finish
            for tool_call in msg.tool_calls:
                tool_name = tool_call.get('name') if isinstance(tool_call, dict) else getattr(tool_call, 'name', '')
                if tool_name == 'finish':
                    return "__end__"
            # Found an AIMessage with tool_calls, but finish wasn't called
            break
    
    return "researcher"


# Researcher Subgraph (defined after functions so we can use them)
researcher_builder = StateGraph(ResearcherState)
researcher_builder.add_node("researcher", researcher)
researcher_builder.add_node("researcher_tools", ToolNode(researcher_tools_list, messages_key="reseacher_messages"))
researcher_builder.add_edge(START, "researcher")
researcher_builder.add_conditional_edges(
    "researcher",
    should_continue_research,
    {"researcher_tools": "researcher_tools", "__end__": END}
)
researcher_builder.add_conditional_edges(
    "researcher_tools",
    check_research_finished,
    {
        "researcher": "researcher",
        "__end__": END
    }
)
researcher_subgraph = researcher_builder.compile()


plan_llm = llm.with_structured_output(ResearchPlan)
async def create_research_plan(state, config) -> Command[Literal["supervisor"]]:
    """Transform user messages into a structured research brief."""
    supervisor_messages = state.get("supervisor_messages", [])
    
    # Pass the whole message history
    prompt = [SystemMessage(content=GRAPH_PLANNER_INSTRUCTIONS)] + supervisor_messages
    result = plan_llm.invoke(prompt)
    query = result.query
    plan = result.research_plan
    deliverables = {
        deliverable: "To be determined"
        for deliverable in result.key_deliverables
    }
    
    return Command(
        goto="supervisor",
        update={
            "research_plan": plan,
            "deliverables": deliverables,
            "query": query,
            "supervisor_messages": [
                HumanMessage(content=f"The user's query is: {query}"),
                HumanMessage(content=f"Current status of key deliverables: {deliverables}")
            ]
        }
    )


# Create deep_research tool with researcher_subgraph reference
deep_research = create_deep_research_tool(researcher_subgraph)
supervisor_tools = [general_research, deep_research, think_tool, research_complete]
supervisor_llm = llm.bind_tools(supervisor_tools)

async def supervisor(state, config) -> Command[Literal["supervisor_tools", "__end__"]]:
    """Lead research supervisor that plans research strategy."""
    supervisor_messages = state.get("supervisor_messages", [])
    result = supervisor_llm.invoke([SystemMessage(content=GRAPH_SUPERVISOR_INSTRUCTIONS)] + supervisor_messages)
    
    return {"supervisor_messages": [result]}
    

def should_continue(state: SupervisorState) -> Literal["supervisor_tools", "__end__"]:
    """Conditional edge that determines whether to continue to tools or end."""
    supervisor_messages = state.get("supervisor_messages", [])
    if not supervisor_messages:
        return "__end__"
    last_message = supervisor_messages[-1]
    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
        return "__end__"
    else:
        return "supervisor_tools"


def check_research_complete(state: SupervisorState) -> Literal["supervisor", "__end__"]:
    """Check if the last tool called was research_complete and route accordingly."""
    supervisor_messages = state.get("supervisor_messages", [])
    if not supervisor_messages:
        return "supervisor"
    
    # Find the last AIMessage with tool_calls (should be the one that just executed tools)
    for i in range(len(supervisor_messages) - 1, -1, -1):
        msg = supervisor_messages[i]
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            # Check if any tool call was research_complete
            for tool_call in msg.tool_calls:
                tool_name = tool_call.get('name') if isinstance(tool_call, dict) else getattr(tool_call, 'name', '')
                if tool_name == 'research_complete':
                    return "__end__"
            # Found an AIMessage with tool_calls, but research_complete wasn't called
            break
    
    return "supervisor"


# Supervisor Subgraph
supervisor_builder = StateGraph(SupervisorState)
supervisor_builder.add_node("supervisor", supervisor)
supervisor_builder.add_node("supervisor_tools", ToolNode(supervisor_tools, messages_key="supervisor_messages"))
supervisor_builder.add_edge(START, "supervisor")
supervisor_builder.add_conditional_edges(
    "supervisor",
    should_continue,
    {
        "supervisor_tools": "supervisor_tools",
        "__end__": END
    }
)
supervisor_builder.add_conditional_edges(
    "supervisor_tools",
    check_research_complete,
    {
        "supervisor": "supervisor",
        "__end__": END
    }
)
supervisor_subgraph = supervisor_builder.compile()


async def final_report_generation(state, config):
    """Generate the final comprehensive research report from findings and deliverables."""
    
    # Extract deliverables and messages from state
    deliverables = state.get("deliverables", {})
    supervisor_messages = state.get("supervisor_messages", [])
    query = state.get("query", "")
    
    # Prepare deliverables text
    deliverables_text = "\n".join([f"- {key}: {value}" for key, value in deliverables.items()])
    
    # Format conversation history as string
    from langchain_core.messages import get_buffer_string
    conversation_history = get_buffer_string(supervisor_messages)
    
    # Create prompt for final report generation
    report_prompt = [
        SystemMessage(content=FINAL_REPORT_INSTRUCTIONS),
        HumanMessage(content=f"""Generate the final comprehensive research report.

**Original Query, with Instructions:**
{query}

**Completed Deliverables:**
{deliverables_text if deliverables_text else ""}

**Conversation History:**
The following conversation history contains all research findings, tool results, and calculations:
{conversation_history}
""")
    ]

    # Generate final report using LLM
    final_report = llm.invoke(report_prompt).content
    
    # Add the final report as a supervisor message
    return {
        "supervisor_messages": [
            AIMessage(content=final_report)
        ]
    }


# Main Graph
graph_builder = StateGraph(SupervisorState)
graph_builder.add_node("supervisor", supervisor_subgraph)
graph_builder.add_node("create_research_plan", create_research_plan)
graph_builder.add_node("final_report_generation", final_report_generation)

graph_builder.add_edge(START, "create_research_plan")
graph_builder.add_edge("create_research_plan", "supervisor")
graph_builder.add_edge("supervisor", "final_report_generation")
graph_builder.add_edge("final_report_generation", END)

graph = graph_builder.compile()
