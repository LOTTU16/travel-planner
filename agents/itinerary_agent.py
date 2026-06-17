import os
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from state import TravelPlannerState

def itinerary_agent_node(state: TravelPlannerState) -> dict:
    """
    Itinerary Agent node. Generates a structured, day-wise schedule 
    based on flights, selected hotels, local weather, and user preferences.
    Uses LLM for full personalization when available.
    """
    ext_dest = state.get("extracted_destination", {})
    dest_city = ext_dest.get("city", state.get("destination", ""))
    num_days = ext_dest.get("num_days", 3)
    preferences = state.get("preferences", "Sightseeing")
    
    selected_hotel = state.get("hotels", [{}])[0].get("name", "Local Accommodations")
    weather_summary = state.get("weather", {}).get("summary", "typical weather")
    
    # Pre-calculate list of days
    itinerary_days = []
    
    log_entry = f"Itinerary Agent: Creating a {num_days}-day itinerary for {dest_city}."
    
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if api_key:
        try:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, openai_api_key=api_key)
            prompt = ChatPromptTemplate.from_messages([
                ("system", (
                    "You are a local tour guide and travel planner. Create a detailed day-wise itinerary for {dest_city}.\n"
                    "The plan must span exactly {num_days} day(s), integrating interests: '{preferences}'.\n"
                    "Consider that the traveler is staying at '{hotel}' and weather is: '{weather_summary}'.\n"
                    "Respond with a JSON array of objects, one for each day, containing: "
                    "'day' (int), 'title' (string), 'morning' (string), 'afternoon' (string), 'evening' (string).\n"
                    "Respond ONLY with raw JSON."
                )),
                ("user", "Generate the itinerary for {num_days} days in {dest_city}.")
            ])
            chain = prompt | llm
            
            response = chain.invoke({
                "dest_city": dest_city,
                "num_days": num_days,
                "preferences": preferences,
                "hotel": selected_hotel,
                "weather_summary": weather_summary
            })
            
            raw_text = response.content.strip()
            if raw_text.startswith("```"):
                lines = raw_text.split("\n")
                if lines[0].startswith("```json"):
                    raw_text = "\n".join(lines[1:-1])
                else:
                    raw_text = "\n".join(lines[1:-1])
            
            itinerary_days = json.loads(raw_text)
            log_entry += " (Generated dynamically by OpenAI)"
        except Exception as e:
            log_entry += f" (LLM generation failed: {str(e)})"
            itinerary_days = []

    # Procedural Fallback if LLM was offline or failed
    if not itinerary_days:
        # Generate procedurally based on popular topics and preferences
        themes = [
            {"title": "Arrival & City Overview", "morning": "Arrive in city, check into {hotel}, and unpack.", "afternoon": "Take a guided walking tour of the historical center.", "evening": "Enjoy a welcome dinner at a local traditional bistro."},
            {"title": "Cultural Discoveries", "morning": "Visit the city's premier art museum or gallery.", "afternoon": "Stroll through a famous botanical garden or historic park.", "evening": "Experience local performing arts or visit a scenic sky bar."},
            {"title": "Local Flavors & Shopping", "morning": "Explore a famous local food market for breakfast stalls.", "afternoon": "Shopping in boutique shopping districts or historic arcades.", "evening": "Join a cooking class or go on a street food tasting trail."},
            {"title": "Hidden Gems & Neighborhoods", "morning": "Visit a lesser-known residential neighborhood to experience local life.", "afternoon": "Explore a historic fortress, palace, or landmark ruins.", "evening": "Relax at a canal-side cafe or local watering hole."},
            {"title": "Scenic Excursion & Views", "morning": "Take a short day-trip or climb to the highest viewpoint in the city.", "afternoon": "Unwind with a boat cruise or a spa treatment.", "evening": "Have a celebratory final dinner overlooking the city lights."}
        ]
        
        for d in range(1, num_days + 1):
            # Pick a theme index based on day (cycling if num_days > 5)
            theme = themes[(d - 1) % len(themes)]
            itinerary_days.append({
                "day": d,
                "title": f"Day {d}: {theme['title']}",
                "morning": theme["morning"].format(hotel=selected_hotel),
                "afternoon": theme["afternoon"],
                "evening": theme["evening"]
            })
        log_entry += " (Generated using procedural templates)"

    return {
        "itinerary": itinerary_days,
        "logs": [log_entry]
    }
