# animation.py

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import os
import time
load_dotenv()
ENV = os.environ.get("ENV")
fps = 10
def current_milli_time():
    return round(time.time() * 1000)

class MainWindow():

    #----------------
    
    def __init__(self, main):
        self.main = main
        self.canvas = tk.Canvas(main, width=720, height=720, bd=0, highlightthickness=0, relief='ridge')
        self.canvas.pack()
        self.canvas.grid(row=0, column=0)
        self.y = 10
        self.direction = 100
        self.last_render = current_milli_time()
        
        i = Image.open('assets/loading.jpg')
        self.resized_image = i.resize((720,720))
        self.resized_image = self.resized_image.convert("RGBA")
        self.loading_image = ImageTk.PhotoImage(self.resized_image)

        self.image_on_canvas = self.canvas.create_image(0, 0, anchor='nw', image=self.loading_image)
    
        self.main.bind("<Escape>", lambda e: self.close_window())
        self.render_image()
        self.main.after(1000, self.render_image)
    
    #----------------
    def close_window(self):
        msg_box = tk.messagebox.askquestion('Exit Application', 'Are you sure you want to exit the application?',icon='warning')
        if msg_box == 'yes':
            self.main.destroy()


    def autoRotateImage(self):
        self.rotateImage(1)
        self.main.after(1000, self.autoRotateImage)



    def render_image(self):
        global fps
        text = "James"
        now = current_milli_time()
        delta = (now - self.last_render) / 1000
        
        font = ImageFont.truetype("fonts/Rubik-VariableFont_wght.ttf", 75, encoding="unic")
        image_to_render = Image.new('RGBA',(720, 720),(255,255,255,0))
        draw = ImageDraw.Draw(image_to_render)

        width = draw.textlength(text,font=font)
        x0 = (720 / 2)-((width / 2) + 20)
        y0 = self.y - (75/2)
        x1 = (720 / 2)+((width / 2) + 20)
        y1 = self.y + (75/2)
        draw.rectangle((x0, y0,x1, y1), fill=(255,255,255,180))
        draw.text((720/2,self.y),text,(38,38,38),font, anchor="mm")

        out = Image.alpha_composite(self.resized_image, image_to_render)
        self.current_image = ImageTk.PhotoImage(out)
        self.canvas.itemconfig(self.image_on_canvas, image=self.current_image)
        self.y = self.y + (delta * self.direction)
        if(self.y < 0):
            self.direction = self.direction * -1
            self.y = 0
        elif(self.y > 720):
            self.direction = self.direction * -1
            self.y= 720
        
        self.last_render = now
        self.main.after(round(1000/fps), self.render_image)



#----------------------------------------------------------------------
if __name__ == "__main__":
    #try:
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()
    #except (KeyboardInterrupt, Exception) as e:
    #    print(e)
    #    root.destroy()
    #    pass