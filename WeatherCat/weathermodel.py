from PIL import Image

class WeatherModel:
    def __init__(self):
        self.forecasts = []
        self.images = []
        self.summary = ""
        self.image_index = 0
        self.description_index = 0
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
        return Image.open(self.images[self.image_index][2])
    
    def next_image(self, direction = 1):
        self.image_index = self.image_index + direction
        if(self.image_index >= len(self.images)):
            self.image_index = 0
        if(self.image_index < 0):
            self.image_index = len(self.images) - 1        
        return Image.open(self.images[self.image_index][2])
    
    def get_description(self):

        try:
            options = list(self.forecasts[0].keys())
            if self.description_index == len(options):
                return self.summary
            else:
                key = options[self.description_index]
                return key + ": " + str(self.forecasts[0][key])

        except Exception as e:
            print(e)
            return "fail"
        
    def next_description(self, direction = 1):
        try:
            self.description_index = self.description_index + direction
            options = list(self.forecasts[0].keys())
            if self.description_index < 0:
                self.description_index = len(options)

            if (self.description_index == len(options)):
                return self.summary
            elif(self.description_index < len(options)):
                key = options[self.description_index]
                return key + ": " + str(self.forecasts[0][key])
            else:
                self.description_index = 0
                key = options[self.description_index]
                return key + ": " + str(self.forecasts[0][key])
        except Exception as e:
            print(e)
            return "error"        


    
