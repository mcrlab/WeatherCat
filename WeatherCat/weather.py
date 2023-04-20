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
            a = requests.get("http://pi4.local:8086/query?prety=true&db=house&q=SELECT%20max(%22temperature%22),%20max(%22pressure%22)%20FROM%20%22forecast%22%20WHERE%20time%20%3E=%20now()%20-%201h%20GROUP%20BY%20time(1h)%20FILL(linear)")
            data = a.json()
            print(data)
            temperature = data['results'][0]['series'][0]['values'][1][1]
            pressure =  data['results'][0]['series'][0]['values'][1][2]  

            d = requests.get("http://pi4.local:8086/query?prety=true&db=house&q=SELECT%20description%20from%20forecast%20order%20by%20time%20desc%20limit%201")
            data = d.json()

            weather_description = data['results'][0]['series'][0]['values'][0][1]

            return WeatherForecast(temperature, weather_description, pressure)
        
        except Exception as e:
            print(e)
            return WeatherForecast(-1, "clear sky", -1)

class WeatherForecast():
    def __init__(self, temperature, description, pressure):
        self.temperature = temperature
        self.description = description
        self.pressure = pressure


class WeatherNotLoadedException(Exception):
    """Weather not loaded"""
    pass


class ForecastDirectory():
    def __init__(self, conn):
        self.conn = conn
        c = self.conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS forecast (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            pressure FLOAT, 
            temperature FLOAT,
            description TEXT,
            t TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
        
    def insert(self, forecast):
        c = self.conn.cursor()
        
        c.execute("INSERT INTO forecast (pressure, temperature, description) VALUES (?,?,?)", (forecast.pressure, forecast.temperature, forecast.description))
        self.conn.commit()
        pass
    
    def last(self):
        a = requests.get("http://pi4.local:8086/query?prety=true&db=house&q=SELECT%20max(%22temperature%22),%20max(%22pressure%22)%20FROM%20%22forecast%22%20WHERE%20time%20%3E=%20now()%20-%2024h%20GROUP%20BY%20time(1h)%20FILL(linear)")
        data = a.json()
        print(data)
        results = []
        for value in data['results'][0]['series'][0]['values']:
            results.append(("",value[2],value[1],"",value[0]))
        return results
    
        c = self.conn.cursor()
        c.execute("SELECT * FROM forecast LIMIT 20")
        output = c.fetchall()
        return output
    