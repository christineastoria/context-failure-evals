import operator
from langgraph.graph import MessagesState
from langchain_core.messages import MessageLikeRepresentation
from pydantic import BaseModel, Field
from typing import Annotated, List, Dict, Optional, TypedDict


def override_reducer(current_value, new_value):
    """Reducer function that allows overriding values in state."""
    if isinstance(new_value, dict) and new_value.get("type") == "override":
        return new_value.get("value", new_value)
    elif isinstance(current_value, dict) and isinstance(new_value, dict):
        # Merge dictionaries instead of adding
        return {**current_value, **new_value}
    else:
        return operator.add(current_value, new_value)

        
class ResearcherState(TypedDict):
    """Model for researcher state."""
    research_question: str
    reseacher_messages: Annotated[list[MessageLikeRepresentation], override_reducer]
    deliverables: Annotated[Dict[str, str], override_reducer] = {}
    deliverable_key: Optional[str]  # The shorthand name of the deliverable this researcher should store
    finding: Optional[str]
    data_level: Optional[str]  # Level of data needed: aggregate, specific, or stated
    data_source: Optional[str]  # Where to find data: statistics, key_points, or research_findings
    calculation_guidance: Optional[str]  # Formula/method guidance for calculations

class SupervisorState(TypedDict):
    """State for the supervisor that manages research tasks."""
    supervisor_messages: Annotated[list[MessageLikeRepresentation], override_reducer]
    query: str
    research_plan: Optional[str]
    deliverables: Annotated[Dict[str, str], override_reducer] = {}


class ResearchPlan(BaseModel):
    query: str = Field(
        description="The user's query to be researched. Should be written as verbatim as possible, with changes only made for clarity and formatting.",
    )
    research_plan: str = Field(
        description="A high level plan of approach for answering the user's query.",
    )
    key_deliverables: List[str] = Field(
        description="A list of key deliverables. Each deliverable MUST be a short phrase (3-6 words) that captures the key metric or information that must be included.",
    )