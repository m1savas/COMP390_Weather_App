import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from pymeteosource.api import Meteosource
from pymeteosource.types import tiers, sections, langs, units
import sqlite3
import requests
import os


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather App")
        self.root.geometry("400x800")  # Adjusted size for better layout
        self.root.configure(bg="#2b2b2b")  # Set dark background color for a modern look

        # API setup
        self.WEATHER_API_KEY = 'nzhtiyao5q7clib6qjlf3cfio9dcqoq592t8xknf'
        self.GEOCODING_API_KEY = '1253a2456429430ca9da22b1240d1ee1'
        self.TIER = tiers.FREE

        self.meteosource = Meteosource(self.WEATHER_API_KEY, self.TIER)

        self.background_image_path = r"C:\Users\minas\Downloads\cloud-sky.jpg"

        # Set up GUI components
        self.setup_gui()

        if os.path.exists(self.background_image_path):
            self.set_background_image(self.background_image_path)
        else:
            print(f"Background image path does not exist: {self.background_image_path}")

    def setup_gui(self):
        # Input field for city
        frame = tk.Frame(self.root, bg="#2b2b2b")
        frame.place(relx=0.5, rely=0.05, anchor='n')

        self.entry_city = tk.Entry(frame, font=("Helvetica", 14), width=20, fg="#ffffff", bg="#4b4b4b",
                                   insertbackground='white')
        self.entry_city.pack(side="left", padx=10)

        button_search = tk.Button(frame, text="Get Weather", font=("Helvetica", 10), command=self.search_weather,
                                  bg="#ffc107", fg="#2b2b2b")
        button_search.pack(side="right")

        # Current weather display
        self.current_frame = tk.Frame(self.root, bg="#2b2b2b")
        self.current_frame.place(relx=0.5, rely=0.15, relwidth=0.85, relheight=0.3, anchor='n')

        self.weather_icon_label = tk.Label(self.current_frame, bg="#2b2b2b")
        self.weather_icon_label.pack(pady=5)

        self.label_result = tk.Label(self.current_frame, text="", font=("Helvetica", 22, 'bold'), fg="#ffffff",
                                     bg="#2b2b2b")
        self.label_result.pack()

        self.additional_info_label = tk.Label(self.current_frame, text="", font=("Helvetica", 12), fg="#d3d3d3",
                                              bg="#2b2b2b")
        self.additional_info_label.pack(pady=5)

        # Hourly forecast frame
        self.hourly_frame = tk.Frame(self.root, bg="#4b4b4b", bd=5)
        self.hourly_frame.place(relx=0.5, rely=0.55, relwidth=0.9, relheight=0.35, anchor='n')

    #functions to send API keys to tests folder for testing. if there is a better way to do this please tell me. -miah
    def get_api_key_geolocation(self):
        return self.GEOCODING_API_KEY
    def get_api_key_weather(self):
        return self.WEATHER_API_KEY
    
    def set_background_image(self, image_path):
        try:
            image = Image.open(image_path)
            image = image.resize((400, 800), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.background_label = tk.Label(self.root, image=photo)
            self.background_label.place(relwidth=1, relheight=1)
            self.background_label.lower()  # Place the background behind other widgets
            self.background_label.image = photo  # Keep reference
        except Exception as e:
            print(f"Error loading background image: {str(e)}")

    def get_city_coordinates(self, city):
        try:
            url = f"https://api.opencagedata.com/geocode/v1/json?q={city}&key={self.GEOCODING_API_KEY}"
            response = requests.get(url)
            data = response.json()

            if data['results']:
                lat = data['results'][0]['geometry']['lat']
                lon = data['results'][0]['geometry']['lng']
                return lat, lon
            else:
                return None, None
        except Exception as e:
            messagebox.showerror("Error", f"Geocoding failed: {str(e)}")
            return None, None

    def get_weather(self, city):
        try:
            lat, lon = self.get_city_coordinates(city)

            if not lat or not lon:
                messagebox.showwarning("Error", "Could not find coordinates for the entered city.")
                return None

            forecast = self.meteosource.get_point_forecast(
                lat=lat,
                lon=lon,
                sections=[sections.CURRENT, sections.HOURLY],
                lang=langs.ENGLISH,
                units=units.METRIC
            )
            return forecast
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return None

    def load_weather_icon(self, condition):
        icon_path = ""
        if "clear" in condition.lower():
            icon_path = r"C:\Users\minas\Downloads\icons8-clear-sky-64.png"
        elif "cloud" in condition.lower():
            icon_path = r"C:\Users\minas\Downloads\icons8-cloud-48.png"
        elif "rain" in condition.lower():
            icon_path = r"C:\Users\minas\Downloads\icons8-rain-48.png"
        elif "snow" in condition.lower():
            icon_path = r"C:\Users\minas\Downloads\icons8-snow-48.png"
        else:
            icon_path = r"C:\Users\minas\Downloads\icons8-sky-100.png"

        try:
            if os.path.exists(icon_path):
                image = Image.open(icon_path)
                image = image.resize((60, 60), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.weather_icon_label.config(image=photo)
                self.weather_icon_label.image = photo  # Keep reference
            else:
                print(f"Icon path does not exist: {icon_path}")
        except Exception as e:
            print(f"Error loading weather icon: {str(e)}")

    def load_hourly_forecast(self, hourly_data):
        for widget in self.hourly_frame.winfo_children():
            widget.destroy()

        hours_to_display = min(6, len(hourly_data))

        for i in range(hours_to_display):
            hour = hourly_data[i]

            hour_frame = tk.Frame(self.hourly_frame, bg="#2b2b2b", bd=2, relief="ridge")
            hour_frame.pack(side="left", padx=3, pady=3)

            # Extract the time from the data (using 'forecast_time_iso' attribute)
            if hasattr(hour, 'forecast_time_iso'):
                time_str = hour.forecast_time_iso.split('T')[1][:5]
            else:
                time_str = 'N/A'

            time_label = tk.Label(hour_frame, text=time_str, font=("Helvetica", 8), fg="#ffffff", bg="#2b2b2b")
            time_label.pack()

            if hasattr(hour, 'summary'):
                condition = hour.summary.lower()
            else:
                condition = 'unknown'

            icon_path = self.get_hourly_icon(condition)
            try:
                if os.path.exists(icon_path):
                    icon_image = Image.open(icon_path)
                    icon_image = icon_image.resize((20, 20), Image.LANCZOS)
                    icon_photo = ImageTk.PhotoImage(icon_image)
                    icon_label = tk.Label(hour_frame, image=icon_photo, bg="#2b2b2b")
                    icon_label.image = icon_photo  # Keep reference
                    icon_label.pack()
                else:
                    print(f"Hourly icon path does not exist: {icon_path}")
            except Exception as e:
                print(f"Error loading hourly icon: {str(e)}")

            temp_c = getattr(hour, 'temperature', 'N/A')
            temp_f = round((temp_c * 9 / 5) + 32, 1) if temp_c != 'N/A' else 'N/A'
            temp_label = tk.Label(hour_frame, text=f"{temp_f}°F", font=("Helvetica", 8), fg="#ffffff", bg="#2b2b2b")
            temp_label.pack()

    def get_hourly_icon(self, condition):
        if "clear" in condition:
            return r"C:\Users\minas\Downloads\icons8-clear-sky-64.png"
        elif "cloud" in condition:
            return r"C:\Users\minas\Downloads\icons8-cloud-48.png"
        elif "rain" in condition:
            return r"C:\Users\minas\Downloads\icons8-rain-48.png"
        elif "snow" in condition:
            return r"C:\Users\minas\Downloads\icons8-snow-48.png"
        else:
            return r"C:\Users\minas\Downloads\icons8-sky-100.png"

    def search_weather(self):
        city = self.entry_city.get()
        if city:
            weather_data = self.get_weather(city)
            if weather_data:
                current_weather = weather_data.current
                try:
                    temp_c = getattr(current_weather, 'temperature', 'N/A')
                    temp_f = round((temp_c * 9 / 5) + 32, 1) if temp_c != 'N/A' else 'N/A'
                    condition = getattr(current_weather, 'summary', 'N/A')
                    feels_like_c = getattr(current_weather, 'apparent_temperature', 'N/A')
                    feels_like = round((feels_like_c * 9 / 5) + 32, 1) if feels_like_c != 'N/A' else 'N/A'
                    humidity = getattr(current_weather, 'relative_humidity', 'N/A')

                    if hasattr(current_weather, 'wind'):
                        wind_speed_kph = getattr(current_weather.wind, 'speed', 'N/A')
                        wind_speed = round(wind_speed_kph / 1.609, 1) if wind_speed_kph != 'N/A' else 'N/A'
                    else:
                        wind_speed = 'N/A'

                    # Update the main weather display
                    self.label_result.config(text=f"{temp_f}°F")
                    self.additional_info_label.config(text=f"{condition}\nFeels like {feels_like}°F\n"
                                                           f"Humidity: {humidity}%\nWind Speed: {wind_speed} mph")

                    # Load the appropriate weather icon
                    self.load_weather_icon(condition)

                    # Load hourly forecast
                    hourly_data = weather_data.hourly
                    self.load_hourly_forecast(hourly_data)

                    # Save to the database
                    self.save_weather(city, f"{temp_f}°F", condition, f"{humidity}%", f"{wind_speed} mph")

                except AttributeError as e:
                    messagebox.showerror("Error", f"Error accessing weather data: {str(e)}")
        else:
            messagebox.showwarning("Input Error", "Please enter a city name.")

    def save_weather(self, city, temp, condition, humidity, wind_speed):
        conn = sqlite3.connect('weather_data.db')
        c = conn.cursor()
        c.execute("INSERT INTO weather (city, temperature, condition, humidity, wind_speed) VALUES (?, ?, ?, ?, ?)",
                  (city, temp, condition, humidity, wind_speed))
        conn.commit()
        conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
