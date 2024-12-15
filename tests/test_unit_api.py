#unit tests for api with the weather provider
import requests
import pytest
from app.updated_Weather_App import WeatherApp
from pymeteosource.api import Meteosource
from pymeteosource.types import tiers, sections, langs, units
import tkinter as tk

#fixtures
@pytest.fixture
def app():
    root = tk.Tk()
    return root
    
@pytest.fixture
def london_forecast_api(app):
    
    try:
        forecast = WeatherApp(app).meteosource.get_point_forecast(
        lat=51.5074456, #london
        lon=-0.1277653, #london
        sections=[sections.CURRENT, sections.HOURLY],
        lang=langs.ENGLISH,
        units=units.METRIC
        )
        yield forecast
    except Exception:
        yield None

@pytest.fixture
def london_response_dot_json(app):
    test_london_json_api_key = WeatherApp(app).get_api_key_geolocation()
    city = "london"
    url = f"https://api.opencagedata.com/geocode/v1/json?q={city}&key={test_london_json_api_key}"
    response = requests.get(url)
    data = response.json()
    yield data

#test methods
def test_get_request_geolocation_city(app): #True
    test_geocoding_api_key = WeatherApp(app).get_api_key_geolocation()
    city = "london"
    url = f"https://api.opencagedata.com/geocode/v1/json?q={city}&key={test_geocoding_api_key}"
    response = requests.get(url)
    assert response.status_code == 200
    
def test_coordinates_from_data(london_response_dot_json): #True
    data = london_response_dot_json
    if data['results']:
        lat = data['results'][0]['geometry']['lat']
        lon = data['results'][0]['geometry']['lng']
        assert (lat == 51.5074456) and (lon == -0.1277653)
    else:
        assert False
    
def test_weather_from_coordinates_temp(london_forecast_api): #True
    try:
        temp_c = getattr(london_forecast_api, 'temperature', 'N/A')
        temp_f = round((temp_c * 9 / 5) + 32, 1) if temp_c != 'N/A' else 'N/A'
        assert -30 <= temp_c <= 60 and -50 <= temp_f <= 120 #sanity check
    except Exception:
        assert False

def test_weather_from_coordinates_condition(london_forecast_api): #True
    try:
        condition = getattr(london_forecast_api, 'summary', 'N/A')
        assert "snow" in condition.lower() or "clear" in condition.lower() or "rain" in condition.lower() or "cloud" in condition.lower()
    except Exception:
        assert False

def test_weather_from_coordinates_humidity(london_forecast_api): #True
    try:
        cloud_cover = getattr(london_forecast_api, 'cloud_cover', 0)
        estimated_humidity = min(100, max(40, round(cloud_cover * 1.2)))
        assert 0 <= estimated_humidity <= 1000 #sanity check as best as I can, I don't understand humidity -Miah
    except Exception:
        assert False

def test_weather_from_coordinates_wind(london_forecast_api): #True
    try:
        if hasattr(london_forecast_api, 'wind'):
            wind_speed_kph = getattr(london_forecast_api.wind, 'speed', 'N/A')
            wind_speed = round(wind_speed_kph / 1.609, 1) if wind_speed_kph != 'N/A' else 'N/A'
        else:
            wind_speed = 'N/A'
        assert wind_speed == 'N/A' or 0 <= wind_speed <= 150 #sanity check
    except Exception:
        assert False
