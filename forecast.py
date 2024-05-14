import requests
import urllib.parse as parse
HOST = "pi4.local"

#query =  "SELECT  FROM \"weather\" where forecasttime = 1683018000 "

query = """ SELECT description, temperature, pressure from weather where time > now() limit 1"""

a = requests.get("http://{0}:8086/query?prety=true&db=weather&q={1}".format(HOST, parse.quote(query)))
data = a.json()
print(data['results'][0]['series'][0]['values'][0])
#temperature =           data['results'][0]['series'][0]['values'][1][1]

#print(temperature)
