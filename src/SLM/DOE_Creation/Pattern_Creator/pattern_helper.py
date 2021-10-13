"""
pattern_helper.py : Matthew Van Soelen
Description : Contains implemention of some 
            helper classes for the view, and Pattern_Data 
            which manages creating and manipulating the data and images. 
"""

# Tkinter Imports - GUI creation
from tkinter import *
from tkinter import filedialog
from tkinter import font 
from tkinter.ttk import Progressbar

# Python Image Library (PIL) - image processing 
from PIL import Image, ImageTk, ImageFilter, ImageDraw

# Numpy import - Data manipulation
import numpy as np

# Pathing imports - reading and writing files and paths
import os 
import ntpath
import sys
import json

# Python Debugger - basic debugging tool
import pdb

class Toggled_Frame(Frame):
    def __init__(self, parent, text="", state=True, *args, **options):
        Frame.__init__(self, parent, *args, **options)

        self.toggle_text = ["\u27A4\t"+text, "\u25BC\t"+text]

        self.show = BooleanVar()
        self.show.set(state)

        self.title_frame = Frame(self)
        self.title_frame.pack(fill="x", expand=1)

        self.sub_frame = Frame(self, relief="sunken", borderwidth=1)

        self.toggle_button = Button(self.title_frame, text=self.toggle_text[0], 
                                        anchor="w", command=self.toggle)
        self.toggle_button.pack(side="left", fill="x", expand=1)

        # self.title_label = Label(self.title_frame, text=text)
        # self.title_label.pack(side="left", fill="x", expand=1)

        if not self.show.get():
            self.sub_frame.pack(fill="x", expand=1)
            self.toggle_button.config(text=self.toggle_text[1])
            self.show.set(False)

    def toggle(self):
        if self.show.get():
            self.sub_frame.pack(fill="x", expand=1)
            self.toggle_button.config(text=self.toggle_text[1])
            self.show.set(False)
        else:
            self.sub_frame.forget()
            self.toggle_button.config(text=self.toggle_text[0])
            self.show.set(True)

    def set_title(self, title=""):
        self.title_label.config(text=title)

class ToolTip(object):
    """
    Information hovering over Tkinter widget 
    Source: https://stackoverflow.com/questions/20399243/display-message-when-hovering-over-something-with-mouse-cursor-in-python
    """
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "12", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

class Pattern_Data:
    def __init__(self, root: Tk, update_gui):
        self.root = root
        self.update_gui = update_gui
        self.width = 1920
        self.height = self.width
        self.pattern_list = np.array([]) # list of patterns that can be displayed(fft/Orgin/etc)
        self.thumbnail_size = (450,450)

        current_path = os.getcwd()
        self.folder_path = os.path.join(current_path, "Pattern_Gui_Data")
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)


        try:
            default_img_path = os.path.join(current_path, "Default_Preview.png")
            self.default_img = Image.open(default_img_path)
        except:
            self.default_img = Image.fromarray(np.zeros((self.height, self.width), dtype = np.uint16))
        
        self.upload_image = self.default_img.convert('L')
        self.upload_data = np.asarray(self.upload_image)
        self.thumbnail_upload_image = self.upload_image.copy()
        self.thumbnail_upload_image.thumbnail(self.thumbnail_size)
        self.tk_upload_image = ImageTk.PhotoImage(self.thumbnail_upload_image)

        self.orig_image = self.default_img.convert('L')
        self.data = np.asarray(self.orig_image)
        self.thumbnail_image = self.orig_image.copy()
        self.thumbnail_image.thumbnail(self.thumbnail_size)
        self.tk_image = ImageTk.PhotoImage(self.thumbnail_image)

        
        self.fft_image = self.default_img.convert('L')
        self.thumbnail_fft_image = self.fft_image.copy()
        self.fft_data = np.asarray(self.fft_image)
        self.raw_fft = self.fft_data
        self.thumbnail_fft_image.thumbnail(self.thumbnail_size)
        self.tk_fft_image = ImageTk.PhotoImage(self.thumbnail_fft_image)

        self.images = {
            "names": ['Custom','FFT', 'Produced'],
            "images": [self.upload_image, self.fft_image, self.orig_image],
            "tk_images": [self.tk_upload_image, self.tk_fft_image, self.tk_image],
            "data": [self.upload_data, self.fft_data, self.data]
        }



        self.file_path = None
        self.pattern_name = "Default"
        self.max_amplitude = 255

        self.entry_box_width = 6
        self.label_box_width = 8

        # Method Data
        self.method_arr = ['Old','Meshgrid']
        self.method_options = set(self.method_arr)
        self.method = StringVar(self.root)
        self.method.set(self.method_arr[1])

        # Upload Settings Data
        self.upload_color_state = IntVar(self.root)
        self.gray_max = StringVar()
        self.gray_min = StringVar()

        self.image_options = set(self.images['names'])
        self.cur_image = StringVar(self.root, value=self.images['names'][0])


        # Dimensions Data

        self.square_pattern = BooleanVar(self.root, value=True)
        self.user_width = StringVar()
        self.user_height = StringVar()

        # Custom Pattern Data

        self.types = ['Single Freq','Single Point [x,y]', 'Hor. Line', 'Ver. Line', 'Diagonal Line', 'Upload', 'Slope']
        self.type_options = set(self.types)
        self.p_type = StringVar(self.root)
        self.p_type.set('Single Freq')

        self.user_freq = StringVar()
        self.user_angle = StringVar()
        self.user_x = StringVar()
        self.user_y = StringVar()
        self.user_coords = StringVar()
        self.user_line_len = StringVar()
        self.user_y_max = StringVar()
        self.user_y_min = StringVar()
        self.user_x_max =  StringVar(value="1")
        

        # Extra Options Data

        self.margin_pattern = BooleanVar(value=True)
        self.user_margin_size = StringVar(value="2000")

        self.fft_shift_state = BooleanVar(value=True)

        # Process Data

        self.progress_bar_value = 0
        self.progress_label = ""

        self.grating_count = 0
        self.cur_image.trace("w", self.display_image)
        self.display_image()
    
    def crop_array_center(self, arr, height, width):
        """
        Crops array to center 
        """
        arr_height, arr_width = arr.shape 
        x_margin = (arr_width - width)//2
        y_margin = (arr_height - height)//2
        return arr[y_margin:y_margin+height, x_margin:x_margin+width]
    
    def center_crop(self, image, array_width, array_height, width, height):
        x_margin = (array_width - width) //2
        y_margin = (array_height - height) // 2
        return image.crop((x_margin, y_margin, x_margin + width, y_margin + height))
        

    def get_method(self):
        return self.method

    def set_method(self, option):
        self.method = option
        return True

    def pattern_select(self, file_path=None):
        """
        Function called when upload_pattern_button pressed
        Opens a file dialog propmting used to select a file
        """
        if file_path is None:
            self.file_path = filedialog.askopenfilename(initialdir='Patterns', 
                                                        title="Select Image", 
                                                        filetypes=(("png images","*.png"),
                                                                ("jpeg images","*.jpeg"), 
                                                                ("All files","*.*")))
        else:
            self.file_path = file_path
        
        self.pattern_name = ntpath.basename(self.file_path)
        path = os.path.splitext(self.file_path)[0] #splits off file extension
        self.file_name = ntpath.basename(path)

        self.images['images'][0] = Image.open(self.file_path).convert('L')
        self.p_type.set('Upload')
        self.cur_image.set(self.images['names'][0])
        
        # self.upload_image.show()

    def display_image(self, *args ):
        self.update_images()
        self.update_gui.set("Previews")

    def update_images(self):

        if self.p_type.get() == self.types[5]: 
            self.thumbnail_upload_image = self.images['images'][0].copy()
            self.thumbnail_upload_image.thumbnail(self.thumbnail_size)
            self.images['tk_images'][0] = ImageTk.PhotoImage(self.thumbnail_upload_image)


        self.images['images'][2] = Image.fromarray(self.images['data'][2]).convert('L')
        self.thumbnail_image = self.images['images'][2].copy()
        self.thumbnail_image.thumbnail(self.thumbnail_size)
        self.images['tk_images'][2] = ImageTk.PhotoImage(self.thumbnail_image)

        self.images['images'][1] = Image.fromarray(self.images['data'][1]).convert('L')
        self.thumbnail_fft_image = self.images['images'][1].copy()
        self.thumbnail_fft_image.thumbnail(self.thumbnail_size)
        self.images['tk_images'][1] = ImageTk.PhotoImage(self.thumbnail_fft_image)

    def point_at_old(self, x:int = None, y:int = None, freq:float=None, angle:int=None, value:int = 255):
        """
        return array containing a sin pattern representing a point 
        at the given coordinates or freq and angle

        Method: Old 
            sin pattern produced using 1D linspace, converted to image, 
            rotated, converted back to array, and cropped
        """
        data = np.zeros((2*self.height, 2*self.width))
        # pdb.set_trace()
        if x is not None and y is not None:
            dist = np.sqrt( x**2 + y**2)
            freq = dist

            if x < 1:
                angel = 0
            else:
                angle = np.degrees(np.arctan(y/x))
        elif freq is None or angle is None:
            print("point_at_old: Incomplete coords, freq and angle")

        x = np.linspace(0, 2* np.pi, 2*self.width)

        # value = 255 # grayscale value from original image.
        amplitude = value/(self.max_amplitude * 2)
        for i in range(2*self.height):
            gray = amplitude * (np.sin(x * (freq*2)) + 1)
            data[i] = gray
      

        img = Image.fromarray(data)
        img = img.rotate(- angle)
        data = np.asarray(img)
        data = self.crop_array_center(data, self.height, self.width)
        if x is not None:
            x = int(x)
        if y is not None:
            y = int(y)
        if angle is not None:
            angle = float(angle)
        if freq is not None:
            freq = float(freq)
        if value is not None:
            value = int(value)
        return data, {'x':x, 'y':y, 'angle':angle, 'freq':freq, 'value':value}

    def point_at_meshgrid(self, x:int = None, y:int = None, freq:float=None, angle:int=None, value:int=255):
        """
        return array containing a sin pattern representing a point 
        at the given coordinates or freq and angle

        Method: Meshgrid
            sin pattern produced using the meshgrid of two 1D linspace at specified angle
        """
        # pdb.set_trace()
        side = max(self.height, self.width)
        diag = int(np.ceil(np.sqrt(side**2 + side**2)))
        lin_x = np.linspace(0, 2*np.pi, diag)
        lin_y = np.linspace(0, 2*np.pi, diag)

        if x is not None and y is not None:
            dist = np.sqrt( x**2 + y**2)
            freq = dist
            if x < 1:
                angle = 0
            else:
                angle = np.arctan(y/x)

        elif freq is not None and angle is not None:
            angle = np.radians(angle)
        elif freq is None or angle is None:
            print("point_at_meshgrid: Incomplete coords, freq and angle")
        
        amplitude = value/(self.max_amplitude * 2)
        mesh_x, mesh_y = np.meshgrid(lin_x, lin_y)
        angled_mesh = mesh_x*np.cos(angle)+mesh_y*np.sin(angle)
        data = amplitude * (np.sin(angled_mesh * freq) + 1)
        if x is not None:
            x = int(x)
        if y is not None:
            y = int(y)
        if angle is not None:
            angle = float(angle)
        if freq is not None:
            freq = float(freq)
        if value is not None:
            value = int(value)
        data = self.crop_array_center(data, self.height, self.width)
        return data, {'x':x, 'y':y, 'angle':angle, 'freq':freq, 'value':value}

    def points_of_arr(self, arr, method:int):
        """
        return array containing a sum of sin patterns 
        representing the array of given points, using the given method
        """
        data = np.zeros((self.height, self.width))
        for point in arr:
            if method == 0: # old Method
                temp_data, pattern_configs = self.point_at_old(x= point[0], y= point[1])
                data += temp_data
                self.pattern_list = np.append(self.pattern_list, [pattern_configs], 0)
            elif method == 1: # meshgrid Method
                temp_data, pattern_configs = self.point_at_meshgrid(x= point[0], y= point[1])
                data += temp_data
                self.pattern_list = np.append(self.pattern_list, [pattern_configs], 0)
            else:
                print("points_of_arr: Undefined Method")
        # pdb.set_trace()
        n = len(arr)
        data = (data / n)
        return data

    def single_freq(self):
        """
        Produce sine wave pattern for a single with a single frequency
        """
        if float(self.user_freq.get()):
            freq = float(self.user_freq.get())
        else:
            freq = 1.2
            print("Freq set to 1.2")

        if int(self.user_angle.get()) or self.user_angle.get() == '0':
            angle = int(self.user_angle.get())
        else:
            angle = 10
            print("angle set to 10")

        method = self.method.get()

        if method == "Old":
            self.images['data'][2], pattern_configs = self.point_at_old(freq = freq, angle = angle)
            self.pattern_list = np.append(self.pattern_list, [pattern_configs], 0)
        elif method == "Meshgrid":
            self.images['data'][2], pattern_configs = self.point_at_meshgrid(freq = freq, angle = angle)
            self.pattern_list = np.append(self.pattern_list, [pattern_configs], 0)
        else:
            print("Undefined Method")

        self.pattern_name = "freq_%s_%s\N{DEGREE SIGN}_%s.png"%(freq, angle, method)

    def single_point(self):
        """
        Produce sine wave pattern for a single with a single frequency at given coordinates
        """
        if int(self.user_x.get()) or self.user_x.get() == '0':
            x_pos = int(self.user_x.get())
        else:
            x_pos = 10
            print("x_pos set to 10")

        if int(self.user_y.get()) or self.user_y.get() == '0':
            y_pos = int(self.user_y.get())
        else:
            y_pos = 10
            print("y_pos set to 10")

        method = self.method.get()
        if method == self.method_arr[0]:
            self.images['data'][2], pattern_configs =  self.point_at_old(x = x_pos, y = y_pos)
            self.pattern_list = np.append(self.pattern_list, [pattern_configs], 0)
        elif method == self.method_arr[1]:
            self.images['data'][2], pattern_configs =  self.point_at_meshgrid(x = x_pos, y = y_pos)
            self.pattern_list = np.append(self.pattern_list, [pattern_configs], 0)
        else:
            print("Undefined Method")
        # pdb.set_trace()
        self.pattern_name = "freq_[%s, %s]_%s.png"%(x_pos, y_pos, method)

    def hor_line(self):
        """
        Produce sine wave pattern for a series of sine waves that produce a horizontal line of frequencies
        """
        if int(self.user_x.get()) or self.user_x.get() == '0':
            x_pos = int(self.user_x.get())
        else:
            x_pos = 10
            print("x_pos set to 10")

        if int(self.user_y.get()) or self.user_y.get() == '0':
            y_pos = int(self.user_y.get())
        else:
            y_pos = 10
            print("y_pos set to 10")

        if int(self.user_line_len.get()) or self.user_line_len.get() == '0':
            line_len = int(self.user_line_len.get())
        else:
            line_len = 10
            print("line_len set to 10")

        points = []
        for i in range(line_len):
            points.append((x_pos+i, y_pos))

        method = self.method.get()

        if method == self.method_arr[0]:
            self.images['data'][2] =  self.points_of_arr(arr = points, method = 0)
        elif method == self.method_arr[1]:
            self.images['data'][2] =  self.points_of_arr(arr = points, method = 1)
        else:
            print("hor_line: Undefined Method")

        self.pattern_name = "hLine_%s_[%s, %s]_%s.png"%(line_len, x_pos, y_pos, method)

    def ver_line(self):
        """
        Produce sine wave pattern for a series of sine waves that produce a vertical line of frequencies
        """
        if int(self.user_x.get()) or self.user_x.get() == '0':
            x_pos = int(self.user_x.get())
        else:
            x_pos = 10
            print("x_pos set to 10")

        if int(self.user_y.get()) or self.user_y.get() == '0':
            y_pos = int(self.user_y.get())
        else:
            y_pos = 10
            print("y_pos set to 10")

        if int(self.user_line_len.get()) or self.user_line_len.get() == '0':
            line_len = int(self.user_line_len.get())
        else:
            line_len = 10
            print("line_len set to 10")

        points = []
        for i in range(line_len):
            points.append((x_pos, y_pos+i))

        method = self.method.get()

        if method == self.method_arr[0]:
            self.images['data'][2] =  self.points_of_arr(arr = points, method = 0)
        elif method == self.method_arr[1]:
            self.images['data'][2] =  self.points_of_arr(arr = points, method = 1)
        else:
            print("hor_line: Undefined Method")

        self.pattern_name = "vLine_%s_[%s, %s]_%s.png"%(line_len ,x_pos, y_pos, method)

    def diagnal_line(self):
        """
        Produce sine wave pattern for a series of sine waves that produce a diagonal line of frequencies
        """
        if int(self.user_x.get()) or self.user_x.get() == '0':
            x_pos = int(self.user_x.get())
        else:
            x_pos = 10
            print("x_pos set to 10")

        if int(self.user_y.get()) or self.user_y.get() == '0':
            y_pos = int(self.user_y.get())
        else:
            y_pos = 10
            print("y_pos set to 10")

        if int(self.user_line_len.get()) or self.user_line_len.get() == '0':
            line_len = int(self.user_line_len.get())
        else:
            line_len = 10
            print("line_len set to 10")

        if int(self.user_angle.get()) or self.user_angle.get() == '0':
                angle = int(self.user_angle.get())
        else:
            angle = 10
            print("angle set to 10")

        points = []
        slope = np.tan(np.radians(angle))

        for x in range(x_pos, x_pos + line_len):
            new_y = slope * (x-x_pos)+y_pos
            new_y = np.round(new_y)
            points.append((x, new_y))

        method = self.method.get()

        if method == self.method_arr[0]:
            self.images['data'][2] =  self.points_of_arr(arr = points, method = 0)
        elif method == self.method_arr[1]:
            self.images['data'][2] =  self.points_of_arr(arr = points, method = 1)
        else:
            print("diagnal_line: Undefined Method")

        self.pattern_name = "dLine_%s_%s\N{DEGREE SIGN}_[%s, %s]_%s.png"%(line_len, angle,x_pos, y_pos, method)

    def uploaded_pattern(self):
        """
        Produce sine wave pattern for a series of sine waves 
        that produce the input image drawn with frequencies
        """
        method = self.method.get()
        data = np.zeros((self.height, self.width))
        count = 0 # number of sin patterns summed 
        for column in range(self.width):
            for row in range(self.height):
                color = self.images['data'][0][row, column]
                if color != 0:
                    if method == self.method_arr[0]: # old Method
                        temp_data, pattern_configs = self.point_at_old(x= column, y= row, value=color)
                        data += temp_data
                        self.pattern_list = np.append(self.pattern_list, [pattern_configs], 0)
                    elif method == self.method_arr[1]: # meshgrid Method
                        temp_data, pattern_configs = self.point_at_meshgrid(x= column, y= row, value=color)
                        data += temp_data
                        self.pattern_list = np.append(self.pattern_list, [pattern_configs], 0)
                    else:
                        print("points_of_arr: Undefined Method")
                    count += 1
                    self.progress_bar_value = count
                    self.progress_label= "Processing (%d out of %d)"%(count,self.grating_count)
                    self.update_gui.set("Progressbar")
        self.images['data'][2] = (data / count)

        self.pattern_name = "[%s].png"%(self.file_name)
        
    def point_slope(self):
        """
        Produce a Sawtooth Pattern using point slope form
        """
        
        if int(self.user_angle.get()) or self.user_angle.get() == '0':
            angle = int(self.user_angle.get())
        else:
            angle = 10
            print("angle set to 10")
            
        if int(self.user_y_max.get()) or self.user_y_max.get() == '0':
            y_max = int(self.user_y_max.get())
        else:
            y_max = 255
            print("y_max set to 255")
            
        if int(self.user_y_min.get()) or self.user_y_min.get() == '0':
            y_min = int(self.user_y_min.get())
        else:
            y_min = 20
            print("y_min set to 20")
            
        if int(self.user_x_max.get()) or self.user_x_max.get() == '0':
            x_max = int(self.user_x_max.get())
        else:
            x_max = 80
            print("x_max set to 80")
            
        slope = (y_max-y_min)/x_max
        array_width = int(np.ceil( np.sqrt(pow(self.width, 2) + pow(self.height, 2))))
        array_height = array_width
        data = np.zeros((array_height, array_width), dtype = np.uint16)
        
        for i in range(array_width):
            color = slope * (i % x_max) + y_min
            data[:,i] = color
            
        img = Image.fromarray(data)
        img = img.convert('L')
        img = img.rotate(angle)
        img = self.center_crop(img, array_width, array_height, self.width, self.height)
        self.images['data'][2] = np.asarray(img)
        

        x=None 
        y=None
        freq=None
        value=None
        pattern_configs = {'x':x, 'y':y, 'angle':angle, 'freq': freq, 'value':value}
        self.pattern_list = np.append(self.pattern_list, [pattern_configs], 0)

    def save_image(self, image: Image, folder_path, pattern_name=None):
        """
        Saves image in the current to folder path with pattern name as png
        """
        if pattern_name:
            file_name = pattern_name
        else:
            file_name = "Default.png"
        file_name = os.path.join(folder_path, file_name)
        image.save(file_name)

    def create_fft(self):
        """
        Takes the fourier transform of the prodcued sum of sine wave pattern
        """
        self.raw_fft = np.fft.fft2(self.images['data'][2])
        if self.fft_shift_state.get():
            self.images['data'][1] = np.fft.fftshift(self.raw_fft)
        else:
            self.images['data'][1] = self.raw_fft

        self.images['data'][1] = np.abs(self.images['data'][1])
        max_value = np.max(self.images['data'][1])
        temp_index = np.unravel_index(np.argmax(self.images['data'][1]), self.images['data'][1].shape)
        temp_value = self.images['data'][1][temp_index]
        self.images['data'][1][temp_index] = 0
        max_value = np.max(self.images['data'][1])
        self.images['data'][1][temp_index] = temp_value


        if max_value <= 0:
            c = 0
        else:
            c = 255/(max_value)
        self.images['data'][1] = c * self.images['data'][1]
        
        self.images['images'][1] = Image.fromarray(self.images['data'][1])
        self.images['images'][1] = self.images['images'][1].convert('L')
        self.thumbnail_fft = self.images['images'][1].copy()
        self.thumbnail_fft.thumbnail(self.thumbnail_size)
        self.images['tk_images'][1] = ImageTk.PhotoImage(self.thumbnail_fft)

    def process(self):
        """
        Uses input parameters to start the progress bar, 
        manipulate the image and called the appropriate function
        """
        self.progress_bar_value = 0
        self.pattern_list = np.array([])
        # self.process_frame.update()

        self.update_gui.set("Progressbar")

        color_state = self.upload_color_state.get()
        if color_state == "0":
            temp_data = np.asarray(self.images["images"][0])
            temp_data = self.binary_threshold(temp_data, 128)
            self.images["images"][0] = Image.fromarray(temp_data).convert('L')
        elif color_state == "1":
            gray_min = int(self.gray_min.get()) if int(self.gray_min.get()) else 0
            gray_max = int(self.gray_max.get()) if int(self.gray_max.get()) else 255
            temp_data = np.asarray(self.images["images"][0])
            temp_data = np.where(temp_data<gray_min, gray_min, temp_data)
            temp_data = np.where(temp_data>gray_max, gray_max, temp_data)
            self.images["images"][0] = Image.fromarray(temp_data).convert('L')

        self.images["data"][0] = np.asarray(self.images["images"][0])
        self.height, self.width = self.images["data"][0].shape

        try:

            if self.p_type.get() == self.types[5]:
                print("Uploaded Dim: %s X %s"%(self.width, self.height))
            elif self.square_pattern.get():
                self.width = int(self.user_width.get())
                self.height = self.width
            else:
                self.width = int(self.user_width.get())
                self.height = int(self.user_height.get())
        except:
            print("Set default dimensions because of Error")
            self.width = 2000
            self.height = self.width
        if self.user_margin_size.get():
            margin_size = int(self.user_margin_size.get())
        else:
            margin_size = 2000

        if self.margin_pattern.get():
            if self.p_type.get() == self.types[5]:
                # h_pad = (self.height * margin_size) - self.height
                # w_pad = (self.width * margin_size) - self.width
                h_pad = margin_size
                w_pad = margin_size
                self.images["data"][2] = np.pad(self.images["data"][0], [[0, h_pad],[0, w_pad]], mode='constant')
                self.images["images"][2] = Image.fromarray(self.images["data"][0]).convert('L')
                self.height, self.width = self.images["data"][0].shape
            else:
                self.width = margin_size + self.width
                self.height = margin_size + self.height

        self.grating_count = len(np.transpose(np.nonzero(self.images["data"][0])))
        self.progress_label= "Processing (%d out of %d)"%(1,self.grating_count)
        self.update_gui.set("Progressbar")

        if self.p_type.get() == self.types[0]:
            self.single_freq()
        elif self.p_type.get() == self.types[1]:
            self.single_point()
        elif self.p_type.get() == self.types[2]:
            self.hor_line()
        elif self.p_type.get() == self.types[3]:
            self.ver_line()
        elif self.p_type.get() == self.types[4]:
            self.diagnal_line()
        elif self.p_type.get() == self.types[5]:
            self.uploaded_pattern()
        elif self.p_type.get() == self.types[6]:
            self.point_slope()


        
        self.display_image()
        if self.p_type.get() != self.types[6]:
            self.images["data"][2] = np.round( self.images["data"][2]  * self.max_amplitude)
        self.create_fft()
        self.cur_image.set(self.images["names"][2])
        self.display_image()
        self.progress_bar_value = 0
        self.progress_label= ""
        self.update_gui.set("Progressbar")


    def run_sawtooth(self):
        """
        Start the process to produce Sawtooth wave pattern images
        """
        if self.data is not None:
            folder = os.path.splitext(self.pattern_name)[0]
            self.create_sawtooth_folder(folder)
        else:
            print("Error: Must process data before generating Sawtooth")

        self.progress_bar_value = 0
        self.progress_label= ""
        self.update_gui.set('Sawtooth')

    def create_sawtooth_folder(self, folder_name):
        """
        Produce sawtooth wave pattern images, in a folder with a json file containing all relevant information
        """
        full_dict = {}
        file_name = "Default"
        current_path = os.getcwd()
        folder_path = os.path.join(current_path, 'Sawtooth_Pattern_Folder/')
        folder_path = os.path.join(folder_path, folder_name)
        img = None

        self.update_gui.set('Sawtooth')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        for count, pattern in enumerate(self.pattern_list):
            if pattern['value'] is None:
                pattern['value'] = self.max_amplitude
            if pattern['angle'] is not None and pattern['freq'] is not None:
                height = 1152
                width = 1920
                y_min = 0
                y_max = 128
                x_max = width / pattern['freq']
                slope = (y_max - y_min) / x_max
                side = max(height, width)
                diag = int(np.ceil(np.sqrt(side**2 + side**2)))
                data = np.zeros((diag,diag))
                for i in range(diag):
                    color = slope * (i % x_max + y_min)
                    data[:, i] = color
                # pdb.set_trace()
                img = Image.fromarray(data).convert('L')
                angle_degrees = np.degrees(pattern['angle'])
                img = img.rotate(angle_degrees)
                data = np.asarray(img)
                data = self.crop_array_center(data, height, width)
                img = Image.fromarray(data).convert('L')
                # img = Image.fromarray(data)
                # lin_x = np.linspace(0, pattern['value'], diag)
                # lin_y = np.linspace(0, pattern['value'], diag)

                # mesh_x, mesh_y = np.meshgrid(lin_x, lin_y)

                # angled_mesh = mesh_x*np.cos(pattern['angle'])+mesh_y*np.sin(pattern['angle'])
                # angled_mesh = (angled_mesh * pattern['freq'] % self.max_amplitude)

                # angled_mesh = np.round(angled_mesh)
                # angled_mesh = self.crop_array_corner(angled_mesh, height, width)

                
                if pattern['x'] is not None and pattern['y'] is not None:
                    file_name = "[%s, %s].png"%(pattern['x'], pattern['y'])
                else:
                    file_name = "<%s, %s>.png"%(pattern['angle'], pattern['freq'])


                self.save_image(image=img, folder_path=folder_path, pattern_name=file_name)
                pattern.update({'file_name': file_name})
                full_dict[count] = pattern 
            else:
                print("Sawtooth Error: %s"%(pattern))
            self.progress_bar_value = count
            self.progress_label= "Generating Sawtooth Patterns (%d out of %d)"%(count,self.grating_count)
            self.update_gui.set('Sawtooth')

        full_dict_path = os.path.join(folder_path, 'data.json')
        with open(full_dict_path, "w") as outfile:
            json.dump(full_dict, outfile)