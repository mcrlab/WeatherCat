import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
from WeatherCat.weather import WeatherService
from WeatherCat.ai import CatService, CatNotCreatedException
from dotenv import load_dotenv
import sqlite3
import os
from assistant import Assistant

load_dotenv()
ENV = os.environ.get("ENV")

    
class WeatherModel:
    def __init__(self):
        self.forecasts = []
        self.images = []
        self.summary = ""
        self.image_index = -1
        pass

    def set_forecasts(self, forecasts):
        self.forecasts = forecasts
    
    def get_forecasts(self):
        return self.forecasts
    
    def get_latest_forecast(self):
        return self.forecasts[0]
    
    def set_summary(self, summary):
        self.summary = summary
    
    def get_summary(self):
        return self.summary
    
    def set_images(self, images):
        self.images = images
    
    def current_image(self):
        return self.images[self.image_index][2]
    
    def next_image(self):
        self.image_index = self.image_index + 1
        if(self.image_index > len(self.images)):
            self.image_index = 0
        return self.images[self.image_index][2]
    

class WeatherView:
    def __init__(self, root, controller):
        self.controller = controller
        i = Image.open('assets/loading.jpg')
        resized_image = i.resize((720,720))
        self.loading_image = ImageTk.PhotoImage(resized_image)
        
        self.canvas = tk.Canvas(root, width=720, height=720, bd=0, highlightthickness=0, relief='ridge')
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor='nw', image=self.loading_image)
        self.canvas.pack()
        self.canvas.grid(row=0, column=0)
        self.canvas.tag_bind(self.image_on_canvas, '<Button-1>', lambda e: self.controller.handleClick(e))

        pass

    def in_a_triangle(self, triangle, point):
        x1,y1 = triangle[0] 
        x2,y2 = triangle[1]
        x3,y3 = triangle[2]
        xp,yp = point

        c1 = (x2-x1)*(yp-y1)-(y2-y1)*(xp-x1)
        c2 = (x3-x2)*(yp-y2)-(y3-y2)*(xp-x2)
        c3 = (x1-x3)*(yp-y3)-(y1-y3)*(xp-x3)
        return (c1<0 and c2<0 and c3<0) or (c1>0 and c2>0 and c3>0)

    def where_is_the_click(self, point):
        
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
            if self.in_a_triangle(triangle, point):
                return i
        return i

        
    def render_image(self, message, background):        
        line_height = 50
        font = ImageFont.truetype("fonts/Rubik-VariableFont_wght.ttf", line_height, encoding="unic")

        self.data_count = 0
        background = background.resize((720,720))
        background = background.convert("RGBA")
        image_to_render = Image.new('RGBA',(720, 720),(255,255,255,0))
        draw = ImageDraw.Draw(image_to_render)

        words = message.split(" ")
        lines = []
        i = 0
        line =  ""
        content = ""
        for word in words:
            if draw.textlength(line + word, font) < 650:
                line = line + word + " "
            else:
                lines.append(line)
                line = word + " "
        lines.append(line)
 
        content = "\n".join(lines)

        widest = 0
        for i in content.split('\n'):    
            text_width = draw.textlength(i,font=font)
            if text_width > widest:
                widest = text_width
                
        width = widest

        height = (line_height/2) * len(lines)
        draw.rectangle(((720 / 2)-((width / 2) + 20), (720 / 2) - (height+20), (720 / 2)+((width / 2)+20), (720 / 2)+(height+20)), fill=(255,255,255,180))    
        draw.text((720/2,720/2), content, (38,38,38), font, anchor="mm")

        out = Image.alpha_composite(background, image_to_render)
        self.current_image = ImageTk.PhotoImage(out)
        self.canvas.itemconfig(self.image_on_canvas, image=self.current_image)

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

        self.root.after(1000, self.fetchWeather)
        #self.main.after(1000 * 60, self.autoRotateImage)

    def handleClick(self, event):
        point = (event.x, event.y)

        if event.x < 100 and event.y < 100:
            self.controller.close_window()
            return

        quadrant = self.view.where_is_the_click(point)
        self.rotateImage()
        print(quadrant)

    def fetchWeather(self):
        try:
            retry_time = 60 * 60
            self.model.set_forecasts(self.weather_service.fetch_weather())
            self.model.set_summary(self.assistant.summarise(self.model.get_forecasts()))
            latest_description =self.model.get_latest_forecast().description
            self.model.set_images(self.cat_service.find_cats(latest_description))
            image = Image.open(self.model.next_image())
            self.view.render_image(self.model.get_summary(), image)
            pass
        except Exception as e:
            pass
        finally:
            pass
            self.root.after(1000 * retry_time, self.fetchWeather)

    def rotateData(self):
        pass

    def rotateImage(self):
        image = Image.open(self.model.next_image())
        self.view.render_image(self.model.get_summary(), image)
        pass

    def autoRotateImage(self):
        pass
    
    def autoRotateData(self):
        pass

    def close_window(self):
        msg_box = tk.messagebox.askquestion('Exit Application', 'Are you sure you want to exit the application?',icon='warning')
        if msg_box == 'yes':
            self.root.destroy()

#----------------------------------------------------------------------
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = WeatherController(root)
        root.mainloop()
    except (KeyboardInterrupt, Exception) as e:
        print(e)
        root.destroy()
        pass