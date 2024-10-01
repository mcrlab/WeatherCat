import tkinter as tk
from tkinter import messagebox
from WeatherCat.weathermodel import WeatherModel
from WeatherCat.weatherview import WeatherView
from assistant import Assistant
from WeatherCat.weather import WeatherService
from WeatherCat.ai import CatService, CatNotCreatedException
import sqlite3
from dotenv import load_dotenv
import os
from PIL import Image

load_dotenv()
ENV = os.environ.get("ENV")


class WeatherController:
    def __init__(self, root):
        self.root = root
        self.model = WeatherModel()
        self.view = WeatherView(root, self)
        self.assistant = Assistant()
        self.weather_service = WeatherService()
        conn = sqlite3.connect('images.db')
        self.cat_service = CatService(conn)
        self.root.bind("<Escape>", lambda e: self.close_window())
        self.background_image = Image.open('assets/loading.jpg')
        self.view.render_image("Loading...", self.background_image)

        if ENV == "production":
            self.root.attributes("-fullscreen", True)

        self.root.after(500, self.fetchWeather)
        self.root.after(10 * 1000, self.autoRotateImage)


    def handleClick(self, event):
        point = (event.x, event.y)

        if event.x < 100 and event.y < 100:
            self.close_window()
            return

        quadrant = self.view.where_is_the_click(point)
  
        if (quadrant == 0):
            self.rotateData(-1)
        elif (quadrant == 1):
            self.rotateImage(1)
        elif (quadrant ==  2):
            self.rotateData(1)
        elif (quadrant ==  3):
            self.rotateImage(-1)
                
    def fetchWeather(self):
        try:
            retry_time = 60 * 60
            self.model.set_forecasts(self.weather_service.fetch_weather())
            self.model.set_summary(self.assistant.summarise(self.model.get_forecasts()))
            latest_description =self.model.get_latest_forecast()['description']
            self.model.set_images(self.cat_service.find_cats(latest_description))
            image = self.model.next_image()
            self.view.render_image(self.model.get_summary(), image)
            pass
        except Exception as e:
            pass
        finally:
            self.root.after(1000 * retry_time, self.fetchWeather)
            pass

    def rotateData(self, direction=1):
        image = self.model.current_image()
        text = self.model.next_description(direction)
        self.view.render_image(text, image)
        pass

    def rotateImage(self, direction=1):
        image = self.model.next_image(direction)
        text = self.model.get_description()
        self.view.render_image(text, image)
        pass

    def autoRotateImage(self):
        self.root.after(10 * 1000, self.rotateImage)

    def close_window(self):
        msg_box = messagebox.askquestion('Exit Application', 'Are you sure you want to exit the application?',icon='warning')
        if msg_box == 'yes':
            self.root.destroy()
