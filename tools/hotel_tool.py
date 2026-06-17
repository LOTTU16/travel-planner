import random
from typing import List, Dict, Any

def get_hotel_recommendations(destination: str, budget_tier: str) -> List[Dict[str, Any]]:
    """
    Simulates hotel search for a destination matching a budget tier.
    Returns hotels with ratings, price per night, amenities, and location description.
    """
    dest_clean = destination.strip().lower()

    # Pre-coded hotels for popular destinations
    # Price per night is normalized for "Mid-range", we will scale it for Budget/Luxury
    db = {
        "paris": [
            {
                "name": "Hotel Regina Louvre", 
                "base_price": 280, 
                "rating": 4.7, 
                "amenities": ["Free WiFi", "Eiffel Tower View", "Bar", "Pet Friendly"],
                "area": "1st Arr. (Louvre)",
                "description": "Elegant boutique hotel overlooking the Louvre Museum with classic French decor."
            },
            {
                "name": "Hotel Caron de Beaumarchais", 
                "base_price": 160, 
                "rating": 4.5, 
                "amenities": ["Free WiFi", "Air Conditioning", "Historical Building"],
                "area": "Le Marais",
                "description": "Charming 18th-century themed hotel situated in the vibrant Marais district."
            },
            {
                "name": "Les Piaules Nation Hostel", 
                "base_price": 60, 
                "rating": 4.2, 
                "amenities": ["Rooftop Bar", "Co-working space", "Shared Kitchen"],
                "area": "Nation",
                "description": "Modern boutique hostel featuring a rooftop terrace with panoramic Paris views."
            }
        ],
        "london": [
            {
                "name": "The Savoy", 
                "base_price": 650, 
                "rating": 4.9, 
                "amenities": ["Butler Service", "Indoor Pool", "Luxury Spa", "Award-winning Bar"],
                "area": "Covent Garden",
                "description": "Iconic luxury hotel on the Thames, synonymous with British elegance."
            },
            {
                "name": "CitizenM Tower of London", 
                "base_price": 180, 
                "rating": 4.6, 
                "amenities": ["Rooftop Bar", "iMac controls", "Free Movies", "24/7 Food"],
                "area": "City of London",
                "description": "High-tech, stylish lodging right above the Tower Hill tube station."
            },
            {
                "name": "The Generator London", 
                "base_price": 45, 
                "rating": 4.0, 
                "amenities": ["Games Room", "Cinema Room", "Bar", "Bicycle Rental"],
                "area": "Bloomsbury",
                "description": "Lively social hostel with quirky design elements, close to the British Museum."
            }
        ],
        "tokyo": [
            {
                "name": "Park Hyatt Tokyo", 
                "base_price": 750, 
                "rating": 4.8, 
                "amenities": ["Indoor Pool", "Peak Lounge", "Spa", "Skyline Views"],
                "area": "Shinjuku",
                "description": "Renowned high-rise luxury hotel famous for its panoramic views and appearance in 'Lost in Translation'."
            },
            {
                "name": "Hotel Gracery Shinjuku", 
                "base_price": 160, 
                "rating": 4.4, 
                "amenities": ["Godzilla Terrace", "Free WiFi", "Multiple Restaurants"],
                "area": "Kabukicho, Shinjuku",
                "description": "Popular modern hotel featuring the famous life-sized Godzilla head on its terrace."
            },
            {
                "name": "Nine Hours Capsule Hotel", 
                "base_price": 40, 
                "rating": 4.1, 
                "amenities": ["Futuristic Sleep Pods", "Locker Room", "High-speed WiFi"],
                "area": "Suidobashi",
                "description": "Ultra-minimalist capsule hotel providing sleeping pods, showers, and lockers."
            }
        ]
    }

    hotels = []
    
    # Check if we have pre-coded database options
    matched_city = None
    for city in db:
        if city in dest_clean:
            matched_city = city
            break
            
    if matched_city:
        hotels = [dict(h) for h in db[matched_city]]
    else:
        # Generate procedurally based on destination string
        seed = sum(ord(c) for c in dest_clean)
        rng = random.Random(seed)
        
        adjectives = ["Grand", "Boutique", "Royal", "Vista", "Metropolitan", "Garden", "Heritage", "Central"]
        nouns = ["Plaza", "Inn", "Suites", "Lodge", "Hotel & Spa", "Resort", "Retreat"]
        areas = ["Downtown", "Old Town District", "Waterfront Promenade", "Central Heights", "Theater District"]
        
        for i in range(3):
            adj = rng.choice(adjectives)
            noun = rng.choice(nouns)
            area = rng.choice(areas)
            
            # Rating between 3.8 and 4.9
            rating = round(rng.uniform(3.8, 4.9), 1)
            
            # Base price
            base = rng.randint(80, 300)
            
            amenity_pool = ["Free WiFi", "Breakfast Included", "Fitness Center", "Swimming Pool", "Rooftop Terrace", "Bicycle Rental", "Air Conditioning", "Restaurant & Bar"]
            amenities = rng.sample(amenity_pool, k=rng.randint(3, 5))
            
            hotels.append({
                "name": f"The {adj} {noun} {destination.capitalize()}",
                "base_price": base,
                "rating": rating,
                "amenities": amenities,
                "area": area,
                "description": f"A highly rated {rating}-star establishment offering comfortable lodging in the scenic {area} area."
            })

    # Scale and filter hotels based on the user's budget tier
    adjusted_hotels = []
    for h in hotels:
        new_h = dict(h)
        
        if budget_tier == "Budget":
            # Scale down base prices and adjust ratings to fit budget hotels
            new_h["price_per_night"] = int(new_h["base_price"] * 0.4)
            if new_h["price_per_night"] > 90:
                new_h["price_per_night"] = 85
            if new_h["price_per_night"] < 25:
                new_h["price_per_night"] = 35
            new_h["tier_label"] = "Budget-Friendly"
        elif budget_tier == "Luxury":
            # Scale up base prices for high-end experiences
            new_h["price_per_night"] = int(new_h["base_price"] * 2.8)
            if new_h["price_per_night"] < 400:
                new_h["price_per_night"] = 450
            new_h["tier_label"] = "Luxury / Five-Star"
            if "Butler Service" not in new_h["amenities"]:
                new_h["amenities"].append("Concierge Service")
        else:  # Mid-range
            new_h["price_per_night"] = int(new_h["base_price"] * 0.95)
            if new_h["price_per_night"] < 90:
                new_h["price_per_night"] = 120
            new_h["tier_label"] = "Mid-Range Comfort"
            
        new_h["price_display"] = f"${new_h['price_per_night']} / night"
        new_h["data_source"] = "Simulated Hospitality GDS API"
        adjusted_hotels.append(new_h)

    # Sort hotels by rating descending
    adjusted_hotels.sort(key=lambda x: x["rating"], reverse=True)
    return adjusted_hotels
