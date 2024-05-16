import os
import requests
import urllib.parse as parse
from dotenv import load_dotenv
import time
import json

load_dotenv()
HOST = os.environ.get("HOST")
DB   = os.environ.get("DB") 
ENV  = os.environ.get("ENV")

class WeatherService():
    def __init__(self):
        pass
    def fetch_weather(self):
        try:
            if ENV == 'development':
                f = open("./sample.json", "r");
                d = f.read()
                f.close()
                data = json.loads(d)
            else:
                query = """ SELECT temperature, pressure, description, precipitation from weather where time > now() limit 1"""
                a = requests.get("http://{0}:8086/query?prety=true&db={1}&q={2}".format(HOST, DB, parse.quote(query)))
                data = a.json()

            forecast_time =         data['results'][0]['series'][0]['values'][0][0]
            temperature =           data['results'][0]['series'][0]['values'][0][1]
            pressure =              data['results'][0]['series'][0]['values'][0][2]
            weather_description =   data['results'][0]['series'][0]['values'][0][3]
            precipitation =         data['results'][0]['series'][0]['values'][0][4]

            return WeatherForecast(forecast_time, temperature, weather_description, pressure, precipitation)
        
        except Exception as e:
            print(e)
            return WeatherForecast("", -1, "clear sky", -1)
        
class WeatherForecast():
    def __init__(self, time, temperature, description, pressure, precipitation):
        self.time = time
        self.temperature = temperature
        self.description = description
        self.pressure = pressure
        self.precipitation = precipitation


class WeatherNotLoadedException(Exception):
    """Weather not loaded"""
    pass
