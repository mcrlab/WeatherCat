import openai
import shutil
from slugify import slugify
from WeatherCat.imageservice import ImageDirectory
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()
openai.organisation = os.getenv('ORG')
openai.api_key = os.getenv("OPENAI_API_KEY")


class CatService():
    def __init__(self, conn):  
        self.directory = ImageDirectory(conn)
        pass
    
    def find_cats(self, description):
        images = self.directory.find(description)
        if len(images) > 10:
            #cat images found
            return images
        else:
            # no images for that found - create a new one
            images = self.create_cat(description)
        return images
    
    def generate_cat_image(self, weather_description):
        try:
            print("creating new cat image for: {0}".format(weather_description))
            prompt = "some cats in {0}".format(weather_description)

            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="512x512"
            )
            image_url = response['data'][0]['url']
            return image_url
        except Exception as e:
            raise Exception("Failed to generate a cat image")
            
    def create_cat(self, weather_description):
        try:
            image_url = self.generate_cat_image(weather_description)
            file_name = "images/{0}-{1}.jpg".format(slugify(weather_description), round(time.time()*1000))

            res = requests.get(image_url, stream=True)

            if res.status_code == 200:
                with open(file_name,'wb') as f:
                    shutil.copyfileobj(res.raw, f)
                print('image successfully downloaded: ', file_name)
            else:
                print('image couldn\'t be retrieved')

            self.directory.insert(weather_description, file_name)
            return self.directory.find(weather_description)
        except Exception as e:
            raise CatNotCreatedException("Can't generate a new cat")
        

class CatNotCreatedException(Exception):
    "cat could not be created"
    pass