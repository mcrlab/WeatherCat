import requests
import urllib.parse as parse
from dotenv import load_dotenv
import os
load_dotenv()
HOST = os.environ.get("HOST")
DB = os.environ.get("DB")

query = """ SELECT description, temperature, pressure from weather where time > now() limit 1"""

a = requests.get("http://{0}:8086/query?prety=true&db={1}&q={2}".format(HOST, DB, parse.quote(query)))
data = a.json()
print(data['results'][0]['series'][0]['values'][0])
