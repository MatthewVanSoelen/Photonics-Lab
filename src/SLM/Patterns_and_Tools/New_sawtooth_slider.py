
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

class Adjustment_Frame(Frame):
    def __init__(self, parent, variable, from_limit, to_limit, interval, start_amt, text="", *args, **options):
        Frame.__init__(self, parent, *args, **options)

        font = 20
        self.frame = Frame(self)
        self.frame.grid(row=0,column=0)

        Label(self.frame, text=text, font=font).pack(side=LEFT)
        self.y_max_slider = Scale(self.frame, from_=from_limit, to=to_limit, tickinterval=interval, variable=variable, orient=HORIZONTAL, length=400, width=30, font=font)
        self.y_max_slider.set(start_amt)
        self.y_max_slider.pack(side=LEFT)

        
        Button(self.frame, text="-10", font=font, command= lambda: self.increment(variable,-10, from_limit, to_limit)).pack(side=LEFT)
        Button(self.frame, text="-1", font=font, command= lambda: self.increment(variable,-1, from_limit, to_limit)).pack(side=LEFT)
        self.entry = Entry(self.frame, font=font, textvariable=variable)
        self.entry.pack(side=LEFT)
        Button(self.frame, text="+10", font=font, command= lambda: self.increment(variable,10, from_limit, to_limit)).pack(side=RIGHT)
        Button(self.frame, text="+1", font=font, command= lambda: self.increment(variable,1, from_limit, to_limit)).pack(side=RIGHT)
        
        

    def increment(self,var, x, from_limit, to_limit):
        if(var.get() + x) > to_limit:
            var.set(to_limit)
        elif (var.get() + x) < 0:
            var.set(from_limit)
        else:
            var.set(var.get() + x)


class SawTooth_slider:
    def __init__(self, root):

        self.root = root
        ## Monitor controlling 
        # Finds the resolution of all monitors that are connected.
        active_monitors = get_monitors() # "monitor(screenwidth x screenheight + startpixel x + startpixel y)"
        
        for monitor in active_monitors:
            print(monitor)

        
        # Assign the separated x and y start values to variables
        begin_monitor_horizontal = active_monitors[0].x
        begin_monitor_vertical = active_monitors[0].y
        begin_slm_horizontal = active_monitors[1].x
        begin_slm_vertical = active_monitors[1].y

        print("monitor x: ", begin_monitor_horizontal, 
            "\nmonitor y: ", begin_slm_vertical, 
            "\nslm x: ", begin_slm_horizontal, 
            "\nslm y: ", begin_slm_vertical)
        
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

        controls_frame = Frame(self.root)
        controls_frame.grid(row=0, column=0)

        y_max_frame = Adjustment_Frame(controls_frame, text="y_max", variable=self.y_max, from_limit=0, to_limit=255, interval=255, start_amt=0)
        y_max_frame.grid(row=0, column=0)

        y_min_frame = Adjustment_Frame(controls_frame, text="y_min", variable=self.y_min, from_limit=0, to_limit=255, interval=255, start_amt=0)
        y_min_frame.grid(row=1, column=0)

        x_max_frame = Adjustment_Frame(controls_frame, text="x_max", variable=self.x_max, from_limit=1, to_limit=255, interval=254, start_amt=0)
        x_max_frame.grid(row=2, column=0)

        degree_frame = Adjustment_Frame(controls_frame, text="degree", variable=self.degree, from_limit=0, to_limit=360, interval=180, start_amt=0)
        degree_frame.grid(row=3, column=0)

        current_path = os.getcwd()
        folder_path = os.path.join(current_path, "Grating_Images")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)


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
        
        self.pattern_window = Toplevel(self.root, bg="blue")

        self.pattern_window.update_idletasks()
        self.pattern_window.overrideredirect(1)
        self.pattern_window.bind("<Escape>", lambda e: pattern_window.destroy())
        # self.pattern_window_geometry = str("1920x1152+300+-300")
        self.pattern_window_geometry = str("{:}".format(width) +
                                        'x' + "{:}".format(height) + '+' +
                                        "{:}".format(begin_slm_horizontal) + '+' +
                                        "{:}".format(begin_slm_vertical))
        \
        self.pattern_window.geometry(self.pattern_window_geometry)
        create_grating()
        self.pattern = Label(self.pattern_window,image = self.photo)
        self.pattern.pack()
        self.pattern_window.overrideredirect(True)

            
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
            
        Button(self.root, text="Save", font=20, command = save_grating).grid(row=4, column=0, padx=20, pady=20)


                
root = Tk()
root.title("SawTooth Slider")
root.minsize(1000, 500)
app = SawTooth_slider(root)
root.mainloop()
