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
            if ENV == 'development!':
                print('loading dev data')
                f = open("./sample.json", "r");
                d = f.read()
                f.close()
                data = json.loads(d)
            else:
                query = """ SELECT temperature, pressure, description, precipitation, humidity, "wind description" from weather where time > now() limit 12"""
                a = requests.get("http://{0}:8086/query?prety=true&db={1}&q={2}".format(HOST, DB, parse.quote(query)))
                data = a.json()
            print(data)
            forecasts = []
            for i in range(0,11):
                forecast_time =         data['results'][0]['series'][0]['values'][i][0]
                temperature =           data['results'][0]['series'][0]['values'][i][1]
                pressure =              data['results'][0]['series'][0]['values'][i][2]
                weather_description =   data['results'][0]['series'][0]['values'][i][3]
                precipitation =         data['results'][0]['series'][0]['values'][i][4]
                humidity =              data['results'][0]['series'][0]['values'][i][5]
                wind_description =      data['results'][0]['series'][0]['values'][i][6]
                
                forecasts.append(WeatherForecast(forecast_time, temperature, weather_description, pressure, precipitation, humidity, wind_description))
            print(len(forecasts))
            return forecasts
        
        except Exception as e:
            print(e)
            return WeatherForecast("", -1, "clear sky", -1)
        
class WeatherForecast(object):
    def __init__(self, time, temperature, description, pressure, precipitation, humidty, wind_description):
        self.time = time
        self.temperature = temperature
        self.description = description
        self.pressure = pressure
        self.precipitation = precipitation
        self.humidity = humidty
        self.wind_description = wind_description

    def serialize(self):
        return self.__dict__
    
class WeatherNotLoadedException(Exception):
    """Weather not loaded"""
    pass
