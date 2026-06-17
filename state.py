import operator
from typing import Annotated, TypedDict, List, Dict, Any

class TravelPlannerState(TypedDict):
    """
    State definition for the LangGraph travel planning workflow.
    Uses Annotated with operator.add for logs and errors to aggregate
    messages across concurrent agents without overwriting them.
    """
    # User inputs
    source: str
    destination: str
    start_date: str
    end_date: str
    budget: float
    preferences: str

    # Extracted / Calculated parameters
    extracted_destination: Dict[str, Any]  # {"city": str, "country": str, "num_days": int, "budget_tier": str}

    # Parallel Agent Outputs
    flights: List[Dict[str, Any]]
    hotels: List[Dict[str, Any]]
    weather: Dict[str, Any]

    # Sequential Agent Outputs
    itinerary: List[Dict[str, Any]]
    final_plan: str

    # Reducer arrays to accumulate executions & errors
    logs: Annotated[List[str], operator.add]
    errors: Annotated[List[str], operator.add]
