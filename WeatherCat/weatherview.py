import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont

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
