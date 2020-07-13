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



class Color_Slider:
    def __init__(self, master):

        self.master = master
        ### Monitor controlling 
        # Finds the resolution of all monitors that are connected.
        active_monitors = get_monitors() # "monitor(screenwidth x screenheight + startpixel x + startpixel y)"
        
        
        # Separates all numbers from a string
        monitor_values=re.findall('([0-9]+)', str(active_monitors))
        print(monitor_values)
        
        # Assign the separated digits of the string to a variable
        begin_monitor_horizontal = monitor_values[0]
        begin_monitor_vertical = monitor_values[1]
        begin_slm_horizontal = 20 # monitor_values[7]
        begin_slm_vertical = 20 # monitor_values[8]
        
        
        # Reverse the monitor pixel order (because, the SLM monitor is located ón the left side of the main monitor)
        #begin_slm_horizontal = str(int(begin_monitor_horizontal) - int(begin_slm_horizontal))
        #begin_slm_vertical = str(int(begin_monitor_vertical) - int(begin_slm_vertical))
        
        #Define picture/window size in pixels (size of the SLM)
        width = 1920
        height = 1152
        self.data = np.zeros((height, width), dtype = np.uint16)
        self.color = IntVar()
        
        
        self.slider = Scale(self.master, from_=0, to=255, tickinterval=255, variable= self.color ,orient=HORIZONTAL, sliderlength=100)
        self.slider.set(0)
        self.slider.pack()
        
        self.entry = Entry(self.master, textvariable=self.color)
        self.entry.pack()

        self.color_window = Toplevel(self.master)
        self.color_window.overrideredirect(1)
        self.color_window.bind("<Escape>", lambda e: color_window.destroy())
        self.color_window_geometry = str("{:}".format(width) + 'x' + "{:}".format(height) + '+' + "{:}".format(begin_slm_horizontal) + '+' + "{:}".format(begin_slm_vertical))
        self.color_window.geometry(self.color_window_geometry)
        self.img = Image.fromarray(self.data)
        self.img = self.img.convert('L')
        self.photo = ImageTk.PhotoImage(self.img)

        self.window_slm_label = Label(self.color_window, image=self.photo)
        self.window_slm_label.pack()

        def display_color():
            self.data[:,:] = int(self.color.get())
            self.img = Image.fromarray(self.data)
            self.img = self.img.convert('L')
            self.photo = ImageTk.PhotoImage(self.img)
            self.window_slm_label.config(image=self.photo)

        Button(self.master, text='Display', command=display_color).pack()



        
master = Tk()
master.title("Color Slider")
master.minsize(300, 300)
app = Color_Slider(master)
master.mainloop()