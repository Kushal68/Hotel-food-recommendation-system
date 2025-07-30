import re
import requests

GEMINI_API_KEY = "AIzaSyCTcWkbPvwBzb3Sx4QWifxS0VoBuFx2ick"
# Use free model endpoint
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

def parse_user_message(message: str) -> dict:
    # Prompt Gemini to extract hotel/food search preferences as JSON
    prompt = f"""
    Extract the following fields from the user's search request and return as JSON:
    - type (string, either 'hotel' or 'food')
    - location (string)
    - amenities (list of strings, for hotels)
    - cuisine (string, for food)
    - min_price (number, optional)
    - max_price (number, optional)
    - min_rating (number, optional)
    If a field is not mentioned, set it to null (or empty list for amenities).
    Example output: {{"type": "hotel", "location": "Annapurna Trek", "amenities": ["wifi"], "cuisine": null, "min_price": null, "max_price": null, "min_rating": null}}
    User message: {message}
    """
    data = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    try:
        response = requests.post(GEMINI_API_URL, json=data, timeout=10)
        response.raise_for_status()
        result = response.json()
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        import json
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
            for key in ["type", "location", "amenities", "cuisine", "min_price", "max_price", "min_rating"]:
                if key not in parsed:
                    parsed[key] = None if key not in ["amenities"] else []
            return parsed
    except requests.exceptions.HTTPError as e:
        print(f"Gemini API HTTP error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"Gemini API error: {e}")
    # Fallback: improved parser
    type_ = "hotel"
    if re.search(r"food|restaurant|cafe|diner", message, re.IGNORECASE):
        type_ = "food"
    
    # Extract location - stop at 'with', 'at least', 'minimum', etc.
    location = None
    location_match = re.search(
        r'in ([\w\s]+?)(?:\s+with|\s+at least|\s+minimum|\s+under|\s+over|\s+between|\s+\$|$)',
        message, re.IGNORECASE
    )
    if location_match:
        location = location_match.group(1).strip()
    
    # Extract cuisine for food - look for cuisine type before 'food' or 'restaurant'
    cuisine = None
    if type_ == "food":
        # Look for patterns like "Italian food", "Nepali restaurant", etc.
        # Avoid common words like 'me', 'a', 'the', 'some', 'any'
        cuisine_match = re.search(r'\b(Italian|Nepali|Indian|Chinese|French|Tibetan|Vegan|Continental|Bakery|Street Food|Tea & Snacks)\b\s+(?:food|restaurant|cafe|diner)', message, re.IGNORECASE)
        if cuisine_match:
            cuisine = cuisine_match.group(1).strip()
    
    # Extract price range (numerical values)
    min_price = None
    max_price = None
    
    # Look for patterns like "under $20", "over $15", "between $10 and $30"
    under_match = re.search(r'under \$?(\d+)', message, re.IGNORECASE)
    if under_match:
        max_price = int(under_match.group(1))
    
    over_match = re.search(r'over \$?(\d+)', message, re.IGNORECASE)
    if over_match:
        min_price = int(over_match.group(1))
    
    between_match = re.search(r'between \$?(\d+)\s+and\s+\$?(\d+)', message, re.IGNORECASE)
    if between_match:
        min_price = int(between_match.group(1))
        max_price = int(between_match.group(2))
    
    # Look for single price mentions like "$20" or "20 dollars"
    single_price_match = re.search(r'\$?(\d+)\s*(?:dollars?|USD)?', message, re.IGNORECASE)
    if single_price_match and min_price is None and max_price is None:
        price = int(single_price_match.group(1))
        # Assume it's a max price if no other context
        max_price = price
    
    # Extract min_rating (e.g., 'at least 4 stars', '4+ rating')
    min_rating = None
    rating_match = re.search(r'(?:at least|minimum|min) (\d+(?:\.\d+)?)', message)
    if not rating_match:
        rating_match = re.search(r'(\d+(?:\.\d+)?)\+? (?:stars?|rating)', message)
    if rating_match:
        min_rating = float(rating_match.group(1))
    
    # Extract amenities for hotels (e.g., 'with wifi and hot shower')
    amenities = []
    if type_ == "hotel":
        amenities_match = re.search(r'with ([\w\s,]+?)(?:\s+under|\s+over|\s+between|\s+\$|$)', message, re.IGNORECASE)
        if amenities_match:
            # Split by 'and', ','
            raw = amenities_match.group(1)
            for part in re.split(r',| and ', raw):
                part = part.strip()
                if part:
                    amenities.append(part)
    
    return {
        "type": type_,
        "location": location,
        "amenities": amenities,
        "cuisine": cuisine,
        "min_price": min_price,
        "max_price": max_price,
        "min_rating": min_rating,
        "raw_message": message
    }