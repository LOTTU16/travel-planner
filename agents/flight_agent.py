import os
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from state import TravelPlannerState
from tools.flight_tool import get_flight_recommendations

def flight_agent_node(state: TravelPlannerState) -> dict:
    """
    Flight Agent node. Retrieves flight recommendations based on extracted
    source, destination, and budget tier. Uses an LLM to add reasoning
    if API keys are available, otherwise applies a rule-based selection.
    """
    ext_dest = state.get("extracted_destination", {})
    source_city = ext_dest.get("source_city", state.get("source", ""))
    dest_city = ext_dest.get("city", state.get("destination", ""))
    budget_tier = ext_dest.get("budget_tier", "Mid-range")

    # Get flight options from tool
    options = get_flight_recommendations(source_city, dest_city, budget_tier)
    
    if not options:
        return {
            "flights": [],
            "logs": ["Flight Agent: No flights found."],
            "errors": ["Flight Agent: Empty flight options list."]
        }

    # Add default reasoning (rule-based)
    for i, opt in enumerate(options):
        if i == 0:
            opt["recommendation_reason"] = f"Cheapest option for {budget_tier} travel. Best for budget optimization."
        elif "Direct" in opt["stops"]:
            opt["recommendation_reason"] = "Direct flight. Best for saving travel time."
        else:
            opt["recommendation_reason"] = "Alternative schedule choice."

    log_entry = f"Flight Agent: Retrieved {len(options)} flights from {source_city} to {dest_city}."

    # Use LLM to personalize the recommendations and choose the best one if key is present
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if api_key and len(options) > 0:
        try:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, openai_api_key=api_key)
            prompt = ChatPromptTemplate.from_messages([
                ("system", (
                    "You are an expert flight booking agent. Analyze the provided flight options for a travel route.\n"
                    "Provide a short personal recommendation reason for each flight option based on the travel budget category: {budget_tier}.\n"
                    "Respond with a JSON array of strings, where each string corresponds to the recommendation reason for each flight in order.\n"
                    "Keep reasons concise (1-2 sentences). Respond ONLY with raw JSON."
                )),
                ("user", "Flight Options: {options_json}\nBudget Tier: {budget_tier}")
            ])
            chain = prompt | llm
            
            options_json = json.dumps([{k: v for k, v in f.items() if k != "recommendation_reason"} for f in options])
            response = chain.invoke({"options_json": options_json, "budget_tier": budget_tier})
            
            raw_text = response.content.strip()
            if raw_text.startswith("```"):
                lines = raw_text.split("\n")
                if lines[0].startswith("```json"):
                    raw_text = "\n".join(lines[1:-1])
                else:
                    raw_text = "\n".join(lines[1:-1])
            
            reasons = json.loads(raw_text)
            if isinstance(reasons, list) and len(reasons) <= len(options):
                for idx, reason in enumerate(reasons):
                    options[idx]["recommendation_reason"] = reason
                log_entry += " (Reasoning enhanced by OpenAI)"
        except Exception as e:
            log_entry += f" (LLM reasoning failed: {str(e)})"

    return {
        "flights": options,
        "logs": [log_entry]
    }
