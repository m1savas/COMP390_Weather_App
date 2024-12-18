import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from pymeteosource.api import Meteosource
from pymeteosource.types import tiers, sections, langs, units
import sqlite3
import requests
import os
import logging
from datetime import datetime

# Set up logging with less verbose output
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


class RoundedFrame(tk.Canvas):
    def __init__(self, parent, bg_color="#2b2b2b", corner_radius=15, **kwargs):
        tk.Canvas.__init__(self, parent, bg=parent["bg"], highlightthickness=0, **kwargs)
        self.bg_color = bg_color
        self.corner_radius = corner_radius
        self.bind('<Configure>', self._on_resize)

    def _on_resize(self, event):
        self.delete("rounded_frame")
        width = event.width
        height = event.height
        self.create_rounded_rect(0, 0, width, height, self.corner_radius)

    def create_rounded_rect(self, x1, y1, x2, y2, radius):
        self.create_polygon(
            x1 + radius, y1,
            x1 + radius, y1,
            x2 - radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
            smooth=True,
            fill=self.bg_color
        )


class ModernButton(tk.Button):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=8,
            font=("Helvetica", 10, "bold"),
            cursor="hand2"
        )

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['background'] = '#ffcd38'  # Lighter shade for hover

    def on_leave(self, e):
        self['background'] = '#ffc107'  # Original color


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather App")
        self.root.geometry("400x600")  # Slightly reduced height
        self.root.configure(bg="#1a237e")  # Dark blue background

        # API setup remains the same
        self.WEATHER_API_KEY = 'nzhtiyao5q7clib6qjlf3cfio9dcqoq592t8xknf'
        self.GEOCODING_API_KEY = '1253a2456429430ca9da22b1240d1ee1'
        self.TIER = tiers.FREE
        self.meteosource = Meteosource(self.WEATHER_API_KEY, self.TIER)
        self.background_image_path = r"C:\Users\minas\Downloads\night-with-clouds-weather-app-screen-mobile-interface-design-forecast-weather-background-time-concep.jpg"

        # Initialize animation variables
        self.loading = False
        self.fade_counter = 0

        self.setup_gui()
        if os.path.exists(self.background_image_path):
            self.set_background_image(self.background_image_path)

    #functions to send variables to tests folder for testing. if there is a better way to do this please tell me. -Miah
    def get_api_key_geolocation(self):
        return self.GEOCODING_API_KEY
    def get_api_key_weather(self):
        return self.WEATHER_API_KEY
    
    def get_gui_geometry(self):
        return self.root.geometry
    def get_gui_title(self):
        return self.root.title
    
    def get_background_image_path(self):
        if os.path.exists(self.background_image_path):
            return self.background_image_path
        else:
            return "Error: no background image path"
    def get_background_label_dot_image(self):
        self.get_background_image_path(self)
        try:
            self.set_background_image(self, self.background_image_path)
            return self.background_label.cget("image")
        except Exception:
                return "Error: could not set background image"
    
    def get_icon_image_path(self):
        try:
            if os.path.exists(r"C:\Users\minas\Downloads\icons8-snow-48.png:"): #snow
                return r"C:\Users\minas\Downloads\icons8-snow-48.png:"
            else:
                return "Error: no icon image path"
        except Exception:
            return "Error: no icon image path"
    def get_weather_icon_label_dot_image(self):
        self.get_icon_image_path(self)
        try:
            self.load_weather_icon(self, "snow")
            return self.weather_icon_label.cget("image")
        except Exception:
            return "Error: could not set icon image"
    
    def get_temp_label_text(self):
        return self.label_result.cget("text")
    #end of functions that send variables to tests folder for testing
    
    def set_background_image(self, image_path):
        try:
            image = Image.open(image_path)
            image = image.resize((400, 700), Image.LANCZOS)  # Updated to match new window size
            photo = ImageTk.PhotoImage(image)
            self.background_label = tk.Label(self.root, image=photo)
            self.background_label.place(relwidth=1, relheight=1)
            self.background_label.lower()
            self.background_label.image = photo
        except Exception as e:
            logging.error(f"Error loading background image: {str(e)}")

    def get_city_coordinates(self, city):
        try:
            url = f"https://api.opencagedata.com/geocode/v1/json?q={city}&key={self.GEOCODING_API_KEY}"
            response = requests.get(url)
            data = response.json()

            if data['results']:
                lat = data['results'][0]['geometry']['lat']
                lon = data['results'][0]['geometry']['lng']
                logging.info(f"Retrieved coordinates for {city}")
                return lat, lon
            else:
                logging.warning(f"No coordinates found for city: {city}")
                return None, None
        except Exception as e:
            logging.error(f"Geocoding failed: {str(e)}")
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
            logging.error(f"Error getting weather data: {str(e)}")
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
                self.weather_icon_label.image = photo
            else:
                logging.warning(f"Icon path does not exist: {icon_path}")
        except Exception as e:
            logging.error(f"Error loading weather icon: {str(e)}")

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
                    # Temperature
                    temp_c = getattr(current_weather, 'temperature', 'N/A')
                    temp_f = round((temp_c * 9 / 5) + 32, 1) if temp_c != 'N/A' else 'N/A'

                    # Condition
                    condition = getattr(current_weather, 'summary', 'N/A')

                    # Calculate humidity from cloud cover
                    cloud_cover = getattr(current_weather, 'cloud_cover', 0)
                    estimated_humidity = min(100, max(40, round(cloud_cover * 1.2)))

                    # Wind speed
                    if hasattr(current_weather, 'wind'):
                        wind_speed_kph = getattr(current_weather.wind, 'speed', 'N/A')
                        wind_speed = round(wind_speed_kph / 1.609, 1) if wind_speed_kph != 'N/A' else 'N/A'
                    else:
                        wind_speed = 'N/A'

                    # Update display
                    self.label_result.config(text=f"{temp_f}°F")
                    self.additional_info_label.config(
                        text=f"{condition}\n"
                             f"Est. Humidity: {estimated_humidity}%\n"
                             f"Cloud Cover: {cloud_cover}%\n"
                             f"Wind Speed: {wind_speed} mph"
                    )

                    self.load_weather_icon(condition)
                    self.load_hourly_forecast(weather_data.hourly)
                    self.save_weather(city, f"{temp_f}°F", condition, f"{estimated_humidity}%", f"{wind_speed} mph")

                except AttributeError as e:
                    logging.error(f"Error accessing weather data: {str(e)}")
                    messagebox.showerror("Error", f"Error accessing weather data: {str(e)}")
        else:
            messagebox.showwarning("Input Error", "Please enter a city name.")

    def save_weather(self, city, temp, condition, humidity, wind_speed):
        try:
            conn = sqlite3.connect('weather_data.db')
            c = conn.cursor()

            c.execute('''CREATE TABLE IF NOT EXISTS weather
                        (city TEXT, temperature TEXT, condition TEXT, humidity TEXT, wind_speed TEXT)''')

            c.execute("INSERT INTO weather (city, temperature, condition, humidity, wind_speed) VALUES (?, ?, ?, ?, ?)",
                      (city, temp, condition, humidity, wind_speed))
            conn.commit()
            logging.info(f"Weather data saved for {city}")
        except Exception as e:
            logging.error(f"Database error: {str(e)}")
        finally:
            conn.close()

    def setup_gui(self):
        self.search_frame = RoundedFrame(self.root, bg_color="#2b2b2b", corner_radius=15)
        self.search_frame.place(relx=0.5, rely=0.03, relwidth=0.85, height=35, anchor='n')  # Reduced height and moved up

        # Smaller entry field
        self.entry_city = tk.Entry(
            self.search_frame,
            font=("Helvetica", 12),  # Reduced font size
            bg="#4b4b4b",
            fg="white",
            insertbackground='white',
            relief="flat",
            bd=0
        )
        self.entry_city.place(relx=0.02, rely=0.5, relwidth=0.7, height=30, anchor='w')

        # Smaller search button
        self.search_button = ModernButton(
            self.search_frame,
            text="Get Weather",
            bg="#ffc107",
            fg="#2b2b2b",
            command=self.animate_search,
            font=("Helvetica", 9, "bold")  # Reduced font size
        )
        self.search_button.place(relx=1, rely=0.5, anchor='e')

        # Current weather frame
        self.current_frame = RoundedFrame(self.root, bg_color="#2b2b2b", corner_radius=20)
        self.current_frame.place(relx=0.5, rely=0.12, relwidth=0.9, relheight=0.35,
                                 anchor='n')  # Adjusted position and height

        # Weather icon
        self.weather_icon_label = tk.Label(self.current_frame, bg="#2b2b2b")
        self.weather_icon_label.place(relx=0.5, rely=0.2, anchor='center')

        # Smaller temperature display
        self.label_result = tk.Label(
            self.current_frame,
            text="",
            font=("Helvetica", 36, 'bold'),  # Reduced font size
            fg="#ffffff",
            bg="#2b2b2b"
        )
        self.label_result.place(relx=0.5, rely=0.5, anchor='center')

        # Additional info with smaller font
        self.additional_info_label = tk.Label(
            self.current_frame,
            text="",
            font=("Helvetica", 10),  # Reduced font size
            fg="#d3d3d3",
            bg="#2b2b2b",
            justify='center'
        )
        self.additional_info_label.place(relx=0.5, rely=0.8, anchor='center')

        # Hourly forecast frame - moved down and adjusted height
        self.hourly_frame = RoundedFrame(self.root, bg_color="#2b2b2b", corner_radius=20)
        self.hourly_frame.place(relx=0.5, rely=0.55, relwidth=0.9, relheight=0.25, anchor='n')  # Adjusted position

    def animate_search(self):
        if not self.loading:
            self.loading = True
            self.fade_counter = 0
            self.search_button.configure(state='disabled')
            self.root.after(50, self.fade_out)

    def fade_out(self):
        if self.fade_counter < 10:
            alpha = 1 - (self.fade_counter / 10)
            self.label_result.configure(fg=f"#{int(255 * alpha):02x}{int(255 * alpha):02x}{int(255 * alpha):02x}")
            self.fade_counter += 1
            self.root.after(20, self.fade_out)
        else:
            self.search_weather()
            self.fade_counter = 0
            self.root.after(20, self.fade_in)

    def fade_in(self):
        if self.fade_counter < 10:
            alpha = self.fade_counter / 10
            self.label_result.configure(fg=f"#{int(255 * alpha):02x}{int(255 * alpha):02x}{int(255 * alpha):02x}")
            self.fade_counter += 1
            self.root.after(20, self.fade_in)
        else:
            self.loading = False
            self.search_button.configure(state='normal')

    def load_hourly_forecast(self, hourly_data): #this is the new version of the method, I am assuming -Miah
        for widget in self.hourly_frame.winfo_children():
            widget.destroy()

        hours_to_display = min(6, len(hourly_data))

        # Create a container frame for the hourly forecasts
        container = tk.Frame(self.hourly_frame, bg="#2b2b2b")
        container.place(relx=0.5, rely=0.1, relwidth=0.95, relheight=0.8, anchor='n')

        for i in range(hours_to_display):
            # Create individual hour frame with rounded corners
            hour_frame = RoundedFrame(container, bg_color="#3b3b3b", corner_radius=10)
            hour_frame.place(relx=i / hours_to_display, rely=0,
                             relwidth=1 / hours_to_display - 0.02, relheight=1)

            hour = hourly_data[i]

            if hasattr(hour, 'date'):
                time_str = hour.date.strftime('%I:%M %p').lstrip('0')
            else:
                time_str = 'N/A'

            # Time label
            time_label = tk.Label(
                hour_frame,
                text=time_str,
                font=("Helvetica", 10, "bold"),
                fg="#ffffff",
                bg="#3b3b3b"
            )
            time_label.place(relx=0.5, rely=0.15, anchor='center')

            # Weather icon
            if hasattr(hour, 'summary'):
                condition = hour.summary.lower()
                icon_path = self.get_hourly_icon(condition)
                try:
                    if os.path.exists(icon_path):
                        icon_image = Image.open(icon_path)
                        icon_image = icon_image.resize((30, 30), Image.LANCZOS)
                        icon_photo = ImageTk.PhotoImage(icon_image)
                        icon_label = tk.Label(hour_frame, image=icon_photo, bg="#3b3b3b")
                        icon_label.image = icon_photo
                        icon_label.place(relx=0.5, rely=0.5, anchor='center')
                except Exception as e:
                    logging.error(f"Error loading hourly icon: {str(e)}")

            # Temperature
            temp_c = getattr(hour, 'temperature', 'N/A')
            temp_f = round((temp_c * 9 / 5) + 32, 1) if temp_c != 'N/A' else 'N/A'
            temp_label = tk.Label(
                hour_frame,
                text=f"{temp_f}°F",
                font=("Helvetica", 12, "bold"),
                fg="#ffffff",
                bg="#3b3b3b"
            )
            temp_label.place(relx=0.5, rely=0.85, anchor='center')

    # [Previous methods remain the same: get_city_coordinates, get_weather, load_weather_icon,
    # get_hourly_icon, search_weather, save_weather, set_background_image]


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
