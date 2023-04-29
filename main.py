import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
from WeatherCat.weather import WeatherService
from WeatherCat.ai import CatService, CatNotCreatedException
from dotenv import load_dotenv
import sqlite3
import io
import matplotlib.pyplot as plt

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
        self.data_count = -1

        self.main.attributes("-fullscreen", True)
        self.main.bind("<Escape>", lambda e: self.close_window())
        self.canvas.tag_bind(self.image_on_canvas, '<Button-1>', lambda e: self.handleClick(e))

        self.main.after(1000, self.fetchWeather)
        #self.main.after(1000 * 60, self.autoRotateImage)
    
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

            
        except (Exception, CatNotCreatedException) as e:
            print(e)
            self.canvas.itemconfig(self.image_on_canvas, image=self.error_image)
            retry_time = 60 * 1
        finally:
            self.main.after(1000 * retry_time, self.fetchWeather)

    def autoRotateImage(self):
        pass
        #self.rotateImage(1)
        #self.main.after(1000 * 60, self.autoRotateImage)

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
        if self.data_count > 2:
            self.data_count = -1
        if self.data_count < -1:
            self.data_count = 2
        self.render_image()

    def rotateImage(self, direction=1):

        self.weather_image_number += direction

        if self.weather_image_number < 0:
            self.weather_image_number = len(self.weather_images) - 1

        if self.weather_image_number == len(self.weather_images):
            self.weather_image_number = 0
        self.render_image()


    def get_chart(self, data_count):
        plt.rcParams["figure.autolayout"] = True

        px = 1/plt.rcParams['figure.dpi']  # pixel in inches
        fig, ax = plt.subplots(figsize=(720*px, 720*px))
        ax = plt.gca()

        forecasts = self.weather_service.last24()

        timings = []
        pressure = []
        temperature = []

        for forecast in forecasts:
            timings.append(forecast.time)
            pressure.append(forecast.pressure)
            temperature.append(forecast.temperature)
        if data_count == 1:
            plt.plot(timings, pressure, color='white',  alpha=0.5, linestyle='dashed', linewidth=4)
        else:
            plt.plot(timings, temperature, color='white', alpha=0.5, linestyle='dashed', linewidth=4)

        fig.patch.set_visible(False)
        ax.get_xaxis().set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)


        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png', transparent=True)

        im = Image.open(img_buf)
        #im.show(title="My Image")
        #img_buf.close()
        return im

    def render_image(self):

        font = ImageFont.truetype("fonts/Rubik-VariableFont_wght.ttf", 75, encoding="unic")
        background = self.weather_images[self.weather_image_number]
        background = background.convert("RGBA")
        image_to_render = Image.new('RGBA',(720, 720),(255,255,255,0))
        draw = ImageDraw.Draw(image_to_render)
        if self.data_count > -1:
            data = [
                "{:.1f}°c".format(self.current_weather.temperature),
                "{0}mb".format(self.current_weather.pressure),
                self.current_weather.description
            ]
            height = 75
            width = draw.textlength(data[self.data_count],font=font)
            draw.rectangle(((720 / 2)-((width / 2) + 20), (720 / 2) - ((height/2)+20), (720 / 2)+((width / 2)+20), (720 / 2)+((height / 2)+20)), fill=(255,255,255,180))
            draw.text((720/2,720/2),data[self.data_count],(38,38,38),font, anchor="mm")
            if self.data_count == 0 or self.data_count == 1:
                image_to_render = Image.alpha_composite(image_to_render, self.get_chart(self.data_count))
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