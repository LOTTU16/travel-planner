import os
import json
import datetime
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from state import TravelPlannerState

def destination_extraction_node(state: TravelPlannerState) -> dict:
    """
    Extracts structured destination data, normalizes city/country,
    calculates travel duration (number of days), and assigns a budget tier.
    Uses LLM if OPENAI_API_KEY is present, otherwise falls back to procedural extraction.
    """
    source = state.get("source", "").strip()
    destination = state.get("destination", "").strip()
    start_date_str = state.get("start_date", "")
    end_date_str = state.get("end_date", "")
    budget = state.get("budget", 1000.0)

    # 1. Procedural calculation of travel days
    num_days = 5
    try:
        d1 = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
        d2 = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
        num_days = max(1, (d2 - d1).days)
    except Exception:
        try:
            d1 = datetime.datetime.strptime(start_date_str, "%m/%d/%Y")
            d2 = datetime.datetime.strptime(end_date_str, "%m/%d/%Y")
            num_days = max(1, (d2 - d1).days)
        except Exception:
            pass

    # 2. Determine budget tier based on daily allowance
    daily_budget = budget / num_days
    if daily_budget < 100:
        budget_tier = "Budget"
    elif daily_budget < 300:
        budget_tier = "Mid-range"
    else:
        budget_tier = "Luxury"

    # Default/procedural extraction values
    city = destination.split(",")[0].strip()
    country = destination.split(",")[1].strip() if "," in destination else ""
    
    extracted_data = {
        "city": city.capitalize(),
        "country": country.capitalize() if country else "Unknown",
        "num_days": num_days,
        "budget_tier": budget_tier,
        "source_city": source.split(",")[0].strip().capitalize(),
        "method": "Procedural Parser (LLM Offline)"
    }

    log_entry = f"Destination Extraction Agent: Extracted {extracted_data['city']} from '{destination}'. Duration: {num_days} days. Budget tier: {budget_tier}."

    # 3. LLM Enhancement if API key is present
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if api_key:
        try:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=api_key)
            prompt = ChatPromptTemplate.from_messages([
                ("system", (
                    "You are a helpful travel assistant. Normalize the source and destination details into structured JSON.\n"
                    "Extract the source city, destination city, destination country, and identify the country. "
                    "Respond ONLY with a raw JSON object containing these keys: 'city', 'country', 'source_city'.\n"
                    "Example:\n"
                    "Input: destination='paris, france', source='nyc'\n"
                    "Output: {{\"city\": \"Paris\", \"country\": \"France\", \"source_city\": \"New York\"}}"
                )),
                ("user", "Input: destination='{destination}', source='{source}'")
            ])
            chain = prompt | llm
            response = chain.invoke({"destination": destination, "source": source})
            
            # Parse JSON
            raw_text = response.content.strip()
            # Basic cleaning in case markdowns are returned
            if raw_text.startswith("```"):
                lines = raw_text.split("\n")
                if lines[0].startswith("```json"):
                    raw_text = "\n".join(lines[1:-1])
                else:
                    raw_text = "\n".join(lines[1:-1])
            
            parsed = json.loads(raw_text)
            extracted_data["city"] = parsed.get("city", extracted_data["city"]).strip().capitalize()
            extracted_data["country"] = parsed.get("country", extracted_data["country"]).strip().capitalize()
            extracted_data["source_city"] = parsed.get("source_city", extracted_data["source_city"]).strip().capitalize()
            extracted_data["method"] = "OpenAI GPT-4o-mini"
            log_entry = f"Destination Extraction Agent (LLM): Extracted '{extracted_data['city']}, {extracted_data['country']}' starting from '{extracted_data['source_city']}'. Mode: {budget_tier}."
        except Exception as e:
            # Fallback is already filled
            log_entry += f" (LLM extraction failed: {str(e)})"

    return {
        "extracted_destination": extracted_data,
        "logs": [log_entry]
    }
