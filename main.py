from fastapi import FastAPI, Query
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from rapidfuzz import process
import uvicorn
from properties import properties, possible_query

# Initialize FastAPI app
app = FastAPI()

# Create a geolocator instance using Nominatim
geolocator = Nominatim(user_agent="moustache_escapes")

@app.get("/nearest-property")
def get_nearest_property(query: str = Query(..., description="City or area name")):
    """
    Returns the list of properties within a 50km radius of the provided location.
    Uses fuzzy matching to identify the closest city from the CityList.
    """

    # Perform fuzzy matching on user query to find the closest known city
    location_match = process.extractOne(query, possible_query, score_cutoff=70)
    location_to_search = location_match[0] if location_match else query

    try:
        # Geocode the location to get latitude and longitude
        location = geolocator.geocode(location_to_search, timeout=30)
        print(location)  # Debug print (can be removed in production)

        if not location:
            return {"message": "Location not found."}

        user_coords = (location.latitude, location.longitude)
        nearby_properties = []

        # Iterate through the properties to find those within a 50km radius
        for prop in properties:
            prop_coords = (prop["lat"], prop["lon"])
            distance_km = geodesic(user_coords, prop_coords).km

            if distance_km <= 50:
                nearby_properties.append({
                    "property": prop["name"],
                    "distance_km": round(distance_km, 2)
                })

        if not nearby_properties:
            return {"message": "No properties available within 50km radius."}

        # Return the list of nearby properties sorted by distance
        return {"nearby_properties": sorted(nearby_properties, key=lambda x: x["distance_km"])}

    except Exception as e:
        # Return error message if any exception occurs
        return {"error": str(e)}

# Run the app using Uvicorn
if _name_ == "_main_":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)