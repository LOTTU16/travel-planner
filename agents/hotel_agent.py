import os
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from state import TravelPlannerState
from tools.hotel_tool import get_hotel_recommendations

def hotel_agent_node(state: TravelPlannerState) -> dict:
    """
    Hotel Agent node. Recommends lodging by querying the hotel tool
    and aligning recommendations with user budget and text preferences.
    Uses LLM for customized matching reasoning if available.
    """
    ext_dest = state.get("extracted_destination", {})
    dest_city = ext_dest.get("city", state.get("destination", ""))
    budget_tier = ext_dest.get("budget_tier", "Mid-range")
    preferences = state.get("preferences", "")

    # Query tool
    hotels = get_hotel_recommendations(dest_city, budget_tier)

    if not hotels:
        return {
            "hotels": [],
            "logs": ["Hotel Agent: No hotels found."],
            "errors": ["Hotel Agent: Empty hotel recommendations list."]
        }

    # Default rule-based selection/reasoning
    pref_words = [w.lower() for w in preferences.replace(",", " ").split() if len(w) > 2]
    for h in hotels:
        match_reasons = []
        # Check standard matches
        for p in pref_words:
            for am in h["amenities"]:
                if p in am.lower() or p in h["description"].lower() or p in h["area"].lower():
                    if p not in match_reasons:
                        match_reasons.append(p)
        
        if match_reasons:
            h["match_reason"] = f"Excellent fit for your interest in {', '.join(match_reasons)}. Located in {h['area']}."
        else:
            h["match_reason"] = f"Top-rated {h['rating']}★ hotel in {h['area']} matching your {budget_tier} budget."

    log_entry = f"Hotel Agent: Found {len(hotels)} hotels in {dest_city} matching budget category."

    # OpenAI powered reasoning
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if api_key and len(hotels) > 0:
        try:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, openai_api_key=api_key)
            prompt = ChatPromptTemplate.from_messages([
                ("system", (
                    "You are a luxury concierge hotel specialist. Analyze the hotel options and the user's travel preferences.\n"
                    "For each hotel, draft a short matching reason explaining why this hotel fits their preferences: '{preferences}'.\n"
                    "Keep the explanations concise (1-2 sentences). Respond with a JSON array of strings in the exact order of the hotels. Respond ONLY with raw JSON."
                )),
                ("user", "Hotels: {hotels_json}\nPreferences: {preferences}")
            ])
            chain = prompt | llm
            
            hotels_json = json.dumps([{k: v for k, v in h.items() if k != "match_reason"} for h in hotels])
            response = chain.invoke({"hotels_json": hotels_json, "preferences": preferences})
            
            raw_text = response.content.strip()
            if raw_text.startswith("```"):
                lines = raw_text.split("\n")
                if lines[0].startswith("```json"):
                    raw_text = "\n".join(lines[1:-1])
                else:
                    raw_text = "\n".join(lines[1:-1])
            
            reasons = json.loads(raw_text)
            if isinstance(reasons, list) and len(reasons) <= len(hotels):
                for idx, reason in enumerate(reasons):
                    hotels[idx]["match_reason"] = reason
                log_entry += " (Preferences matched by OpenAI)"
        except Exception as e:
            log_entry += f" (LLM personalization failed: {str(e)})"

    return {
        "hotels": hotels,
        "logs": [log_entry]
    }
