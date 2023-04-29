import os
import requests
import urllib.parse as parse
from dotenv import load_dotenv
import time

load_dotenv()
HOST = os.environ.get("HOST")

class WeatherService():
    def __init__(self):
        pass
    def fetch_weather(self):
        try:
            query =  "SELECT max(\"temperature\"), max(\"pressure\") FROM \"forecast\" WHERE time >= now() - 1h GROUP BY time(1h) FILL(linear)"
            a = requests.get("http://{0}:8086/query?prety=true&db=house&q={1}".format(HOST, parse.quote(query)))
            data = a.json()
            temperature = data['results'][0]['series'][0]['values'][1][1]
            pressure =  data['results'][0]['series'][0]['values'][1][2]  

            query = "SELECT description from forecast order by time desc limit 1"
            d = requests.get("http://{0}:8086/query?prety=true&db=house&q={1}".format(HOST, parse.quote(query)))
            data = d.json()

            weather_description = data['results'][0]['series'][0]['values'][0][1]

            return WeatherForecast("", temperature, weather_description, pressure)
        
        except Exception as e:
            print(e)
            return WeatherForecast(-1, "clear sky", -1)

    def last24(self):
        try:
            query = "SELECT max(\"temperature\"), max(\"pressure\") FROM \"forecast\" WHERE time >= now() - 24h GROUP BY time(1h) FILL(linear) LIMIT 24"
            query2 = "select distinct(\"description\") FROM \"forecast\" WHERE time >= now() - 24h GROUP BY time(1h) FILL(linear) LIMIT 24"
            a = requests.get("http://{0}:8086/query?db=house&q={1}".format(HOST, parse.quote("{0};{1}".format(query,query2))))

            data = a.json()
            self.forecasts = []
            
            for i in range(0, len(data['results'][0]['series'][0]['values'])):
                forecast = data['results'][0]['series'][0]['values'][i]
                temperature = forecast[1]
                pressure = forecast[2]
                description = data['results'][1]['series'][0]['values'][i][1]
                time =  forecast[0]
                self.forecasts.append(WeatherForecast(time,temperature,description,pressure))
            return self.forecasts
        except Exception as e:
            print(e)
            return [] 
        
class WeatherForecast():
    def __init__(self, time, temperature, description, pressure):
        self.time = time
        self.temperature = temperature
        self.description = description
        self.pressure = pressure


class WeatherNotLoadedException(Exception):
    """Weather not loaded"""
    pass
