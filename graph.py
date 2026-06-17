from langgraph.graph import StateGraph, START, END
from state import TravelPlannerState
from agents.destination_agent import destination_extraction_node
from agents.flight_agent import flight_agent_node
from agents.hotel_agent import hotel_agent_node
from agents.weather_agent import weather_agent_node
from agents.itinerary_agent import itinerary_agent_node
from agents.final_planner import final_planner_node

def build_travel_planner_graph():
    """
    Constructs the LangGraph state machine.
    Sets up the following execution flow:
    
            START
              │
      [destination_extraction]
        /     │      \
    [flights] [hotels] [weather]  (Parallel execution)
        \     │      /
      [itinerary_generator]       (Fan-in / Merge point)
              │
       [final_planner]
              │
             END
    """
    # Initialize the graph with the TravelPlannerState structure
    workflow = StateGraph(TravelPlannerState)

    # 1. Define nodes
    workflow.add_node("destination_extraction", destination_extraction_node)
    workflow.add_node("flight_agent", flight_agent_node)
    workflow.add_node("hotel_agent", hotel_agent_node)
    workflow.add_node("weather_agent", weather_agent_node)
    workflow.add_node("itinerary_generator", itinerary_agent_node)
    workflow.add_node("final_planner", final_planner_node)

    # 2. Define edges and paths
    # Entry edge
    workflow.add_edge(START, "destination_extraction")

    # Fan-out to parallel agents
    workflow.add_edge("destination_extraction", "flight_agent")
    workflow.add_edge("destination_extraction", "hotel_agent")
    workflow.add_edge("destination_extraction", "weather_agent")

    # Fan-in from parallel agents into the sequential itinerary generator
    workflow.add_edge("flight_agent", "itinerary_generator")
    workflow.add_edge("hotel_agent", "itinerary_generator")
    workflow.add_edge("weather_agent", "itinerary_generator")

    # Sequential flow into final planner compilation
    workflow.add_edge("itinerary_generator", "final_planner")
    workflow.add_edge("final_planner", END)

    # Compile the graph
    return workflow.compile()

# Expose compiled application graph
compiled_graph = build_travel_planner_graph()
