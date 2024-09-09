from openai import OpenAI
from dotenv import load_dotenv
from WeatherCat import weather
import json

load_dotenv()

class Assistant():
    def __init__(self):
        self.client = OpenAI()
    
    def summarise(self, forecasts):
        json_data = json.dumps(forecasts, default=lambda x: x.__dict__)
        request = "summarise the weather in 100 characters from the following json structure " + json_data

        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system", "content":"you are a helpful weather assistant"},
                {
                    "role":"user",
                    "content": request
                }
            ]
        )

        return completion.choices[0].message.content