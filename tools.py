# tools.py
DEBUG = False  # change to True when debugging

import os
import requests
from langchain.tools import tool
from dotenv import load_dotenv
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --------------------------
# ADDRESS TOOL
# --------------------------
@tool
def geocode_address(address: str) -> dict:
    """Convert address into city, latitude, and longitude."""
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_API_KEY}
    r = requests.get(url, params=params)
    
    data = r.json()
    
    if data["status"] != "OK":
        return {"error": f"Geocoding failed: {data.get('status')}"}

    if not data.get("results"):
        return {"error": "Address not found"}

    result = data["results"][0]
    location = result["geometry"]["location"]

    city = "Unknown city"
    for c in result["address_components"]:
        if "locality" in c["types"]:
            city = c["long_name"]
            break

    return {
        "city": city,
        "lat": location["lat"],
        "lon": location["lng"]
    }

# --------------------------
# WEATHER TOOL
# --------------------------
@tool
def get_weather(lat: float, lon: float, date_yyyy_mm_dd: str, days: int = 10) -> dict:
    """Get daily weather forecast for a specific date (YYYY-MM-DD) from Google Weather API."""
    url = "https://weather.googleapis.com/v1/forecast/days:lookup"

    lat = float(lat)
    lon = float(lon)

    params = {
        "key": GOOGLE_API_KEY,
        "location.latitude": lat,
        "location.longitude": lon,
        "days": min(int(days), 10),
        "unitsSystem": "METRIC",
    }

    r = requests.get(url, params=params)

    if DEBUG:
        print(f"DEBUG WEATHER: Status {r.status_code}")
        print(f"DEBUG WEATHER: Response text: {r.text[:200]}")

    if r.status_code != 200:
        return {"error": f"Weather API returned status {r.status_code}: {r.text[:200]}"}

    if not r.text:
        return {"error": "Weather API returned empty response"}

    try:
        data = r.json()
    except Exception as e:
        return {"error": f"Could not parse weather response: {str(e)}"}

    forecast_days = data.get("forecastDays", [])
    if not forecast_days:
        return {"error": f"No forecastDays in response: keys={list(data.keys())}"}

    target = None
    for d in forecast_days:
        disp = d.get("displayDate", {})
        yyyy = disp.get("year")
        mm = disp.get("month") or disp.get("mo") 
        dd = disp.get("day")
        if yyyy and mm and dd:
            candidate = f"{int(yyyy):04d}-{int(mm):02d}-{int(dd):02d}"
            if candidate == date_yyyy_mm_dd:
                target = d
                break

    if not target:
        available = []
        for d in forecast_days[:5]:
            disp = d.get("displayDate", {})
            yyyy = disp.get("year")
            mm = disp.get("month") or disp.get("mo")
            dd = disp.get("day")
            if yyyy and mm and dd:
                available.append(f"{int(yyyy):04d}-{int(mm):02d}-{int(dd):02d}")
        return {"error": f"No forecast found for {date_yyyy_mm_dd}. Available: {available}"}

    max_temp = (
        target.get("maxTemperature", {}).get("degrees")
        or target.get("temperatureMax", {}).get("degrees")
    )
    min_temp = (
        target.get("minTemperature", {}).get("degrees")
        or target.get("temperatureMin", {}).get("degrees")
    )
    conditions = (
        (target.get("daytimeForecast", {}) or {}).get("weatherCondition", {}).get("description")
        or target.get("weatherCondition", {}).get("description")
    )
    precip_prob = (
        (target.get("daytimeForecast", {}) or {}).get("precipitation", {}).get("probability")
        or target.get("precipitation", {}).get("probability")
    )

    return {
        "date": date_yyyy_mm_dd,
        "temp_max_c": max_temp,
        "temp_min_c": min_temp,
        "conditions": conditions,
        "precip_probability": precip_prob,
    }

# --------------------------
# AIR QUALITY TOOL
# --------------------------
@tool
def get_air_quality(lat: float, lon: float) -> dict:
    """Get air quality from Google."""
    url = "https://airquality.googleapis.com/v1/currentConditions:lookup"
    params = {"key": GOOGLE_API_KEY}
    body = {
        "location": {
            "latitude": lat,
            "longitude": lon
        }
    }

    r = requests.post(url, params=params, json=body)

    if DEBUG:
        print(f"DEBUG AQ: Status {r.status_code}")
        print(f"DEBUG AQ: Response text: {r.text[:200]}")

    
    if r.status_code != 200:
        return {"error": f"Air Quality API returned status {r.status_code}: {r.text[:100]}"}
    
    if not r.text:
        return {"error": "Air Quality API returned empty response"}
    
    try:
        data = r.json()
    except Exception as e:
        return {"error": f"Could not parse air quality response: {str(e)}"}

    aqi = data.get("indexes", [{}])[0].get("aqi")
    category = data.get("indexes", [{}])[0].get("category")

    return {
        "aqi": aqi,
        "category": category
    }

# --------------------------
# SEARCH PLACE TOOL
# --------------------------
@tool
def text_search_place(query: str, max_results: int = 5) -> dict:
    """Search for places and return a list of names + formatted addresses."""
    url = "https://places.googleapis.com/v1/places:searchText"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.shortFormattedAddress"
    }

    payload = {
        "textQuery": query,
        "maxResultCount": min(int(max_results), 10),
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        places = data.get("places", [])
        results = []

        for p in places:
            name = (p.get("displayName") or {}).get("text")
            addr = p.get("formattedAddress") or p.get("shortFormattedAddress")
            if name:
                results.append({
            "name": name,
            "address": addr  # may be None
        })
        if not results:
            return {"error": "No places found"}

        return {"results": results}
    


        

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}