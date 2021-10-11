# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 14:41:43 2020

@author: Matthew_VS
"""


### Python libraries/Packages ###

# Monitor package
from screeninfo import get_monitors # Screen Information (screeninfo) is a package to fetch location and size of physical screens.

# GUI packages 
from tkinter import *
from PIL import Image, ImageTk # Python Imaging Librarier (PIL) package

# Processing packages
import re # Regular Expression (re) is a package to check, if a string contains the specified search pattern.
import numpy as np # Scientific computing package (NumPy)
import os # used to create path to image folder



class SawTooth_Slider:
    def __init__(self, master):
        
        current_path = os.getcwd()
        folder_path = os.path.join(current_path, "Grating_Images")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        
        self.master = master
        ## Monitor controlling 
        # Finds the resolution of all monitors that are connected.
        active_monitors = get_monitors() # "monitor(screenwidth x screenheight + startpixel x + startpixel y)"
        
        
        # Assign the separated x and y start values to variables
        begin_monitor_horizontal = active_monitors[0].x
        begin_monitor_vertical = active_monitors[0].y
        begin_slm_horizontal = active_monitors[1].x
        begin_slm_vertical = active_monitors[1].y
        
        
        # Reverse the monitor pixel order (because, the SLM monitor is located ón the left side of the main monitor)
        begin_slm_horizontal = str(int(begin_monitor_horizontal) - int(begin_slm_horizontal))
        begin_slm_vertical = str(int(begin_monitor_vertical) - int(begin_slm_vertical))
        
        #Define picture/window size in pixels (size of the SLM)
        width = 1920
        height = 1152
        array_width = int(np.ceil( np.sqrt(pow(width, 2) + pow(height, 2))))
        array_height = array_width
        
        self.data = np.zeros((array_height, array_width), dtype = np.uint16)
        self.y_max = IntVar()
        self.y_min = IntVar()
        self.x_max = IntVar()
        self.x_max.set(1)
        self.degree = IntVar()
        
        Label(self.master, text="y_max", font=20).grid(row=0,column=0)
        self.y_max_slider = Scale(self.master,from_=0, to=255, tickinterval=255, variable= self.y_max, orient=HORIZONTAL, length = 400, width = 30, font = 20)
        self.y_max_slider.set(0)
        self.y_max_slider.grid(row=0,column=1)
        
        Label(self.master, text="y_min", font=20).grid(row=1,column=0)
        self.y_min_slider = Scale(self.master, from_=0, to=255, tickinterval=255, variable= self.y_min, orient=HORIZONTAL, length = 400, width = 30, font = 20)
        self.y_min_slider.set(0)
        self.y_min_slider.grid(row=1,column=1)
        
        Label(self.master, text="x_max", font=20).grid(row=2,column=0)
        self.x_max_slider = Scale(self.master, from_=1, to=255, tickinterval=254, variable= self.x_max, orient=HORIZONTAL, length = 400, width = 30, font = 20)
        self.x_max_slider.set(1)
        self.x_max_slider.grid(row=2,column=1)
        
        Label(self.master, text="degree", font=20).grid(row=3,column=0)
        self.degree_slider = Scale(self.master, from_=0, to=360, tickinterval=180, variable= self.degree, orient=HORIZONTAL, length = 400, width = 30, font = 20)
        self.degree_slider.set(0)
        self.degree_slider.grid(row=3,column=1)
        
        def increment(var, x):
            if(var == "y_max"):
                if(self.y_max.get() + x) > 255:
                    self.y_max.set(255)
                elif (self.y_max.get() + x) < 0:
                    self.y_max.set(0)
                else:
                    self.y_max.set(self.y_max.get() + x)
            elif(var == "y_min"):
                if(self.y_min.get() + x) > 255:
                    self.y_min.set(255)
                elif (self.y_min.get() + x) < 0:
                    self.y_min.set(0)
                else:
                    self.y_min.set(self.y_min.get() + x)
            elif(var == "x_max"):
                if(self.x_max.get() + x) > 255:
                    self.x_max.set(255)
                elif (self.x_max.get() + x) < 1:
                    self.x_max.set(1)
                else:
                    self.x_max.set(self.x_max.get() + x)
            elif(var == "degree"):
                if(self.degree.get() + x) > 360:
                    self.degree.set(360)
                elif (self.degree.get() + x) < 0:
                    self.degree.set(0)
                else:
                    self.degree.set(self.degree.get() + x)
           
        
        self.frame1 = Frame(self.master)
        Button(self.frame1, text="-10", font=20, command= lambda: increment("y_max",-10)).pack(side=LEFT)
        Button(self.frame1, text="-1", font=20, command= lambda: increment("y_max",-1)).pack(side=LEFT)
        Button(self.frame1, text="+10", font=20, command= lambda: increment("y_max",10)).pack(side=RIGHT)
        Button(self.frame1, text="+1", font=20, command= lambda: increment("y_max",1)).pack(side=RIGHT)
        self.entry = Entry(self.frame1, font=20, textvariable=self.y_max)
        self.entry.pack()
        self.frame1.grid(row=0,column=2)
        
        self.frame2 = Frame(self.master)
        Button(self.frame2, text="-10", font=20, command= lambda: increment("y_min",-10)).pack(side=LEFT)
        Button(self.frame2, text="-1", font=20, command= lambda: increment("y_min",-1)).pack(side=LEFT)
        Button(self.frame2, text="+10", font=20, command= lambda: increment("y_min",10)).pack(side=RIGHT)
        Button(self.frame2, text="+1", font=20, command= lambda: increment("y_min",1)).pack(side=RIGHT)
        self.entry = Entry(self.frame2, font=20, textvariable=self.y_min)
        self.entry.pack()
        self.frame2.grid(row=1,column=2)
        
        self.frame3 = Frame(self.master)
        Button(self.frame3, text="-10", font=20, command= lambda: increment("x_max",-10)).pack(side=LEFT)
        Button(self.frame3, text="-1", font=20, command= lambda: increment("x_max",-1)).pack(side=LEFT)
        Button(self.frame3, text="+10", font=20, command= lambda: increment("x_max",10)).pack(side=RIGHT)
        Button(self.frame3, text="+1", font=20, command= lambda: increment("x_max",1)).pack(side=RIGHT)
        self.entry = Entry(self.frame3, font=20, textvariable=self.x_max)
        self.entry.pack()
        self.frame3.grid(row=2,column=2)
        
        self.frame4 = Frame(self.master)
        Button(self.frame4, text="-10", font=20, command= lambda: increment("degree",-10)).pack(side=LEFT)
        Button(self.frame4, text="-1", font=20, command= lambda: increment("degree",-1)).pack(side=LEFT)
        Button(self.frame4, text="+10", font=20, command= lambda: increment("degree",10)).pack(side=RIGHT)
        Button(self.frame4, text="+1", font=20, command= lambda: increment("degree",1)).pack(side=RIGHT)
        self.entry = Entry(self.frame4, font=20, textvariable=self.degree)
        self.entry.pack()
        self.frame4.grid(row=3,column=2)
        
        def center_crop(image, array_width, array_height, width, height):
            x_margin = (array_width - width) //2
            y_margin = (array_height - height) // 2
            return image.crop((x_margin, y_margin, x_margin + width, y_margin + height))
        
        def corner_crop(image, width, height):
            return image.crop((0,0,width, height))
        
        def save_image(img, file_name):
            file_name = os.path.join(folder_path, file_name)
            img.save(file_name)
        
        def create_grating():
           
            self.slope = (self.y_max.get()-self.y_min.get())/self.x_max.get()
            
            for i in range(array_width):
                color = self.slope * (i % self.x_max.get()) + self.y_min.get()
                self.data[:, i] = color
            
            self.img = Image.fromarray(self.data)
            self.img = self.img.convert('L')
            self.img = self.img.rotate(self.degree.get())
            self.img = center_crop(self.img, array_width, array_height ,width, height)
            self.photo = ImageTk.PhotoImage(self.img)
        
        self.pattern_window = Toplevel(self.master)
        self.pattern_window.overrideredirect(1)
        self.pattern_window.bind("<Escape>", lambda e: pattern_window.destroy())
        self.pattern_window_geometry = str("{:}".format(width) + 'x' + "{:}".format(height) + '+' + "{:}".format(begin_slm_horizontal) + '+' + "{:}".format(begin_slm_vertical))
        self.pattern_window.geometry(self.pattern_window_geometry)
        create_grating()
        self.pattern = Label(self.pattern_window,image = self.photo)
        self.pattern.pack()
        
        
            
        def display_pattern(*args):
            try:
                int(self.y_max.get())
                int(self.y_min.get())
                int(self.x_max.get())
                int(self.degree.get())
                
                create_grating()
                self.pattern.config(image=self.photo)
            except:
                print("entry box is not a valid integer")
            

        self.y_max.trace("w", display_pattern)
        self.y_min.trace("w", display_pattern)
        self.x_max.trace("w", display_pattern)
        self.degree.trace("w", display_pattern)
        
        def save_grating(*args):
            rouned_slope = np.around(self.slope, 4)
            name = 'Sawtooth_Grating_' + str(self.slope) + 'Slope_' + str(self.degree.get()) + 'Deg.png'
            save_image(self.img, name)
            
        Button(self.master, text="Save", font=20, command = save_grating).grid(row=4, column=0, padx=20, pady=20)


        
master = Tk()
master.title("SawTooth Slider")
master.minsize(1000, 500)
app = SawTooth_Slider(master)
master.mainloop()
