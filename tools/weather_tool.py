import datetime
import random
from typing import Dict, Any

def get_weather_forecast(destination: str, start_date_str: str) -> Dict[str, Any]:
    """
    Simulates weather lookup based on destination and start date.
    Returns temperatures, condition, summary, and suggested packing items.
    """
    dest_clean = destination.strip().lower()
    
    # Try parsing the month from start_date_str
    month = 6  # default to June
    try:
        dt = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
        month = dt.month
    except Exception:
        try:
            # Try alternate format
            dt = datetime.datetime.strptime(start_date_str, "%m/%d/%Y")
            month = dt.month
        except Exception:
            pass

    months_names = ["January", "February", "March", "April", "May", "June", 
                    "July", "August", "September", "October", "November", "December"]
    month_name = months_names[month - 1]

    # Predefined weather descriptions for popular spots depending on season (Summer: Jun-Aug, Winter: Dec-Feb, Spring: Mar-May, Autumn: Sep-Nov)
    # Values represent typical High/Low Temp in Celsius
    db = {
        "paris": {
            "winter": {"temp_high": 8, "temp_low": 3, "condition": "Overcast & Cold", "rain_chance": "45%", "humidity": "82%", "wind": "15 km/h"},
            "spring": {"temp_high": 16, "temp_low": 8, "condition": "Mild & Partly Cloudy", "rain_chance": "30%", "humidity": "72%", "wind": "11 km/h"},
            "summer": {"temp_high": 25, "temp_low": 15, "condition": "Warm & Sunny", "rain_chance": "15%", "humidity": "60%", "wind": "8 km/h"},
            "autumn": {"temp_high": 15, "temp_low": 9, "condition": "Cool & Misty", "rain_chance": "40%", "humidity": "78%", "wind": "12 km/h"}
        },
        "london": {
            "winter": {"temp_high": 9, "temp_low": 4, "condition": "Light Rain & Windy", "rain_chance": "60%", "humidity": "88%", "wind": "22 km/h"},
            "spring": {"temp_high": 14, "temp_low": 7, "condition": "Overcast & Showers", "rain_chance": "50%", "humidity": "80%", "wind": "14 km/h"},
            "summer": {"temp_high": 22, "temp_low": 13, "condition": "Pleasant & Clear", "rain_chance": "25%", "humidity": "68%", "wind": "10 km/h"},
            "autumn": {"temp_high": 14, "temp_low": 9, "condition": "Damp & Foggy", "rain_chance": "55%", "humidity": "85%", "wind": "16 km/h"}
        },
        "tokyo": {
            "winter": {"temp_high": 10, "temp_low": 2, "condition": "Sunny but Cold", "rain_chance": "10%", "humidity": "45%", "wind": "12 km/h"},
            "spring": {"temp_high": 18, "temp_low": 10, "condition": "Cherry Blossom Breeze", "rain_chance": "35%", "humidity": "65%", "wind": "10 km/h"},
            "summer": {"temp_high": 31, "temp_low": 24, "condition": "Hot & Humid", "rain_chance": "50%", "humidity": "80%", "wind": "11 km/h"},
            "autumn": {"temp_high": 20, "temp_low": 12, "condition": "Cool & Clear Sky", "rain_chance": "25%", "humidity": "60%", "wind": "9 km/h"}
        }
    }

    # Deduce season
    if month in [12, 1, 2]:
        season = "winter"
    elif month in [3, 4, 5]:
        season = "spring"
    elif month in [6, 7, 8]:
        season = "summer"
    else:
        season = "autumn"

    matched_city = None
    for city in db:
        if city in dest_clean:
            matched_city = city
            break

    if matched_city:
        weather_data = db[matched_city][season]
    else:
        # Generate procedurally
        seed = sum(ord(c) for c in dest_clean) + month
        rng = random.Random(seed)
        
        # Base temperatures on latitudes (arbitrary assignment via hashing)
        is_warm_climate = (seed % 3 == 0)
        is_rainy_climate = (seed % 5 == 0)
        
        if is_warm_climate:
            if season == "summer":
                weather_data = {"temp_high": rng.randint(30, 36), "temp_low": rng.randint(22, 26), "condition": "Hot & Dry", "rain_chance": "5%", "humidity": "50%", "wind": "12 km/h"}
            elif season == "winter":
                weather_data = {"temp_high": rng.randint(20, 25), "temp_low": rng.randint(14, 18), "condition": "Warm & Sunny", "rain_chance": "10%", "humidity": "62%", "wind": "8 km/h"}
            else:
                weather_data = {"temp_high": rng.randint(25, 30), "temp_low": rng.randint(18, 22), "condition": "Mild & Sunny", "rain_chance": "15%", "humidity": "55%", "wind": "10 km/h"}
        elif is_rainy_climate:
            weather_data = {"temp_high": rng.randint(15, 22), "temp_low": rng.randint(10, 15), "condition": "Frequent Showers", "rain_chance": "75%", "humidity": "90%", "wind": "18 km/h"}
        else:
            # Standard temperate climate
            if season == "summer":
                weather_data = {"temp_high": rng.randint(23, 28), "temp_low": rng.randint(12, 16), "condition": "Pleasant & Clear", "rain_chance": "20%", "humidity": "65%", "wind": "9 km/h"}
            elif season == "winter":
                weather_data = {"temp_high": rng.randint(3, 8), "temp_low": rng.randint(-3, 2), "condition": "Cold & Cloudy", "rain_chance": "30%", "humidity": "75%", "wind": "15 km/h"}
            else:
                weather_data = {"temp_high": rng.randint(12, 18), "temp_low": rng.randint(6, 11), "condition": "Breezy & Cool", "rain_chance": "40%", "humidity": "70%", "wind": "13 km/h"}

    # Generate packing tips
    packing_tips = ["Valid Passport", "Camera", "Comfortable walking shoes"]
    
    if weather_data["temp_high"] >= 28:
        packing_tips.extend(["Sunscreen", "Sunglasses", "Lightweight shorts/tshirts", "Refillable water bottle"])
    elif weather_data["temp_high"] <= 10:
        packing_tips.extend(["Thick winter coat", "Thermal layers", "Beanie & gloves", "Warm scarf"])
    else:
        packing_tips.extend(["Light jacket or sweater", "Layered clothing", "Long trousers"])

    if int(weather_data["rain_chance"].replace("%", "")) >= 40:
        packing_tips.extend(["Compact umbrella", "Waterproof jacket or poncho"])

    weather_data["packing_tips"] = packing_tips
    weather_data["month_name"] = month_name
    weather_data["season"] = season.capitalize()
    weather_data["temp_display"] = f"High: {weather_data['temp_high']}°C ({int(weather_data['temp_high']*1.8+32)}°F) | Low: {weather_data['temp_low']}°C ({int(weather_data['temp_low']*1.8+32)}°F)"
    weather_data["data_source"] = "Simulated Climate Statistics Service"
    
    return weather_data
