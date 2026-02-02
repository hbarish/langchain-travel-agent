# Michael Travel Agent

This is a single-agent travel planning application built with **LangChain (v1.2+)**.  
It generates a detailed, multi-city travel plan using real-time data from Google Maps APIs.

## Features
- Supports **multi-city trips** with single dates or date ranges
- Retrieves **weather forecasts** and **air quality** for each city
- Provides:
  - Clothing recommendations
  - Umbrella recommendations
  - Mask recommendations based on air quality
- Optionally suggests **tourist attractions** using the Google Places Text Search API
- Maintains short-term memory for follow-up questions using LangChain memory

## Technologies Used
- Python
- LangChain (`create_agent`)
- LangGraph memory
- Google Maps APIs (Geocoding, Weather, Air Quality, Places)
- `requests`
- `uv` for package management

## Setup
1. Ensure you have **Python 3.11+** and **uv** installed.
2. Create a `.env` file with your API keys:
   ```env
   GOOGLE_API_KEY=your_google_maps_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
