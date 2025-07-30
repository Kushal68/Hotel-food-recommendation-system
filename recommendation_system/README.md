# Hotel Recommendation System (Content-Based Filtering)

## Overview
A FastAPI-based backend that recommends hotels based on user queries using content-based filtering. Integrates with Gemini API for natural language understanding.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

## Usage
Send a POST request to `/recommend` with JSON body:
```json
{
  "message": "recommend me hotel in annapurna trek routes"
}
```

## Files
- `main.py`: FastAPI app
- `gemini_api.py`: Gemini API integration (simulated)
- `recommender.py`: Content-based filtering logic
- `hotels.json`: Sample hotel data 