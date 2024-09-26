import os
import requests
import urllib.parse as parse
from dotenv import load_dotenv


load_dotenv()
HOST = os.environ.get("HOST")
DB   = os.environ.get("DB") 
ENV  = os.environ.get("ENV")

class WeatherService():
    def __init__(self):
        pass

    def fetch_weather(self):
        try:
            query = """select "description", "humidity", "precipitation", "pressure", "temperature", "visibility", "wind description", "wind speed" from weather where time > now() limit 12"""
            a = requests.get("http://{0}:8086/query?prety=true&db={1}&q={2}".format(HOST, DB, parse.quote(query)))
            data = a.json()
            print(data)
            series = data['results'][0]['series'][0]['columns']
            forecastData = data['results'][0]['series'][0]['values']
            forecasts = []
            for forecast in forecastData:
                forecastObject = {}
                x = -1
                for key in series:
                    x = x + 1
                    forecastObject[key]=forecast[x]
                
                forecasts.append(forecastObject)
                
            return forecasts
        
        except Exception as e:
            print(e)
    
class WeatherNotLoadedException(Exception):
    """Weather not loaded"""
    pass
