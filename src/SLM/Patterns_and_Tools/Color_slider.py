### Python libraries ###
# Monitor packages
from screeninfo import get_monitors # Screen Information (screeninfo) is a package to fetch location and size of physical screens.
# Window packages 
from tkinter import *
#from tkinter import Toplevel, Tk, Label # Graphical User Interface (GUI) package
from PIL import Image, ImageTk # Python Imaging Librarier (PIL) package
# Processing packages
import re # Regular Expression (re) is a package to check, if a string contains the specified search pattern.
import numpy as np # Scientific computing package (NumPy)
import os # used to create path to image folder



class Color_Slider:
    def __init__(self, master):
        current_path = os.getcwd()
        folder_path = os.path.join(current_path, "Grating_Images")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        self.master = master
        ### Monitor controlling 
        # Finds the resolution of all monitors that are connected.
        active_monitors = get_monitors() # "monitor(screenwidth x screenheight + startpixel x + startpixel y)"
        
        
        # # Separates all numbers from a string
        monitor_values=re.findall('([0-9]+)', str(active_monitors))
        print(monitor_values)
        
        # # Assign the separated digits of the string to a variable
        begin_monitor_horizontal = monitor_values[0]
        begin_monitor_vertical = monitor_values[1]
        begin_slm_horizontal = monitor_values[7]
        begin_slm_vertical = monitor_values[8]
        
        
        # Reverse the monitor pixel order (because, the SLM monitor is located ón the left side of the main monitor)
        begin_slm_horizontal = str(int(begin_monitor_horizontal) - int(begin_slm_horizontal))
        begin_slm_vertical = str(int(begin_monitor_vertical) - int(begin_slm_vertical))
        
        #Define picture/window size in pixels (size of the SLM)
        width = 1920
        height = 1152
        self.data = np.zeros((height, width), dtype = np.uint16)
        self.color = IntVar()
        
        
        self.slider = Scale(self.master, from_=0, to=255, tickinterval=255, variable= self.color ,orient=HORIZONTAL, length=400, width = 30, font=20)
        self.slider.set(0)
        self.slider.pack()
        
        def increment_color(x):
            self.color.set(self.color.get() + x)
        
        self.frame1 = Frame(self.master)
        Button(self.frame1, text="-10", font=20, command= lambda: increment_color(-10)).pack(side=LEFT)
        Button(self.frame1, text="-1", font=20, command= lambda: increment_color(-1)).pack(side=LEFT)
        Button(self.frame1, text="+10", font=20, command= lambda: increment_color(10)).pack(side=RIGHT)
        Button(self.frame1, text="+1", font=20, command= lambda: increment_color(1)).pack(side=RIGHT)
        self.entry = Entry(self.frame1, font=20, textvariable=self.color)
        self.entry.pack()
        self.frame1.pack()

        self.color_window = Toplevel(self.master, bg="#000000")
        self.color_window.overrideredirect(1)
        self.color_window.bind("<Escape>", lambda e: color_window.destroy())
        self.color_window_geometry = str("{:}".format(width) + 'x' + "{:}".format(height) + '+' + "{:}".format(begin_slm_horizontal) + '+' + "{:}".format(begin_slm_vertical))
        self.color_window.geometry(self.color_window_geometry)


        def display_color(*args):
            hex_num = hex(self.color.get())
            print(hex_num)
            hex_num = hex_num[2:]
            if(len(hex_num) < 2):
                hex_num = "0%s"%(hex_num)
            hex_color = "#%s%s%s"%(hex_num, hex_num, hex_num)
            print(hex_color)
            self.color_window.config(bg=hex_color)

        self.color.trace("w", display_color)



        
master = Tk()
master.title("Color Slider")
master.minsize(600, 200)
app = Color_Slider(master)
master.mainloop()
