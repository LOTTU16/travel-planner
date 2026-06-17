import os
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from state import TravelPlannerState
from tools.weather_tool import get_weather_forecast

def weather_agent_node(state: TravelPlannerState) -> dict:
    """
    Weather Agent node. Fetches the weather forecast for the destination
    at the time of travel, and compiles tailored packing advice.
    Uses LLM for personalized tips if keys are available.
    """
    ext_dest = state.get("extracted_destination", {})
    dest_city = ext_dest.get("city", state.get("destination", ""))
    start_date = state.get("start_date", "")
    preferences = state.get("preferences", "")

    # Retrieve weather forecast details from tool
    weather_data = get_weather_forecast(dest_city, start_date)

    # Initial logs
    log_entry = f"Weather Agent: Fetched weather for {dest_city} in {weather_data.get('month_name')}. Expecting: {weather_data.get('condition')}."

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if api_key:
        try:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, openai_api_key=api_key)
            prompt = ChatPromptTemplate.from_messages([
                ("system", (
                    "You are a weather analyst and packing coach. Given the destination weather forecast and user travel preferences, "
                    "refine the list of packing items and add a brief 2-sentence clothing summary.\n"
                    "Provide your response as a JSON object with these keys: 'summary', 'packing_tips' (list of strings).\n"
                    "Respond ONLY with raw JSON."
                )),
                ("user", (
                    "Destination: {dest_city}\n"
                    "Forecast Condition: {condition}\n"
                    "Temperature: {temp_display}\n"
                    "Travel Month: {month_name}\n"
                    "User Interests: {preferences}\n"
                    "Base Packing Tips: {base_tips}"
                ))
            ])
            chain = prompt | llm
            
            response = chain.invoke({
                "dest_city": dest_city,
                "condition": weather_data["condition"],
                "temp_display": weather_data["temp_display"],
                "month_name": weather_data["month_name"],
                "preferences": preferences,
                "base_tips": ", ".join(weather_data["packing_tips"])
            })
            
            raw_text = response.content.strip()
            if raw_text.startswith("```"):
                lines = raw_text.split("\n")
                if lines[0].startswith("```json"):
                    raw_text = "\n".join(lines[1:-1])
                else:
                    raw_text = "\n".join(lines[1:-1])
            
            parsed = json.loads(raw_text)
            weather_data["summary"] = parsed.get("summary", f"Expect {weather_data['condition']} weather. Temperatures range: {weather_data['temp_display']}.")
            weather_data["packing_tips"] = parsed.get("packing_tips", weather_data["packing_tips"])
            log_entry += " (Packing suggestions refined by OpenAI)"
        except Exception as e:
            # LLM failed, fallback to standard description
            weather_data["summary"] = f"Expect {weather_data['condition']} weather. Temperatures: {weather_data['temp_display']}. Packing list recommended."
            log_entry += f" (LLM parsing failed: {str(e)})"
    else:
        # Procedural fallback description
        weather_data["summary"] = f"Expected weather is {weather_data['condition']}. {weather_data['temp_display']}. Climate is typical for {weather_data['season']}."

    return {
        "weather": weather_data,
        "logs": [log_entry]
    }
