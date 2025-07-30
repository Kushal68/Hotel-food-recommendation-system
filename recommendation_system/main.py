from fastapi import FastAPI
from pydantic import BaseModel
from gemini_api import parse_user_message
from recommender import recommend_hotels, recommend_food_places

app = FastAPI()

class RecommendationRequest(BaseModel):
    message: str

@app.post("/recommend")
def recommend(request: RecommendationRequest):
    parsed_query = parse_user_message(request.message)
    print(f"Parsed query: {parsed_query}")  # Debug output
    rec_type = parsed_query.get("type", "hotel")
    print(f"Recommendation type: {rec_type}")  # Debug output
    if rec_type == "food":
        recommendations = recommend_food_places(parsed_query)
    else:
        recommendations = recommend_hotels(parsed_query)
    print(f"Found {len(recommendations)} recommendations")  # Debug output
    return {"recommendations": recommendations} 