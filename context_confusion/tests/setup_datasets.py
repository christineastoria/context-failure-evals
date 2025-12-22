"""Dataset setup utilities for context confusion evaluation."""

from typing import List, Dict, Any
from langsmith import Client


def create_shipping_dataset(dataset_name: str, test_cases: List[Dict[str, Any]], client: Client):
    """
    Create or recreate a LangSmith dataset with shipping support test cases.
    
    Args:
        dataset_name: Name of the dataset to create
        test_cases: List of test case dictionaries with query, success_criteria, trajectory, etc.
        client: LangSmith client instance
    
    Returns:
        Dataset object
    """
    # Force recreate to ensure correct structure
    try:
        existing = client.read_dataset(dataset_name=dataset_name)
        client.delete_dataset(dataset_id=existing.id)
    except:
        pass

    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="Test queries exposing context confusion patterns with success criteria"
    )

    for case in test_cases:
        client.create_example(
            inputs={"query": case["query"]},
            outputs={
                "success_criteria": case["success_criteria"],
                "trajectory": case["trajectory"],
                "trajectory_comparison_mode": case["trajectory_comparison_mode"]
            },
            dataset_id=dataset.id
        )
    
    return dataset

