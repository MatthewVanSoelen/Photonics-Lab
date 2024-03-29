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
Degree = 0                  # rotate image by Degree 
y_max = 255                 # hightest gray value
y_min = 0                   # Lowest gray value
x_max = 100                 # width of each sawtooth
slope = (y_max-y_min)/x_max # rate of change of gray values
g_reverse = 0           # for Black->White use FALSE
                            # for White->Black use TRUE


## SawTooth pattern

if(g_reverse == 0):
    reverse = -1
    y_intercept = y_max
else:
    reverse = 1
    y_intercept = y_min

period_counter = 0
for i in range(width_array):                            # for creates color for each column
    
    if(i % (x_max) == 0):
        period_counter += 1

    if(period_counter % 2 == g_reverse):
        color = slope * -1 * (i%x_max) + y_max          # SLope intercept form: y = mx + b (y = color)
        data[:, i] = color                            # Save color to full column of data
    else:
        color = slope * 1 * (i%x_max) + y_min
        data[:, i] = color
                                  


### End of the code for the pattern of the SLM ###
def center_crop(image, array_width, array_height, width, height):
    x_margin = (array_width - width) //2
    y_margin = (array_height - height) // 2
    return image.crop((x_margin, y_margin, x_margin + width, y_margin + height))
                      

def corner_crop(image, width, height):
    return image.crop((0,0,width, height))

def save_image(img, file_name):
    file_name = os.path.join(folder_path, file_name)
    img.save(file_name)

#Transform the created array into an image
img = Image.fromarray(data)    # convert array to Image
img = img.convert('L')        # convert colors to gray values
img = img.rotate(Degree)    # rotate image by degree
img = corner_crop(img, width, height)

#Save the created image
if(g_reverse):
    name = 'Triangle_Reverse_Grating_' + str(slope) + '_' + str(Degree) + 'Deg.png'
    save_image(img, name)
else:
    name = 'Triangle_Grating_' + str(slope) + '_' + str(Degree) + 'Deg.png'
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

# # Open the created image with the SLM pattern
photo = ImageTk.PhotoImage(img)

# # Load the opened image into the window of the SLM monitor
window_slm_label = Label(window_slm, image=photo)
window_slm_label.pack()

# Termination command for the code
image_window.bind("<Escape>", lambda e: image_window.destroy())

# Run the loop for the window environment
image_window.mainloop()
