import os
import requests
from dotenv import load_dotenv
load_dotenv()

WEATHER_API=os.environ.get("WEATHER_API")
LAT = os.environ.get("LAT")
LON = os.environ.get("LON")

class WeatherService():
    def __init__(self):
        pass
    def fetch_weather(self):
        try:
            a = requests.get("https://api.openweathermap.org/data/2.5/weather?lat={0}&lon={1}&appid={2}".format(LAT, LON, WEATHER_API))
            data = a.json()
            print(data)

            weather_description = data['weather'][0]['description']
            temperature = data['main']['temp'] - 273.15
            pressure =  data['main']['pressure']
            return WeatherForecast(temperature, weather_description, pressure)
        
        except Exception as e:
            return "clear sky"

class WeatherForecast():
    def __init__(self, temperature, description, pressure):
        self.temperature = temperature
        self.description = description
        self.pressure = pressure


class WeatherNotLoadedException(Exception):
    """Weather not loaded"""
    pass