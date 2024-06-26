import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
from WeatherCat.weather import WeatherService
from WeatherCat.ai import CatService, CatNotCreatedException
from dotenv import load_dotenv
import sqlite3
import matplotlib.pyplot as plt
import os
load_dotenv()
ENV = os.environ.get("ENV")
def in_a_triangle(triangle, point):
    x1,y1 = triangle[0] 
    x2,y2 = triangle[1]
    x3,y3 = triangle[2]
    xp,yp = point

    c1 = (x2-x1)*(yp-y1)-(y2-y1)*(xp-x1)
    c2 = (x3-x2)*(yp-y2)-(y3-y2)*(xp-x2)
    c3 = (x1-x3)*(yp-y3)-(y1-y3)*(xp-x3)
    return (c1<0 and c2<0 and c3<0) or (c1>0 and c2>0 and c3>0)

def where_is_the_click(point):
    
    top = ((0,0),(360,360),(720,0))
    right = ((720,0),(360,360),(720,720))
    bottom = ((0,720),(360,360),(720,720))
    left = ((0,0),(360,360),(0,720))
    triangles = [
        top, right, bottom, left
    ]
    i = -1
    for triangle in triangles:
        i += 1
        if in_a_triangle(triangle, point):
            return i
    return i

class MainWindow():

    #----------------
    
    def __init__(self, main):
        self.main = main
        conn = sqlite3.connect('images.db')
        self.cat_service = CatService(conn)
        self.weather_service = WeatherService()
        self.weather_image_number = 0
        self.canvas = tk.Canvas(main, width=720, height=720, bd=0, highlightthickness=0, relief='ridge')
        self.canvas.pack()
        self.canvas.grid(row=0, column=0)

        self.weather_images = []
        
        self.generate_app_images()        
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor='nw', image=self.loading_image)

        self.show_data = False
        self.data_count = -1
    
        if ENV == "production":
            self.main.attributes("-fullscreen", True)
    
        self.main.bind("<Escape>", lambda e: self.close_window())
        self.canvas.tag_bind(self.image_on_canvas, '<Button-1>', lambda e: self.handleClick(e))

        self.main.after(1000, self.fetchWeather)
        self.main.after(1000 * 60, self.autoRotateImage)
        self.main.after(1000 * 10, self.autoRotateData);
    
    def generate_app_images(self):
        i = Image.open('assets/error.jpg')
        resized_image = i.resize((720,720))
        self.error_image = ImageTk.PhotoImage(resized_image)

        i = Image.open('assets/loading.jpg')
        resized_image = i.resize((720,720))
        self.loading_image = ImageTk.PhotoImage(resized_image)

    #----------------
    def close_window(self):
        msg_box = tk.messagebox.askquestion('Exit Application', 'Are you sure you want to exit the application?',icon='warning')
        if msg_box == 'yes':
            self.main.destroy()

    def fetchWeather(self):
        try:
            retry_time = 60 * 15 # 15 minutes
            self.forecasts =  self.weather_service.fetch_weather()
            weather_description =self.forecasts[0].description
            self.weather_images = []
            images = self.cat_service.find_cats(weather_description)
            for image in images:
                self.weather_images.append(image[2])
    
            self.weather_image_number = 0
            # set first image on canvas
            self.render_image()

            
        except (Exception, CatNotCreatedException) as e:
            print(e)
            self.canvas.itemconfig(self.image_on_canvas, image=self.error_image)
            retry_time = 60 * 1
        finally:
            self.main.after(1000 * retry_time, self.fetchWeather)

    def autoRotateData(self):
        self.rotateData(1)
        self.main.after(1000 * 10, self.autoRotateData)

    def autoRotateImage(self):
        self.rotateImage(1)
        self.main.after(1000 * 60, self.autoRotateImage)

    def handleClick(self, event):
        point = (event.x, event.y)

        if event.x < 100 and event.y < 100:
            self.close_window()
            return

        quadrant = where_is_the_click(point)

        if quadrant == 0:
            self.rotateData(-1)
        elif quadrant == 1:
            self.rotateImage(1)
        elif quadrant == 2:
            self.rotateData(1)
        elif quadrant == 3:
            self.rotateImage(-1)
        else:
            print("quadrant not clicked")
    
    def rotateData(self, direction=1):
        self.data_count += direction
        if self.data_count > 3:
            self.data_count = -1
        if self.data_count < -1:
            self.data_count = 3
        self.render_image()

    def rotateImage(self, direction=1):

        self.weather_image_number += direction

        if self.weather_image_number < 0:
            self.weather_image_number = len(self.weather_images) - 1

        if self.weather_image_number == len(self.weather_images):
            self.weather_image_number = 0
        self.render_image()

    def render_image(self):

        font = ImageFont.truetype("fonts/Rubik-VariableFont_wght.ttf", 75, encoding="unic")
        image_path = self.weather_images[self.weather_image_number]
        i = Image.open(image_path)
        background = i.resize((720,720))
        background = background.convert("RGBA")
        image_to_render = Image.new('RGBA',(720, 720),(255,255,255,0))
        draw = ImageDraw.Draw(image_to_render)
        if self.data_count > -1:
            data = [
                "{0}°c".format(self.forecasts[0].temperature),
                "{0}mb".format(self.forecasts[0].pressure),
                self.forecasts[0].description,
                "{0}%".format(self.forecasts[0].precipitation),
            ]
            height = 75
            width = draw.textlength(data[self.data_count],font=font)
            draw.rectangle(((720 / 2)-((width / 2) + 20), (720 / 2) - ((height/2)+20), (720 / 2)+((width / 2)+20), (720 / 2)+((height / 2)+20)), fill=(255,255,255,180))
            
            draw.text((720/2,720/2),data[self.data_count],(38,38,38),font, anchor="mm")
        draw.rectangle((0, 720 - (720/5), 720, 720), fill=(255,255,255,100))
        small_font = ImageFont.truetype("fonts/Rubik-VariableFont_wght.ttf", 35, encoding="unic")
        for i in range(0,len(self.forecasts)):
            try:
                draw.text((((720/5) * i)+72,720 - (720/10)),"{0}°c".format(self.forecasts[i].temperature),(38,38,38),small_font, anchor="mm")
            except Exception as e:
                draw.text((((720/5) * i)+72,720 - (720/10)),"-",(38,38,38),small_font, anchor="mm")
            pass

        out = Image.alpha_composite(background, image_to_render)
        self.current_image = ImageTk.PhotoImage(out)
        self.canvas.itemconfig(self.image_on_canvas, image=self.current_image)



#----------------------------------------------------------------------
if __name__ == "__main__":
    try:
        root = tk.Tk()
        MainWindow(root)
        root.mainloop()
    except (KeyboardInterrupt, Exception) as e:
        print(e)
        root.destroy()
        pass