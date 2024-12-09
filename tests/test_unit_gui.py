#unit tests for gui of the window
from app.updated_Weather_App import WeatherApp
from PIL import Image, ImageTk
import pytest
from pymeteosource.api import Meteosource
from pymeteosource.types import tiers, sections, langs, units
import tkinter as tk
  
#fixtures
@pytest.fixture
def app():
    root = tk.Tk()
    test_app = WeatherApp(root)
    return test_app

@pytest.fixture
def london_forecast_gui(app):
    try:
        forecast = app.meteosource.get_point_forecast(
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
def boston_forecast_gui(app):
    try:
        forecast = app.meteosource.get_point_forecast(
        lat=42.3554334, #boston
        lon=-71.060511, #boston
        sections=[sections.CURRENT, sections.HOURLY],
        lang=langs.ENGLISH,
        units=units.METRIC
        )
        yield forecast
    except Exception:
        yield None

#helper methods
def get_background_image_helper(background_image_path):
    try:
        image = Image.open(background_image_path)
        image = image.resize((400, 700), Image.LANCZOS)
        image = ImageTk.PhotoImage(image)
        yield image
    except Exception:
        yield "Error: no background image at background image path"

def get_icon_image_helper(icon_image_path):
    try:
        image = Image.open(icon_image_path)
        image = image.resize((60, 60), Image.LANCZOS)
        image = ImageTk.PhotoImage(image)
        yield image
    except Exception:
        yield "Error: no icon image at icon image path"

def get_background_path(app):
    path = app.get_background_image_path()
    if path == "Error: no background image path":
        yield None
    else:
        yield path

def get_background_image():
    path = get_background_path
    try:
        image = get_background_image_helper(path)
        if image == "Error: no background image at background image path":
            yield None
        else:
            yield image
    except Exception:
        yield None
    
def get_icon_path(app):
    path = app.get_icon_image_path()
    if path == "Error: no icon image path":
        yield None
    else:
        yield path
    
def get_icon_image():
    path = get_icon_path
    try:
        image = get_icon_image_helper(path)
        if image == "Error: no icon image at icon image path":
            yield None
        else:
            yield image
    except Exception:
        yield None

#tests
def test_window_size(app): #True
    assert app.get_gui_geometry == "400x600"

def test_window_title(app): #True
    assert app.get_gui_title == "Weather App"

def test_background_path_exists(): #True
    path = get_background_path
    if path == None:
        assert False
    else:
        assert True

def test_background_image(): #True
    image = get_background_image()
    if image == None:
        assert False
    else:
        assert True

def test_background_from_image(app): #True
    image = get_background_image
    try:
        image_background = app.get_background_label_dot_image()
        if image_background == "Error: could not set background image":
            assert False
        else:
            assert image == image_background
    except Exception:
        assert False

def test_icon_path_exists(): #True
    path = get_icon_path
    if path == None:
        assert False
    else:
        assert True

def test_icon_image(): #True
    image = get_icon_image
    if image == None:
            assert False
    else:
            assert True

def test_icon_from_image(app): #True
    image = get_icon_image
    try:
        image_icon = app.get_weather_icon_label_dot_image()
        if image_icon == "Error: could not set icon image":
            assert False
        else:
            assert image == image_icon
    except Exception:
        assert False
 
def test_updating_forecast(app): #True
    try:
        app.load_hourly_forecast(london_forecast_gui)
        #what temperature was uploaded for london
        first_temp = app.get_temp_label_text
        
        app.load_hourly_forecast(boston_forecast_gui)
        #what temperature was uploaded for boston
        second_temp = app.get_temp_label_text
        
        #assuming that if the temperatures are the same then it didn't update
        assert first_temp != second_temp
    except Exception as e:
        print(e)
        assert False
