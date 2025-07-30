import json
import requests

API_KEY = "YOUR_API_KEY"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"

data = {
    "contents": [
        {"parts": [{"text": "Hello, world!"}]}
    ]
}

response = requests.post(url, json=data)
print(response.status_code)
print(response.text)

def recommend_hotels(parsed_query: dict):
    with open('hotels.json', 'r', encoding='utf-8') as f:
        hotels = json.load(f)
    location = parsed_query.get('location')
    amenities = parsed_query.get('amenities')
    min_price = parsed_query.get('min_price')
    max_price = parsed_query.get('max_price')
    min_rating = parsed_query.get('min_rating')
    filtered = hotels
    if location:
        filtered = [h for h in filtered if location.lower() in h['location'].lower()]
    # Only apply further filters if those fields are present and not empty
    if amenities:
        filtered = [h for h in filtered if all(a in h['amenities'] for a in amenities)]
    if min_price is not None:
        filtered = [h for h in filtered if h['price'] >= min_price]
    if max_price is not None:
        filtered = [h for h in filtered if h['price'] <= max_price]
    if min_rating is not None:
        filtered = [h for h in filtered if h['rating'] >= min_rating]
    # Sort by rating (desc), then price (asc)
    filtered = sorted(filtered, key=lambda h: (-h['rating'], h['price']))
    return filtered[:5]  # Return top 5


def recommend_food_places(parsed_query: dict):
    with open('food_places.json', 'r', encoding='utf-8') as f:
        food_places = json.load(f)
    location = parsed_query.get('location')
    cuisine = parsed_query.get('cuisine')
    min_price = parsed_query.get('min_price')
    max_price = parsed_query.get('max_price')
    min_rating = parsed_query.get('min_rating')
    filtered = food_places
    if location:
        filtered = [f for f in filtered if location.lower() in f['location'].lower()]
    if cuisine:
        filtered = [f for f in filtered if cuisine.lower() in f['cuisine'].lower()]
    if min_price is not None:
        filtered = [f for f in filtered if f['max_price'] >= min_price]
    if max_price is not None:
        filtered = [f for f in filtered if f['min_price'] <= max_price]
    if min_rating is not None:
        filtered = [f for f in filtered if f['rating'] >= min_rating]
    filtered = sorted(filtered, key=lambda f: -f['rating'])
    return filtered[:5]  # Return top 5 