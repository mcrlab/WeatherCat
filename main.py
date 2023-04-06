import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
from WeatherCat.weather import WeatherService
from WeatherCat.ai import CatService, CatNotCreatedException
from dotenv import load_dotenv
import sqlite3

load_dotenv()

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

        self.canvas = tk.Canvas(main, width=720, height=720, bd=0, highlightthickness=0, relief='ridge')
        self.canvas.pack()
        self.canvas.grid(row=0, column=0)
        
        self.generate_app_images()        
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor='nw', image=self.loading_image)

        self.show_data = False
        self.main.attributes("-fullscreen", True)
        self.main.bind("<Escape>", lambda e: self.close_window())
        self.main.after(1000 * 5, self.fetchWeather)
        self.main.after(1000 * 60, self.autoRotateImage)
    
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
            self.current_weather =  self.weather_service.fetch_weather()
            weather_description =self.current_weather.description
            self.weather_images = []
            images = self.cat_service.find_cats(weather_description)
            for image in images:
                i = Image.open(image[2])
                resized_image = i.resize((720,720))
                self.weather_images.append(resized_image)
    
            self.weather_image_number = 0
            # set first image on canvas
            self.render_image()

            self.canvas.tag_bind(self.image_on_canvas, '<Button-1>', lambda e: self.handleClick(e))
        except (Exception, CatNotCreatedException) as e:
            print(e)
            self.canvas.itemconfig(self.image_on_canvas, image=self.error_image)
            retry_time = 60 * 1
        finally:
            self.main.after(1000 * retry_time, self.fetchWeather)

    def autoRotateImage(self):
        self.rotateImage(1)
        self.main.after(1000 * 60, self.autoRotateImage)

    def handleClick(self, event):
        point = (event.x, event.y)
        quadrant = where_is_the_click(point)

        match quadrant:
            case 0:
                self.close_window()
            case 1:
                self.rotateImage(1)
            case 2:
                self.show_data = not self.show_data
                self.render_image()
            case 3:
                self.rotateImage(-1)
            case _:
                print("quadrant not clicked")

    def rotateImage(self, direction=1):

        self.weather_image_number += direction

        if self.weather_image_number < 0:
            self.weather_image_number = len(self.weather_images) - 1

        if self.weather_image_number == len(self.weather_images):
            self.weather_image_number = 0
        self.render_image()

    def render_image(self):
        try:
            font = ImageFont.truetype("fonts/Rubik-VariableFont_wght.ttf", 75, encoding="unic")
            background = self.weather_images[self.weather_image_number]
            background = background.convert("RGBA")
            image_to_render = Image.new('RGBA',(720, 720),(255,255,255,0))
            draw = ImageDraw.Draw(image_to_render)
            if self.show_data:
                temperature = "{:.1f}°c".format(self.current_weather.temperature)
                pressure = "{0}mb".format(self.current_weather.pressure)
                description = self.current_weather.description
                width, height = draw.textsize(description,font=font)
                draw.rectangle(((720 / 2)-((width / 2) + 20), (720 / 2) - ((height/2)+20), (720 / 2)+((width / 2)+20), (720 / 2)+((height / 2)+20)), fill=(255,255,255,180))
                draw.text((720/2,720/2),description,(38,38,38),font, anchor="mm")

            out = Image.alpha_composite(background, image_to_render)
            self.current_image = ImageTk.PhotoImage(out)
            self.canvas.itemconfig(self.image_on_canvas, image=self.current_image)
        except Exception as e:
            print("Could not rotate image")
            print(e)
            pass


#----------------------------------------------------------------------
if __name__ == "__main__":
    try:
        root = tk.Tk()
        MainWindow(root)
        root.mainloop()
    except KeyboardInterrupt:
        pass