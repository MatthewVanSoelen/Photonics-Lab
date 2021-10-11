# -*- coding: utf-8 -*-
"""
Created on Sun Jul 12 17:03:08 2020

@author: Matthew_VS
"""

### Python libraries ###
# Monitor packages
from screeninfo import get_monitors # Screen Information (screeninfo) is a package to fetch location and size of physical screens.
# Window packages 
from tkinter import Toplevel, Tk, Label # Graphical User Interface (GUI) package
from PIL import Image, ImageTk # Python Imaging Librarier (PIL) package
# Processing packages
import re # Regular Expression (re) is a package to check, if a string contains the specified search pattern.
import numpy as np # Scientific computing package (NumPy)
import os # used to create path to image folder

current_path = os.getcwd()
folder_path = os.path.join(current_path, "Grating_Images")
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

### Monitor controlling 
# Finds the resolution of all monitors that are connected.
active_monitors = get_monitors() # "monitor(screenwidth x screenheight + startpixel x + startpixel y)"


# Separates all numbers from a string
monitor_values=re.findall('([0-9]+)', str(active_monitors))
print(monitor_values)

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

width_array = int(np.ceil( np.sqrt(pow(width, 2) + pow(height, 2))))
height_array = width_array

### Begin of the code for the pattern of the SLM ###

#Create a zero-array for the image
data = np.zeros((height_array, width_array), dtype = np.uint16)
Degree = 0                    # rotate image by Degree 
y_max = 255                    # hightest gray value
y_min = 0                    # Lowest gray value
x_max = 100                    # width of each sawtooth
slope = (y_max-y_min)/x_max # rate of change of gray values
g_reverse = False            # for Black->White use FALSE
                            # for White->Black use TRUE
cx, cy = width_array //2, height_array //2 # The center of circle
radius = cy
intercept = 0
## Circle pattern

if(g_reverse):
    reverse = -1
    intercept = y_max
else:
    reverse = 1
    intercept = y_min

for i in range(width_array):                        # for creates color for each column
    color = slope * reverse * ( i % x_max) + intercept     # Slope intercept form: y = mx + b (y = color)
    x, y = np.ogrid[-radius: radius, -radius: radius]
    index = x**2 + y**2 <= radius**2
    data[cy-radius:cy+radius, cx-radius:cx+radius][index] = color                                # Save color to full column of data 
    radius -= 1
### End of the code for the pattern of the SLM ###
                      
def center_crop(image, array_width, array_height, width, height):
    x_margin = (array_width - width) //2
    y_margin = (array_height - height) // 2
    return image.crop((x_margin, y_margin, x_margin + width, y_margin + height))

def save_image(img, file_name):
    file_name = os.path.join(folder_path, file_name)
    img.save(file_name)
    
#Transform the created array into an image
img = Image.fromarray(data)    # convert array to Image
img = img.convert('L')        # convert colors to gray values
img = img.rotate(Degree)    # rotate image by degree
img = center_crop(img, width_array, height_array, width, height)
#Save the created image
if(g_reverse):
    name = 'Circle_Reverse_Grating_' + str(slope) + '_' + str(Degree) + 'Deg.png'
    save_image(img, name)
else:
    name = 'Circle_Grating_' + str(slope) + '_' + str(Degree) + 'Deg.png'
    save_image(img, name)


# Create a window environment on the computer
image_window = Tk()

# Window requieres no frame
image_window.attributes("-alpha", 0.0)
image_window.iconify()


# Create a window on the screen of the SLM monitor
window_slm = Toplevel(image_window)
window_slm_geometry = str("{:}".format(width) + 'x' + "{:}".format(height) + '+' + "{:}".format(begin_slm_horizontal) + '+' + "{:}".format(begin_slm_vertical))
print(window_slm_geometry)
window_slm.geometry(window_slm_geometry)
window_slm.overrideredirect(1)

# Open the created image with the SLM pattern
photo = ImageTk.PhotoImage(img)


# Load the opened image into the window of the SLM monitor
window_slm_label = Label(window_slm, image=photo)
window_slm_label.pack()

# Termination command for the code
image_window.bind('<Escape>', lambda e: image_window.destroy())

# Run the loop for the window environment
image_window.mainloop()
