from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from matplotlib.image import imread
from matplotlib import cm
import numpy as np
from PIL import Image
import os


class Pattern:
    def __init__(self, height:int, width:int):
        self.height = height
        self.width = width
        
        self.data = np.zeros((height, width), dtype = np.uint16)
        self.x_set = set(range(0, width))
        self.y_set = set(range(0, height))

        current_path = os.getcwd()
        self.folder_path = os.path.join(current_path, "Patterns")
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)


    def add_horizontal_bar(self, start:int, end:int, gray_value: int):
        if gray_value not in range(0,255):
            gray_value = 100

        bar = self.y_set.intersection(range(start, end))
        self.data[min(bar): max(bar), :] = gray_value

    def add_vertical_bar(self, start:int, end:int, gray_value: int):
        if gray_value not in range(0,255):
            gray_value = 100

        bar = self.x_set.intersection(range(start, end))
        self.data[:, min(bar): max(bar)] = gray_value

    def add_circle(self, radius:int, cx:int, cy:int, gray_value:int):
        x, y = np.ogrid[-radius: radius, -radius: radius]
        index = x**2 + y**2 <= radius**2
        self.data[cy-radius:cy+radius, cx-radius:cx+radius][index] = gray_value 


    def create_image(self):
        self.image = Image.fromarray(self.data)
        self.image = self.image.convert('L')

    def save_image(self, file_name:str):
        file_name = os.path.join(self.folder_path, file_name)
        self.image.save(file_name)

    def display_image(self):
        self.image.show()

    def create_FFT_image(self):
        self.fft = np.fft.fft2(self.image)
        self.fft = np.abs(self.fft)
        max_value = np.max(self.fft)
        if max_value <= 0:
            c = 0
        else:
            c = 255/(1 + np.log(max_value))

        self.fft = c * np.log(1 + self.fft)

        self.fft_image = Image.fromarray(self.fft)
        self.fft_image = self.fft_image.convert('L')

    def display_fft_image(self):
        self.fft_image.show()


    def display_fft_graph(self):
        
        fig = plt.figure()
        ax = fig.gca(projection='3d')

        x = np.arange(0, self.width, 1)
        y = np.arange(0, self.height, 1)
        X, Y = np.meshgrid(x, y)
        Z = self.fft

        surface = ax.plot_surface(X, Y, Z, cmap=cm.cividis)
        fig.colorbar(surface, shrink=0.5, aspect=5)
        plt.show()

pattern = Pattern(width=1920, height=1152)
pattern.add_vertical_bar(930, 990, 120)
# pattern.add_vertical_bar(100, 160, 240)
pattern.add_horizontal_bar(566, 586, 116)
# pattern.add_horizontal_bar(90, 130, 16)
# pattern.add_circle(100, 960, 576, 200)
pattern.create_image()
pattern.save_image("pattern_temp.png")
pattern.display_image()
pattern.create_FFT_image()
pattern.save_image("FFT_temp.png")
pattern.display_fft_image()
pattern.display_fft_graph()