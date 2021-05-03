### Python libraries ###
# Monitor packages
from screeninfo import get_monitors # Screen Information (screeninfo) is a package to fetch location and size of physical screens.
# Window packages 
from tkinter import Toplevel, Tk, Label # Graphical User Interface (GUI) package
from PIL import Image, ImageTk # Python Imaging Librarier (PIL) package
# Processing packages
import re # Regular Expression (re) is a package to check, if a string contains the specified search pattern.
import numpy as np # Scientific computing package (NumPy)

class SLM_window():

    def __init__(self, master, grating = None):
        ### Monitor controlling 
        # Finds the resolution of all monitors that are connected.
        active_monitors = get_monitors() # "monitor(screenwidth x screenheight + startpixel x + startpixel y)"
        print("Monitor Values:", active_monitors)

        # Separates all numbers from a string
        monitor_values=re.findall('([0-9]+)', str(active_monitors))
        print("Monitor Values:", monitor_values)

        # Assign the separated digits of the string to a variable
        begin_monitor_horizontal = monitor_values[0]
        begin_monitor_vertical = monitor_values[1]
        begin_slm_horizontal = monitor_values[4]
        begin_slm_vertical = monitor_values[5]

        begin_slm_horizontal, begin_slm_vertical = self.display_left_side(begin_monitor_horizontal, begin_slm_horizontal, begin_monitor_vertical, begin_slm_vertical)
        print(begin_slm_horizontal, begin_slm_vertical)
        width = 1920
        height = 1152

        if not grating:
            array = np.zeros((height, width), dtype = np.uint16)
            image = Image.fromarray(array)
            image = image.convert('L')
            grating = ImageTk.PhotoImage(image)

        # self.image_window = Tk()
        self.image_window = master
        

        # Create a window on the screen of the SLM monitor
        self.window_slm = Toplevel(self.image_window)
        self.window_slm_geometry = str("{:}".format(width) + 'x' + "{:}".format(height) + '+' + "{:}".format(begin_slm_horizontal) + '+' + "{:}".format(begin_slm_vertical))
        print(self.window_slm_geometry)
        self.window_slm.geometry(self.window_slm_geometry)
        self.window_slm.overrideredirect(1)
        
        

        # Load the opened image into the window of the SLM monitor
        
        self.window_slm_label = Label(self.window_slm, image=grating)
        self.window_slm_label.pack()
        print(self.window_slm_geometry, "\n", grating.height(), grating.width())
        # Termination command for the code
        self.window_slm.bind("<Escape>", lambda e: self.window_slm.destroy())
       
    
    def display(self,grating):
        self.window_slm_label.config(image=grating)

    def close_window(self):
        print("pressed")
        self.window_slm.destroy()
        self.window_slm.update()

    def display_left_side(self, bmh, bsh, bmv, bsv):
        # Reverse the monitor pixel order (because, the SLM monitor is located ón the left side of the main monitor)
        begin_slm_horizontal = str(int(bmh) - int(bsh))
        begin_slm_vertical = str(int(bmv) - int(bsv))
        return (begin_slm_horizontal, begin_slm_vertical)



