"""Dataset setup utilities for context distraction evaluation."""

from typing import Dict, Any, List
from langsmith import Client

from context_distraction.resources.test_tasks import TEST_TASKS
from context_distraction.resources.validation_utils import generate_expected_tool_calls

client = Client()


def build_reference_outputs(task: Dict[str, Any]) -> Dict[str, Any]:
    """Build reference outputs with all expected values."""
    expected_tool_calls = generate_expected_tool_calls(
        topics=task["topics"],
        primary_domain=task.get("primary_domain"),
        secondary_domain=task.get("secondary_domain"),
        stats_count=task.get("stats_count", 5),
        expert_count=task.get("expert_count", 3),
        case_count=task.get("case_count", 2),
        year_count=task.get("year_count", 3),
        compare_count=task.get("compare_count", 2),
    )
    
    return {
        "recall_questions": task["recall_questions"],
        "expected_answers": task.get("expected_answers", {}),
        "primary_domain": task.get("primary_domain", "renewable_energy"),
        "secondary_domain": task.get("secondary_domain", "artificial_intelligence"),
        "expected_trajectory": expected_tool_calls,
        "expected_trajectory_count": len(expected_tool_calls),
    }


def create_or_get_dataset(dataset_name: str, tasks: List[Dict[str, Any]] = None) -> Any:
    """Create or get LangSmith dataset with test tasks."""
    if tasks is None:
        tasks = TEST_TASKS
    
    try:
        dataset = client.read_dataset(dataset_name=dataset_name)
    except:
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="Research tasks of varying complexity"
        )
    
    # Get existing examples to avoid duplicates
    existing_examples = list(client.list_examples(dataset_id=dataset.id))
    existing_queries = {ex.inputs.get("query") for ex in existing_examples}
    
    # Only add examples that don't already exist
    for task in tasks:
        if task["query"] not in existing_queries:
            client.create_example(
                inputs={"query": task["query"]},
                outputs=build_reference_outputs(task),
                dataset_id=dataset.id
            )
    
    return dataset


def setup_datasets(full_name: str, slim_name: str, tasks: List[Dict[str, Any]]):
    """Setup full and slim datasets for testing."""
    full_dataset = create_or_get_dataset(full_name, tasks=tasks)
    slim_dataset = create_or_get_dataset(slim_name, tasks=tasks[:1])

    return full_dataset, slim_dataset

