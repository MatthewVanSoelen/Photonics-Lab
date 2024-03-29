### Python libraries ###
# Monitor packages
from screeninfo import get_monitors # Screen Information (screeninfo) is a package to fetch location and size of physical screens.
# Window packages 
from tkinter import Toplevel, Tk, Label # Graphical User Interface (GUI) package
import PIL.Image, PIL.ImageTk # Python Imaging Librarier (PIL) package
# Processing packages
import re # Regular Expression (re) is a package to check, if a string contains the specified search pattern.
import numpy as np # Scientific computing package (NumPy)

class SLM_window():

    def __init__(self, master, grating = None):
        ### Monitor controlling 
        # Finds the resolution of all monitors that are connected.
        active_monitors = get_monitors() # "monitor(screenwidth x screenheight + startpixel x + startpixel y)"
        

        # Assign the separated x and y start values to variables
        begin_monitor_horizontal = active_monitors[0].x
        begin_monitor_vertical = active_monitors[0].y
        begin_slm_horizontal = active_monitors[1].x
        begin_slm_vertical = active_monitors[1].y

        print(begin_slm_horizontal, begin_slm_vertical)
        width = 1920
        height = 1152

        if grating is None:
            array = np.zeros((height, width), dtype = np.uint16)
            image = PIL.Image.fromarray(array)
            image = image.convert('L')
            grating = PIL.ImageTk.PhotoImage(image)

        # self.image_window = Tk()
        self.image_window = master
        

        # Create a window on the screen of the SLM monitor
        self.window_slm = Toplevel(self.image_window)
        self.window_slm_geometry = str("{:}".format(width) + 'x' + "{:}".format(height) + '+' + "{:}".format(begin_slm_horizontal) + '+' + "{:}".format(begin_slm_vertical))
        
        print(self.window_slm_geometry)
        self.window_slm.geometry(self.window_slm_geometry)
        self.window_slm.overrideredirect(1)
        
        

        # Load the opened image into the window of the SLM monitor
        
        self.window_slm_label = Label(self.window_slm,image=grating)
        self.window_slm_label.image = grating
        self.window_slm_label.pack()
        
        # Termination command for the code
        self.window_slm.bind("<Escape>", lambda e: self.window_slm.destroy())
       
    
    def display(self,grating):
        self.window_slm_label.config(image=grating)
        self.window_slm_label.image = grating
        
    def display_text(self,msg):
        self.window_slm_label.config(text=msg)

    def close_window(self):
        print("pressed")
        self.window_slm.destroy()
        self.window_slm.update()




