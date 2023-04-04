from tkinter import *
from PIL import Image, ImageTk, ImageDraw, ImageFont
from WeatherCat.weather import WeatherService
from WeatherCat.ai import CatService
from dotenv import load_dotenv
import sqlite3

load_dotenv()

class MainWindow():

    #----------------
    
    def __init__(self, main):
        self.main = main
        conn = sqlite3.connect('images.db')
        self.cat_service = CatService(conn)
        self.weather_service = WeatherService()

        self.canvas = Canvas(main, width=720, height=720, bd=0, highlightthickness=0, relief='ridge')
        self.canvas.pack()
        self.canvas.grid(row=0, column=0)
        
        self.fetchWeather()
        self.main.attributes("-fullscreen", True)
        self.main.bind("<Escape>", lambda e: self.close_window())
        self.main.after(1000 * 30, self.autoRotateImage)

    #----------------
    def close_window(self):
        self.main.destroy()

    def fetchWeather(self):
        weather_description = self.weather_service.fetch_description()
        self.weather_images = []
        images = self.cat_service.find_cats(weather_description)
        for image in images:
            i = Image.open(image[2])
            resized_image = i.resize((720,720))
            #font = ImageFont.truetype("OpenSans-Bold.ttf", 70)
            #draw = ImageDraw.Draw(resized_image)
            #draw.text((28, 36), image[1], fill=(30, 30, 30),font=font)
            self.weather_images.append(ImageTk.PhotoImage(resized_image))
 
        self.weather_image_number = 0
        # set first image on canvas
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor='nw', image=self.weather_images[self.weather_image_number])
        self.canvas.tag_bind(self.image_on_canvas, '<Double-Button-1>', lambda e: self.close_window())
        self.canvas.tag_bind(self.image_on_canvas, '<Button-1>', lambda e: self.rotateImage())
        self.main.after(1000 * 60 * 30, self.fetchWeather)

    def autoRotateImage(self):
        self.rotateImage()
        self.main.after(1000 * 30, self.rotateImage)

    def rotateImage(self):
        
        # next image
        self.weather_image_number += 1

        # return to first image
        if self.weather_image_number == len(self.weather_images):
            self.weather_image_number = 0
        print("rendering {0}".format(self.weather_images[self.weather_image_number]))
        # change image
        self.canvas.itemconfig(self.image_on_canvas, image=self.weather_images[self.weather_image_number])
        


#----------------------------------------------------------------------
if __name__ == "__main__":
    root = Tk()
    MainWindow(root)
    root.mainloop()
