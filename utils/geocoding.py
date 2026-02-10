import os
import requests

def geocode_adress(address, city, state):
    
    token=os.getenv("MAPBOX_TOKEN")

    query = f"{address},{city},{state}"
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json"

    resp = requests.get(
        url,
        params={ "access_token": token, "limit": 1, "autocomplete": "false",},
        timeout=5,
    )
    resp.raise_for_status()
    data = resp.json()

    features = data.get("features",[])
    if not features:
        return None, None
    
    lon, lat = features[0]["center"]
    
    return float(lat), float(lon)