#unit tests
import requests
#import sys #tentatively unneeded?
#sys.path.insert(1, '/COMP390_Weather_App') #tentatively unneeded?
from app.updated_Weather_App import WeatherApp
#TODO it can find the right class but now it's mad about the imports in WeatherApp
   
def api_url_geolocation():
    test_api_url_instance_geolocation = WeatherApp()
    test_geocoding_api_key = test_api_url_instance_geolocation.get_api_key_geolocation(test_api_url_instance_geolocation)
    city = "london"
    url = f"https://api.opencagedata.com/geocode/v1/json?q={city}&key={test_geocoding_api_key}"
    return url

def api_url_weather():
    test_api_url_instance_weather = WeatherApp()
    test_weather_api_key = test_api_url_instance_weather.get_api_key_weather(test_api_url_instance_weather)
    #need other files?
   
def test_get_request(url): #TRUE
    #url must be a string
    response = requests.get(url)
    assert response.status_code == 200
    
    


