import requests
from fake_useragent import UserAgent
from geopy.geocoders import Nominatim

def convert_postcode(Postcode):
    GeoLocator = Nominatim(user_agent="postcode_converter")
    location = GeoLocator.geocode(Postcode + ", UK")
    if location:
        return location.latitude, location.longitude
    else:
        print("Could not resolve postcode to coordinates")
        return None, None

def fetch_libraries(Postcode):
    x, y = convert_postcode(Postcode)

    #Creating API call
    q = f"libraries+near+[{x}%2C+{y}]"
    url = f"https://nominatim.openstreetmap.org/search?q={q}&format=json&countrycodes=gb"
    ua = UserAgent()

    headers = {
        'User-Agent': ua.chrome,
        'From': 'hb01262@surrey.ac.uk'
    }
    # Send request
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print("Error: ", response.status_code)
        return None