import random
from typing import List, Dict, Any

def get_flight_recommendations(source: str, destination: str, budget_tier: str) -> List[Dict[str, Any]]:
    """
    Simulates fetching flight recommendations.
    Uses realistic mock templates and dynamically generates flight options
    based on the budget tier and routing.
    """
    src_clean = source.strip().lower()
    dest_clean = destination.strip().lower()

    # Pre-defined mock database for popular routes (pricing targets mid-range)
    db = {
        ("new york", "london"): [
            {"airline": "British Airways", "flight_no": "BA-178", "departure": "08:30 AM", "arrival": "08:45 PM", "duration": "7h 15m", "base_price": 550, "class": "Economy", "stops": "Direct"},
            {"airline": "Virgin Atlantic", "flight_no": "VS-4", "departure": "06:30 PM", "arrival": "06:50 AM (+1)", "duration": "7h 20m", "base_price": 580, "class": "Economy", "stops": "Direct"},
            {"airline": "Norse Atlantic", "flight_no": "N0-302", "departure": "11:00 PM", "arrival": "11:35 AM (+1)", "duration": "7h 35m", "base_price": 320, "class": "Economy", "stops": "Direct"}
        ],
        ("new york", "paris"): [
            {"airline": "Air France", "flight_no": "AF-007", "departure": "07:00 PM", "arrival": "08:30 AM (+1)", "duration": "7h 30m", "base_price": 620, "class": "Economy", "stops": "Direct"},
            {"airline": "Delta Air Lines", "flight_no": "DL-264", "departure": "05:30 PM", "arrival": "07:15 AM (+1)", "duration": "7h 45m", "base_price": 590, "class": "Economy", "stops": "Direct"},
            {"airline": "Icelandair", "flight_no": "FI-614", "departure": "02:00 PM", "arrival": "06:50 AM (+1)", "duration": "9h 50m", "base_price": 380, "class": "Economy", "stops": "1 stop (KEF)"}
        ],
        ("london", "tokyo"): [
            {"airline": "Japan Airlines", "flight_no": "JL-42", "departure": "09:40 AM", "arrival": "07:25 AM (+1)", "duration": "13h 45m", "base_price": 1100, "class": "Economy", "stops": "Direct"},
            {"airline": "British Airways", "flight_no": "BA-5", "departure": "01:20 PM", "arrival": "11:05 AM (+1)", "duration": "13h 45m", "base_price": 1050, "class": "Economy", "stops": "Direct"},
            {"airline": "Emirates", "flight_no": "EK-4", "departure": "08:00 PM", "arrival": "10:35 PM (+1)", "duration": "18h 35m", "base_price": 750, "class": "Economy", "stops": "1 stop (DXB)"}
        ]
    }

    # Search for an exact match or fallback to generating dynamically
    key = (src_clean, dest_clean)
    flights = []
    
    if key in db:
        flights = [dict(f) for f in db[key]]
    else:
        # Procedural generation based on source and destination name hashes
        # This keeps the output deterministic for the same input
        seed = sum(ord(c) for c in (src_clean + dest_clean))
        rng = random.Random(seed)
        
        carriers = [
            {"name": "Global Airways", "code": "GA"},
            {"name": "JetStream Connect", "code": "JC"},
            {"name": "EcoFly", "code": "EF"},
            {"name": "SkyLink Express", "code": "SL"}
        ]
        
        for i in range(3):
            carrier = rng.choice(carriers)
            f_num = rng.randint(100, 999)
            dep_hour = rng.randint(6, 22)
            dep_min = rng.choice([0, 15, 30, 45])
            duration_hours = rng.randint(2, 14)
            duration_mins = rng.choice([0, 15, 30, 45])
            
            dep_time = f"{dep_hour:02d}:{dep_min:02d} {'AM' if dep_hour < 12 else 'PM'}"
            duration = f"{duration_hours}h {duration_mins}m"
            
            # Base price scales with duration
            base = 100 + (duration_hours * 60)
            # Add some randomness
            base += rng.randint(-30, 50)
            
            flights.append({
                "airline": carrier["name"],
                "flight_no": f"{carrier['code']}-{f_num}",
                "departure": dep_time,
                "arrival": f"{(dep_hour + duration_hours) % 12 or 12:02d}:{dep_min:02d} {'AM' if (dep_hour + duration_hours) % 24 < 12 else 'PM'}",
                "duration": duration,
                "base_price": base,
                "class": "Economy",
                "stops": "Direct" if duration_hours < 6 else "1 stop"
            })

    # Adjust flights based on budget tier
    adjusted_flights = []
    for f in flights:
        new_f = dict(f)
        if budget_tier == "Budget":
            new_f["base_price"] = int(f["base_price"] * 0.85)
            new_f["class"] = "Economy (Saver)"
        elif budget_tier == "Luxury":
            new_f["base_price"] = int(f["base_price"] * 3.5)
            new_f["class"] = "Business Class"
            new_f["stops"] = "Direct"  # Luxury prefers direct
        else:
            new_f["base_price"] = int(f["base_price"])
            new_f["class"] = "Economy"
            
        new_f["price_display"] = f"${new_f['base_price']} USD"
        new_f["data_source"] = "Simulated Airline Inventory API"
        adjusted_flights.append(new_f)

    # Sort flights by price
    adjusted_flights.sort(key=lambda x: x["base_price"])
    return adjusted_flights
