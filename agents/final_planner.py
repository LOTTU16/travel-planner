import os
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from state import TravelPlannerState

def final_planner_node(state: TravelPlannerState) -> dict:
    """
    Final Planner Agent node. Synthesizes all gathered information (flights,
    hotels, weather, itinerary) into a beautifully formatted Markdown travel plan.
    Uses LLM for copy-writing polish when available.
    """
    ext_dest = state.get("extracted_destination", {})
    city = ext_dest.get("city", state.get("destination", ""))
    country = ext_dest.get("country", "")
    num_days = ext_dest.get("num_days", 3)
    budget_tier = ext_dest.get("budget_tier", "Mid-range")
    
    source = state.get("source", "")
    start_date = state.get("start_date", "")
    end_date = state.get("end_date", "")
    budget = state.get("budget", 1000.0)
    preferences = state.get("preferences", "")
    
    flights = state.get("flights", [])
    hotels = state.get("hotels", [])
    weather = state.get("weather", {})
    itinerary = state.get("itinerary", [])
    
    # Generate the base plan markdown (deterministic)
    flight_rows = ""
    for f in flights:
        rec = "⭐" if "recommendation_reason" in f and "Cheapest" in f["recommendation_reason"] or len(flights) == 1 else ""
        flight_rows += f"| {f['airline']} | {f['flight_no']} | {f['departure']} → {f['arrival']} | {f['duration']} | {f['stops']} | **{f['price_display']}** | {f.get('recommendation_reason', '')} {rec} |\n"
        
    hotel_cards = ""
    for idx, h in enumerate(hotels):
        rec = "🏆 **Recommended Choice**" if idx == 0 else ""
        hotel_cards += (
            f"### {idx+1}. {h['name']} ({h['rating']}★) {rec}\n"
            f"- **Location**: {h['area']}\n"
            f"- **Price**: {h['price_display']} ({h['tier_label']})\n"
            f"- **Amenities**: {', '.join(h['amenities'])}\n"
            f"- **Description**: {h['description']}\n"
            f"- **Match Verdict**: *{h.get('match_reason', '')}*\n\n"
        )
        
    weather_section = (
        f"### Forecast: {weather.get('condition', 'Typical Climate')}\n"
        f"- **Temperature**: {weather.get('temp_display', 'Mild')}\n"
        f"- **Humidity**: {weather.get('humidity', 'N/A')} | **Wind**: {weather.get('wind', 'N/A')} | **Rain Chance**: {weather.get('rain_chance', 'N/A')}\n"
        f"- **Outlook**: {weather.get('summary', '')}\n\n"
        f"🎒 **Recommended Packing List:**\n"
    )
    for tip in weather.get("packing_tips", []):
        weather_section += f"- [ ] {tip}\n"
        
    itinerary_section = ""
    for day in itinerary:
        itinerary_section += (
            f"### 🗓️ Day {day['day']}: {day['title']}\n"
            f"- **🌅 Morning**: {day['morning']}\n"
            f"- **☀️ Afternoon**: {day['afternoon']}\n"
            f"- **🌙 Evening**: {day['evening']}\n\n"
        )

    base_markdown = (
        f"# 🌍 Your Personalized Travel Plan to {city}, {country}\n\n"
        f"--- \n\n"
        f"## 📋 Trip Overview\n"
        f"- **Departure City**: {source}\n"
        f"- **Travel Dates**: {start_date} to {end_date} ({num_days} Days)\n"
        f"- **Budget Allocated**: ${budget:.2f} USD ({budget_tier} Tier)\n"
        f"- **Personal Travel Style / Preferences**: {preferences}\n\n"
        f"--- \n\n"
        f"## ✈️ Flight Recommendations\n"
        f"| Airline | Flight No | Schedule | Duration | Stops | Est. Price | Recommendation Reason |\n"
        f"| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
        f"{flight_rows}\n"
        f"--- \n\n"
        f"## 🏨 Hotel Options\n"
        f"{hotel_cards}"
        f"--- \n\n"
        f"## ☀️ Weather Outlook & Packing Guide\n"
        f"{weather_section}\n"
        f"--- \n\n"
        f"## 🗺️ Day-by-Day Itinerary\n"
        f"{itinerary_section}"
        f"--- \n\n"
        f"*Thank you for using AI Travel Planner. Have a safe and wonderful trip!*\n"
        f"*(This travel plan was synthesized by the coordination of 6 specialized agents using LangGraph)*\n"
    )

    log_entry = "Final Planner Agent: Compiled flight, hotel, weather, and itinerary details into Markdown."

    # OpenAI option to write a highly customized intro and outro, polishing the tone
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if api_key:
        try:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4, openai_api_key=api_key)
            prompt = ChatPromptTemplate.from_messages([
                ("system", (
                    "You are a professional travel editor. Your job is to take the structured travel plan and write a beautiful, "
                    "engaging, and polished introduction and conclusion, making the traveler feel excited. "
                    "Incorporate their specific preferences: '{preferences}'.\n"
                    "We will provide you with the base markdown. You must return the updated markdown containing the new, "
                    "highly polished sections. Do not alter the tables, dates, and prices. Return ONLY the final markdown."
                )),
                ("user", "Base Travel Plan Markdown:\n{base_markdown}")
            ])
            chain = prompt | llm
            
            response = chain.invoke({
                "base_markdown": base_markdown,
                "preferences": preferences
            })
            
            final_plan = response.content.strip()
            # If the LLM returned codeblock wrappers, clean them up
            if final_plan.startswith("```markdown"):
                final_plan = final_plan[11:]
                if final_plan.endswith("```"):
                    final_plan = final_plan[:-3]
            elif final_plan.startswith("```"):
                final_plan = final_plan[3:]
                if final_plan.endswith("```"):
                    final_plan = final_plan[:-3]
                    
            base_markdown = final_plan.strip()
            log_entry += " (Copy-writing and formatting enhanced by OpenAI)"
        except Exception as e:
            log_entry += f" (LLM editing failed: {str(e)})"

    return {
        "final_plan": base_markdown,
        "logs": [log_entry]
    }
