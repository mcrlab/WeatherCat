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
    def fetch_description(self):
        try:
            a = requests.get("https://api.openweathermap.org/data/2.5/weather?lat={0}&lon={1}&appid={2}".format(LAT, LON, WEATHER_API))
            data = a.json()
            weather_description = data['weather'][0]['description']
            return weather_description
        except Exception as e:
            return "clear sky"