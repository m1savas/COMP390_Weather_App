#unit tests for saving weather for cities in the database
import sqlite3
import pytest
from app.updated_Weather_App import WeatherApp
from os.path import isfile
import os

#make a database class to make a new instance for each testing session that can be deleted after
class database:
    def __init__(self, name):
        try:
            self.connection = sqlite3.connect(name)
        except Exception as e:
            print(e)
            assert False
            
@pytest.fixture
def est_test_conn():
    if isfile("test.db"):
        delete_database_file #if there is already a test.db then clear it out
    return sqlite3.connect('test.db')

@pytest.fixture
def delete_database_file():
    if isfile("test.db"):
        os.remove("test.db")

def test_save_weather(est_test_conn, delete_database_file): #True
    try:
        test_cursor = est_test_conn.cursor()
        test_cursor.execute('''CREATE TABLE IF NOT EXISTS weather
                            (city TEXT, temperature TEXT, condition TEXT, humidity TEXT, wind_speed TEXT)''')
        test_cursor.execute("INSERT INTO weather (city, temperature, condition, humidity, wind_speed) VALUES (london, 20, snow, 100, 40)")
        est_test_conn.commit()
        assert True
    except Exception as e:
        print(e)
        assert False
    est_test_conn.close()
    delete_database_file
