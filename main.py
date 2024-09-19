import tkinter as tk
from WeatherCat.weathercontroller import WeatherController

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