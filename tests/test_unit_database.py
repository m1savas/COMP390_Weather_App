#unit tests for saving weather for cities in the database
import sqlite3
import pytest
from app.updated_Weather_App import WeatherApp

      
@pytest.fixture(scope='function')
def est_test_conn():
    test_conn=sqlite3.connect(':memory:')
    test_cursor = test_conn.cursor()
    test_cursor.execute('''CREATE TABLE IF NOT EXISTS weather (city TEXT, temperature TEXT, condition TEXT, humidity TEXT, wind_speed TEXT)''')
    test_cursor.execute("INSERT INTO weather (city, temperature, condition, humidity, wind_speed) VALUES (?, ?, ?, ?, ?)", ("london", 35, "snow", 0.5, 40))
    yield test_conn
    test_conn.close()

def test_save_weather(est_test_conn): #True
    test_cursor=est_test_conn.cursor()
    test_cursor.execute("INSERT INTO weather (city, temperature, condition, humidity, wind_speed) VALUES (?, ?, ?, ?, ?)", ("london", 35, "snow", 0.5, 40))
    est_test_conn.commit()
    test_cursor.execute('SELECT * FROM weather')
    test_result=test_cursor.fetchall()
    assert len(test_result) == 5
