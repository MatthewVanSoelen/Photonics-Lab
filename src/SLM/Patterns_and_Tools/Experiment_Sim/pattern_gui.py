"""matplotlib Graphing imports"""
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from matplotlib.image import imread
from matplotlib import cm

"""Tkinter GUI imports"""
from tkinter import *
from tkinter import filedialog
from tkinter import font
from tkinter.ttk import Progressbar

from PIL import Image, ImageTk, ImageFilter, ImageDraw # Image manipulation
import numpy as np # Array manipulation

"""Pathing imports"""
import os
import ntpath 
import sys 

import json # reading/writing json files
import pdb # Debugging

class Pattern_GUI:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title('Pattern Creator')
        self.root.minsize(800,500)
        self.thumbnail_size = (450,450)

        self.create_defaults()
        self.create_frames()

    def create_defaults(self):
        """
        Initialized varible with default values.
        """

        self.width = 1920
        self.height = self.width
        self.pattern_list = np.array([])

        self.upload_data = np.zeros((self.height, self.width), dtype = np.uint16)
        self.upload_image = Image.fromarray(self.upload_data).convert('L')
        self.thumbnail_upload_image = self.upload_image.copy()
        self.thumbnail_upload_image.thumbnail(self.thumbnail_size)
        self.tk_upload_image = ImageTk.PhotoImage(self.thumbnail_upload_image)

        self.data = np.zeros((self.height, self.width), dtype = np.uint16)
        self.orig_image = Image.fromarray(self.data).convert('L')
        self.thumbnail_image = self.orig_image.copy()
        self.thumbnail_image.thumbnail(self.thumbnail_size)
        self.tk_image = ImageTk.PhotoImage(self.thumbnail_image)

        self.fft_data = np.zeros((self.height, self.width), dtype = np.uint16)
        self.raw_fft = self.fft_data
        self.fft_image = Image.fromarray(self.fft_data).convert('L')
        self.thumbnail_fft_image = self.fft_image.copy()
        self.thumbnail_fft_image.thumbnail(self.thumbnail_size)
        self.tk_fft_image = ImageTk.PhotoImage(self.thumbnail_fft_image)

        current_path = os.getcwd()
        self.folder_path = os.path.join(current_path, "Pattern_Gui_Data")
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

        self.file_path = None
        self.pattern_name = "Default"
        self.max_amplitude = 255

        self.entry_box_width = 6
        self.label_box_width = 8

        self.entry_colors = ['black', 'light cyan']
        self.bold_font = font.Font(weight="bold")

    def create_frames(self):
        """
        Create left and right GUI frames 
        """

        self.l_frame = Frame(self.root)
        self.l_frame.grid(row = 0, column = 0)

        self.fill_left_frame()

        self.r_frame = Frame(self.root)
        self.r_frame.grid(row = 0, column = 1)

        self.fill_right_frame()



    def fill_left_frame(self):
        """
        Create various elements apart of the left GUI
        """
        ################################################################################
        # Method Frame
        self.method_frame = Frame(self.l_frame, borderwidth=2, relief=SUNKEN)
        self.method_frame.pack(side="top", fill="both", expand=True)

        Label(self.method_frame,text="Method:").grid(row=0, column=0)
        self.method_arr = ['Old','Meshgrid']
        self.method_options = set(self.method_arr)
        self.method = StringVar(self.root)
        self.method.set(self.method_arr[1])
        OptionMenu(self.method_frame, self.method, *self.method_options).grid(row=0, column=1)

        ################################################################################
        # Upload Frame
        self.upload_frame = Frame(self.l_frame, borderwidth=2, relief=SUNKEN)
        self.upload_frame.pack(side="top", fill="both", expand=True)

        self.upload_pattern_button = Button(self.upload_frame, 
                                            text='Select a Pattern', 
                                            command=self.pattern_select)
        self.upload_pattern_button.grid(row=0, column=0)

        self.upload_color_state = BooleanVar(self.root)
        self.upload_color_state.set(True)
        Checkbutton(self.upload_frame, 
                    text='Black/White', 
                    variable=self.upload_color_state).grid(row=0,column=1)

        ################################################################################
        # Dimentions Frame
        self.dimensions_frame = Frame(self.l_frame, borderwidth=2, relief=SUNKEN)
        self.dimensions_frame.pack(side="top", fill="both", expand=True)

        Label(self.dimensions_frame, text= "Square=[Width, Width]").grid(row=0, column=0)

        self.square_pattern = BooleanVar(self.root)
        self.square_pattern.set(True)
        Checkbutton(self.dimensions_frame, 
                    text='Square Pattern', 
                    variable=self.square_pattern).grid(row=0,column=1)

        Label(self.dimensions_frame, text="Width:").grid(row=1, column=0)
        self.width_entry = Entry(self.dimensions_frame, width=self.entry_box_width)
        self.width_entry.grid(row=1, column=1)

        Label(self.dimensions_frame, text="Height:").grid(row=2, column=0)
        self.height_entry = Entry(self.dimensions_frame, width=self.entry_box_width)
        self.height_entry.grid(row=2, column=1)

        ################################################################################
        # Pattern Options Frame 
        self.pattern_options_frame = Frame(self.l_frame, borderwidth=2, relief=SUNKEN)
        self.pattern_options_frame.pack(side="top", fill="both", expand=True)

        select_frame = Frame(self.pattern_options_frame)
        select_frame.pack(side="top", fill="both", expand=True)
        Label(select_frame,text="Pattern Type:").grid(row=0, column=0)
        self.types = ['Single Freq','Single Point [x,y]', 'Hor. Line', 'Ver. Line', 'Diagonal Line', 'Upload']
        self.type_options = set(self.types)
        self.p_type = StringVar(self.root)
        self.p_type.set('Single Freq')
        OptionMenu(select_frame, self.p_type, *self.type_options).grid(row=0, column=1)

        freq_angle_frame = Frame(self.pattern_options_frame)
        freq_angle_frame.pack(side="top", fill="both", expand=True)
        Label(freq_angle_frame, text="Freq:", width=self.label_box_width).grid(row=0, column=0)
        self.freq_entry = Entry(freq_angle_frame, width=self.entry_box_width)
        self.freq_entry.grid(row=0, column=1)

        Label(freq_angle_frame, text="Angle:", width=self.label_box_width).grid(row=0, column=2)
        self.angle_entry = Entry(freq_angle_frame, width=self.entry_box_width)
        self.angle_entry.grid(row=0, column=3)

        coords_frame = Frame(self.pattern_options_frame)
        coords_frame.pack(side="top", fill="both", expand=True)
        Label(coords_frame, text="x:", width=self.label_box_width).grid(row=0, column=0)
        self.x_entry = Entry(coords_frame, width=self.entry_box_width)
        self.x_entry.grid(row=0, column=1)

        Label(coords_frame, text="y:", width=self.label_box_width).grid(row=0, column=2)
        self.y_entry = Entry(coords_frame, width=self.entry_box_width)
        self.y_entry.grid(row=0, column=3)        

        line_dim_frame = Frame(self.pattern_options_frame)
        line_dim_frame.pack(side="top", fill="both", expand=True)

        Label(line_dim_frame, text="Line Length:", width=self.label_box_width).grid(row=0, column=0)
        self.line_len_entry = Entry(line_dim_frame, width=self.entry_box_width)
        self.line_len_entry.grid(row=0, column=1)

        scale_pattern_frame = Frame(self.pattern_options_frame)
        scale_pattern_frame.pack(side="top", fill="both", expand=True)

        self.scale_pattern = BooleanVar(self.root)
        self.scale_pattern.set(True)
        self.scale_pattern_checkbox = Checkbutton(scale_pattern_frame, 
                    text='Scale Pattern', 
                    variable=self.scale_pattern)
        self.scale_pattern_checkbox.grid(row=0,column=0)
        self.CreateToolTip(widget = self.scale_pattern_checkbox, 
            text = "Increases the size of the image size so the input \n represents one quadrant of the final image.")

        Label(scale_pattern_frame, text="Scale factor:", width=self.label_box_width).grid(row=1, column=0)
        self.scale_factor_entry = Entry(scale_pattern_frame, width=self.entry_box_width)
        self.scale_factor_entry.grid(row=1, column=1)
        self.scale_factor_entry.insert(0, '2')
        ################################################################################
        # FFT Options Frame
        self.fft_options_frame = Frame(self.l_frame, borderwidth=2, relief=SUNKEN)
        self.fft_options_frame.pack(side="top", fill="both", expand=True)

        Label(self.fft_options_frame, text="FFT Options", font=self.bold_font).grid(row=0, column=0)

        self.fft_shift_state = BooleanVar(self.root)
        self.fft_shift_state.set(True)
        Checkbutton(self.fft_options_frame, 
                    text='Shift Fouier Tranform', 
                    variable=self.fft_shift_state).grid(row=1,column=0)

        self.process_frame = Frame(self.l_frame, borderwidth=2, relief=SUNKEN)
        self.process_frame.pack(side="top", fill="both", expand=True)
        self.process_button = Button(self.process_frame,
                                    text='Process',
                                    command= self.process)
        self.process_button.grid(row=0, column=0)

        self.progress_bar = Progressbar(self.process_frame, orient = HORIZONTAL , length = 180, mode='determinate')
        self.progress_bar.grid(row=0, column=1)

        self.gen_saw_button = Button(self.process_frame,
                                    text='Generate Sawtooth',
                                    command= self.run_sawtooth)
        self.gen_saw_button.grid(row=1, column=0)

        self.p_type.trace("w", self.update_color)
        self.update_color()
        

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

        self.p_type.set('Upload')
        self.upload_image = Image.open(self.file_path).convert('L')
        self.update_view()

    def fill_right_frame(self):
        """
        Create various elements apart of the right GUI

        """
        ################################################################################
        # Uploaded image preview
        self.uploaded_frame = Frame(self.r_frame)
        self.uploaded_frame.pack(side="left", fill="both", expand=True)

         # Frame on top of Original Image preview
        uploaded_header = Frame(self.uploaded_frame)
        uploaded_header.grid(row=0, column=0)

        # Button which displays orginal image
        self.display_upload_button = Button(uploaded_header, 
                                            text='Uploaded', 
                                            command= lambda: self.display_image(self.upload_image))
        self.display_upload_button.grid(row=0, column=0)

        # Button which saves original image
        self.save_upload_button = Button(uploaded_header,
                                        text='Save',
                                        command= lambda: self.save_image(self.upload_image, self.pattern_name, self.folder_path))
        self.save_upload_button.grid(row=0, column=1)

        # Label which holds original image thumbnail
        self.upload_image_label = Label(self.uploaded_frame, image=self.tk_image)
        self.upload_image_label.grid(row=1, column=0)
        ################################################################################
        # Produced image preview
        self.produced_frame = Frame(self.r_frame)
        self.produced_frame.pack(side="left", fill="both", expand=True)

        # Frame on top of Original Image preview
        orig_header = Frame(self.produced_frame)
        orig_header.grid(row=0, column=1)

        # Button which displays orginal image
        self.display_orig_button = Button(orig_header, 
                                            text='Produced', 
                                            command= lambda: self.display_image(self.orig_image))
        self.display_orig_button.grid(row=0, column=0)

        # Button which saves original image
        self.save_orig_button = Button(orig_header,
                                        text='Save',
                                        command= lambda: self.save_image(self.orig_image, self.pattern_name, self.folder_path))
        self.save_orig_button.grid(row=0, column=1)

        # Label which holds original image thumbnail
        self.orig_image_label = Label(self.produced_frame, image=self.tk_image)
        self.orig_image_label.grid(row=1, column=1)

        ################################################################################
        # FFT image preview
        self.fft_frame = Frame(self.r_frame)
        self.fft_frame.pack(side="left", fill="both", expand=True)

         # Frame on top of fft Image preview
        fft_header = Frame(self.fft_frame)
        fft_header.grid(row=0, column=0)

        # Button which displays fft image
        self.display_fft_button = Button(fft_header, 
                                            text='FFT', 
                                            command= lambda: self.display_image(self.fft_image))
        self.display_fft_button.grid(row=0, column=0)

        # Button which saves fft image
        self.save_fft_button = Button(fft_header,
                                        text='Save',
                                        command= lambda: self.save_image(image=self.fft_image, pattern_name=self.pattern_name, folder_path=self.folder_path))
        self.save_fft_button.grid(row=0, column=1)

        self.graph_fft_button = Button(fft_header,
                                        text='Graph',
                                        command=self.graph_fft)
        self.graph_fft_button.grid(row=0, column=2)

        # Label which holds fft image thumbnail
        self.fft_image_label = Label(self.fft_frame, image=self.tk_fft_image)
        self.fft_image_label.grid(row=1, column=0)

    def update_view(self):
        """
        Updates the view with the appropriate preview images
        """
        if self.p_type.get() == self.types[5]: 
            self.thumbnail_upload_image = self.upload_image.copy()
            self.thumbnail_upload_image.thumbnail(self.thumbnail_size)
            self.tk_upload_image = ImageTk.PhotoImage(self.thumbnail_upload_image)

            self.display_upload_button.config(text="Upload: %s"%(self.pattern_name))
            self.upload_image_label.config(image=self.tk_upload_image)

        self.orig_image = Image.fromarray(self.data).convert('L')
        self.thumbnail_image = self.orig_image.copy()
        self.thumbnail_image.thumbnail(self.thumbnail_size)
        self.tk_image = ImageTk.PhotoImage(self.thumbnail_image)

        self.display_orig_button.config(text="Produced: %s"%(self.pattern_name))
        self.orig_image_label.config(image=self.tk_image)

        self.fft_image = Image.fromarray(self.fft_data).convert('L')
        self.thumbnail_fft_image = self.fft_image.copy()
        self.thumbnail_fft_image.thumbnail(self.thumbnail_size)
        self.tk_fft_image = ImageTk.PhotoImage(self.thumbnail_fft_image)

        self.display_fft_button.config(text="FFT: %s"%(self.pattern_name))
        self.fft_image_label.config(image=self.tk_fft_image)


    def update_color(self, *args):
        """
        Updates the colors of the entry boxes, depending on the select pattern type.
        Makes needed parameters blue, and the others black.
        """
        self.freq_entry.config(bg= self.entry_colors[0])
        self.angle_entry.config(bg= self.entry_colors[0])
        self.x_entry.config(bg= self.entry_colors[0])
        self.y_entry.config(bg= self.entry_colors[0])
        self.line_len_entry.config(bg= self.entry_colors[0])
        
        if self.p_type.get() == self.types[0]:
            self.freq_entry.config(bg= self.entry_colors[1])
            self.angle_entry.config(bg= self.entry_colors[1])
        elif self.p_type.get() == self.types[1]:
            self.x_entry.config(bg= self.entry_colors[1])
            self.y_entry.config(bg= self.entry_colors[1])
        elif self.p_type.get() == self.types[2] or self.p_type.get() == self.types[3]:
            self.x_entry.config(bg= self.entry_colors[1])
            self.y_entry.config(bg= self.entry_colors[1])
            self.line_len_entry.config(bg= self.entry_colors[1])
        elif self.p_type.get() == self.types[4]:
            self.angle_entry.config(bg= self.entry_colors[1])
            self.x_entry.config(bg= self.entry_colors[1])
            self.y_entry.config(bg= self.entry_colors[1])
            self.line_len_entry.config(bg= self.entry_colors[1])

    def binary_threshold(self, arr, threshold:int=128):
        """
        Applies a binary threshold to an array
        """

        arr = np.where(arr < threshold, arr, self.max_amplitude)
        arr = np.where(arr >= threshold, arr, 0)
        return arr

    def crop_image_corner(self, image):
        """
        Crops image to top left corner
        """
        return image.crop((0,0,self.width, self.height))

    def crop_array_corner(self, arr, height, width):
        """
        Crops array to top left corner
        """
        return arr[0:height, 0:width]

    def crop_image_center(self, image, array_width, array_height, width, height):
        """
        Crops image to center 
        """
        x_margin = (array_width - width) //2
        y_margin = (array_height - height) // 2
        return image.crop((x_margin, y_margin, x_margin + width, y_margin + height))

    def crop_array_center(self, arr, height, width):
        """
        Crops array to center 
        """
        x_margin = width//2
        y_margin = height//2
        return arr[y_margin:y_margin+height, x_margin:x_margin+width]

    def display_image(self, img: Image):
        """
        Opens system view for png image
        """
        img.show()

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

    def CreateToolTip(self, widget, text):
        """
        Creates tool tip information hover over parameter
        """
        toolTip = ToolTip(widget)
        def enter(event):
            toolTip.showtip(text)
        def leave(event):
            toolTip.hidetip()
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def process(self):
        """
        Uses input parameters to start the progress bar, 
        manipulate the image and called the appropriate function
        """
        self.progress_bar['value'] = 0
        self.pattern_list = np.array([])
        self.process_frame.update()
        if self.upload_color_state.get():
            temp_data = np.asarray(self.upload_image)
            temp_data = self.binary_threshold(temp_data, 128)
            self.upload_image =  Image.fromarray(temp_data).convert('L')
        self.upload_data = np.asarray(self.upload_image)
        self.height, self.width = self.upload_data.shape

        try:

            if self.p_type.get() == self.types[5]:
                print("Uploaded Dim: %s X %s"%(self.width, self.height))
            elif self.square_pattern.get():
                self.width = int(self.width_entry.get())
                self.height = self.width
            else:
                self.width = int(self.width_entry.get())
                self.height = int(self.height_entry.get())
        except:
            print("Set default dimensions because of Error")
            self.width = 2000
            self.height = self.width
        if self.scale_factor_entry.get():
            scale_factor = int(self.scale_factor_entry.get())
        else:
            scale_factor = 2

        if self.scale_pattern.get():
            if self.p_type.get() == self.types[5]:
                h_pad = (self.height * scale_factor) - self.height
                w_pad = (self.width * scale_factor) - self.width
                self.upload_data = np.pad(self.upload_data, [[0, h_pad],[0, w_pad]], mode='constant')
                self.upload_image = Image.fromarray(self.upload_data).convert('L')
                self.height, self.width = self.upload_data.shape
            else:
                self.width = scale_factor * self.width
                self.height = scale_factor * self.height

        self.grating_count = len(np.transpose(np.nonzero(self.upload_data)))
        print("count: ",self.grating_count)
        self.progress_bar.config(maximum = self.grating_count)

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


        
        self.update_view()
        self.data = np.round( self.data  * self.max_amplitude)
        self.create_fft()
        self.update_view()
        self.progress_bar['value'] = 0
        self.process_frame.update()

    def run_sawtooth(self):
        """
        Start the process to produce Sawtooth wave pattern images
        """
        if self.data is not None:
            folder = os.path.splitext(self.pattern_name)[0]
            self.create_sawtooth_folder(folder)
        else:
            print("Error: Must process data before generating Sawtooth")

        self.progress_bar['value'] = 0
        self.process_frame.update()

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
            print("freq: %s, angle: %s" %(freq, angle))
        elif freq is None or angle is None:
            print("point_at_meshgrid: Incomplete coords, freq and angle")
        
        amplitude = value/(self.max_amplitude * 2)
        mesh_x, mesh_y = np.meshgrid(lin_x, lin_y)
        angled_mesh = mesh_x*np.cos(angle)+mesh_y*np.sin(angle)
        print("freq: ", freq)
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
        # data = self.crop_array_corner(data, self.height, self.width)
        return data, {'x':x, 'y':y, 'angle':angle, 'freq':freq, 'value':value}

    def points_of_arr(self, arr, method:int):
        """
        return array containing a sum of sin patterns 
        representing the array of given points, using the given method
        """
        data = np.zeros((self.height, self.width))
        for point in arr:
            print("[%s, %s]"%(point[0], point[1]))
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
        if float(self.freq_entry.get()):
            freq = float(self.freq_entry.get())
        else:
            freq = 1.2
            print("Freq set to 1.2")

        if int(self.angle_entry.get()) or self.angle_entry.get() == '0':
            angle = int(self.angle_entry.get())
        else:
            angle = 10
            print("angle set to 10")

        method = self.method.get()

        if method == "Old":
            self.data, pattern_configs = self.point_at_old(freq = freq, angle = angle)
            self.pattern_list = np.append(self.pattern_list, [pattern_configs], 0)
        elif method == "Meshgrid":
            self.data, pattern_configs = self.point_at_meshgrid(freq = freq, angle = angle)
            self.pattern_list = np.append(self.pattern_list, [pattern_configs], 0)
        else:
            print("Undefined Method")

        self.pattern_name = "freq_%s_%s\N{DEGREE SIGN}_%s.png"%(freq, angle, method)

    def single_point(self):
        """
        Produce sine wave pattern for a single with a single frequency at given coordinates
        """
        if int(self.x_entry.get()) or self.x_entry.get() == '0':
            x_pos = int(self.x_entry.get())
        else:
            x_pos = 10
            print("x_pos set to 10")

        if int(self.y_entry.get()) or self.y_entry.get() == '0':
            y_pos = int(self.y_entry.get())
        else:
            y_pos = 10
            print("y_pos set to 10")

        method = self.method.get()
        print("[%s, %s]"%(x_pos, y_pos))
        if method == self.method_arr[0]:
            self.data, pattern_configs =  self.point_at_old(x = x_pos, y = y_pos)
            self.pattern_list = np.append(self.pattern_list, [pattern_configs], 0)
        elif method == self.method_arr[1]:
            self.data, pattern_configs =  self.point_at_meshgrid(x = x_pos, y = y_pos)
            self.pattern_list = np.append(self.pattern_list, [pattern_configs], 0)
        else:
            print("Undefined Method")
        # pdb.set_trace()
        self.pattern_name = "freq_[%s, %s]_%s.png"%(x_pos, y_pos, method)

    def hor_line(self):
        """
        Produce sine wave pattern for a series of sine waves that produce a horizontal line of frequencies
        """
        if int(self.x_entry.get()) or self.x_entry.get() == '0':
            x_pos = int(self.x_entry.get())
        else:
            x_pos = 10
            print("x_pos set to 10")

        if int(self.y_entry.get()) or self.y_entry.get() == '0':
            y_pos = int(self.y_entry.get())
        else:
            y_pos = 10
            print("y_pos set to 10")

        if int(self.line_len_entry.get()) or self.line_len_entry.get() == '0':
            line_len = int(self.line_len_entry.get())
        else:
            line_len = 10
            print("line_len set to 10")

        points = []
        for i in range(line_len):
            points.append((x_pos+i, y_pos))

        method = self.method.get()

        if method == self.method_arr[0]:
            self.data =  self.points_of_arr(arr = points, method = 0)
        elif method == self.method_arr[1]:
            self.data =  self.points_of_arr(arr = points, method = 1)
        else:
            print("hor_line: Undefined Method")

        self.pattern_name = "hLine_%s_[%s, %s]_%s.png"%(line_len, x_pos, y_pos, method)

    def ver_line(self):
        """
        Produce sine wave pattern for a series of sine waves that produce a vertical line of frequencies
        """
        if int(self.x_entry.get()) or self.x_entry.get() == '0':
            x_pos = int(self.x_entry.get())
        else:
            x_pos = 10
            print("x_pos set to 10")

        if int(self.y_entry.get()) or self.y_entry.get() == '0':
            y_pos = int(self.y_entry.get())
        else:
            y_pos = 10
            print("y_pos set to 10")

        if int(self.line_len_entry.get()) or self.line_len_entry.get() == '0':
            line_len = int(self.line_len_entry.get())
        else:
            line_len = 10
            print("line_len set to 10")

        points = []
        for i in range(line_len):
            points.append((x_pos, y_pos+i))

        method = self.method.get()

        if method == self.method_arr[0]:
            self.data =  self.points_of_arr(arr = points, method = 0)
        elif method == self.method_arr[1]:
            self.data =  self.points_of_arr(arr = points, method = 1)
        else:
            print("hor_line: Undefined Method")

        self.pattern_name = "vLine_%s_[%s, %s]_%s.png"%(line_len ,x_pos, y_pos, method)

    def diagnal_line(self):
        """
        Produce sine wave pattern for a series of sine waves that produce a diagonal line of frequencies
        """
        if int(self.x_entry.get()) or self.x_entry.get() == '0':
            x_pos = int(self.x_entry.get())
        else:
            x_pos = 10
            print("x_pos set to 10")

        if int(self.y_entry.get()) or self.y_entry.get() == '0':
            y_pos = int(self.y_entry.get())
        else:
            y_pos = 10
            print("y_pos set to 10")

        if int(self.line_len_entry.get()) or self.line_len_entry.get() == '0':
            line_len = int(self.line_len_entry.get())
        else:
            line_len = 10
            print("line_len set to 10")

        if int(self.angle_entry.get()) or self.angle_entry.get() == '0':
                angle = int(self.angle_entry.get())
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
            self.data =  self.points_of_arr(arr = points, method = 0)
        elif method == self.method_arr[1]:
            self.data =  self.points_of_arr(arr = points, method = 1)
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
                color = self.upload_data[row, column]
                if color != 0:
                    print("upload: [%s,%s]:%s"%(column, row, color))
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
                    self.progress_bar['value'] = count
                    self.process_frame.update()
        self.data = (data / count)

        self.pattern_name = "[%s].png"%(self.file_name)

    def create_fft(self):
        """
        Takes the fourier transform of the prodcued sum of sine wave pattern
        """
        self.raw_fft = np.fft.fft2(self.data)
        if self.fft_shift_state.get():
            self.fft_data = np.fft.fftshift(self.raw_fft)
        else:
            self.fft_data = self.raw_fft

        self.fft_data = np.abs(self.fft_data)
        max_value = np.max(self.fft_data)
        temp_index = np.unravel_index(np.argmax(self.fft_data), self.fft_data.shape)
        temp_value = self.fft_data[temp_index]
        self.fft_data[temp_index] = 0
        max_value = np.max(self.fft_data)
        self.fft_data[temp_index] = temp_value

        print(max_value, np.unravel_index(np.argmax(self.fft_data), self.fft_data.shape))

        if max_value <= 0:
            c = 0
        else:
            c = 255/(max_value)
        self.fft_data = c * self.fft_data
        
        self.fft_image = Image.fromarray(self.fft_data)
        self.fft_image = self.fft_image.convert('L')
        self.thumbnail_fft = self.fft_image.copy()
        self.thumbnail_fft.thumbnail(self.thumbnail_size)
        self.tk_fft = ImageTk.PhotoImage(self.thumbnail_fft)

    def graph_fft(self):
        """
        produces amplitude vesus frequency graph
        """
        if self.raw_fft is None:
            print("Please run pattern first.")
        else:
            y_range,x_range = self.raw_fft.shape
            center_line_index = y_range//2
            x = range(0,x_range)
            plt.fill_between(x, self.raw_fft[center_line_index])
            plt.xlabel("x")
            plt.ylabel("amplitude")
            plt.legend()
            plt.show(self.pattern_name)

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

        self.progress_bar.config(maximum=len(self.pattern_list))
        self.process_frame.update()
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
                # data = np.asarray(img)
                # data = self.crop_array_center(data, height, width)
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
            self.progress_bar['value'] = count
            self.process_frame.update()

        full_dict_path = os.path.join(folder_path, 'data.json')
        with open(full_dict_path, "w") as outfile:
            json.dump(full_dict, outfile)

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

root = Tk()
np.set_printoptions(threshold=sys.maxsize)
gui = Pattern_GUI(root)
root.mainloop()

