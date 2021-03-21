from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from matplotlib.image import imread
from matplotlib import cm
import pdb

from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import numpy as np 

import os
import ntpath
import sys

class Pattern_GUI:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title('Pattern Creator')
        self.root.minsize(800,500)
        self.root.config(bg='gainsboro')
        self.thumbnail_size = (450,450)

        self.create_defaults()
        self.create_frames()

    def create_defaults(self):
        self.width = 1920
        self.height = self.width

        self.data = np.zeros((self.height, self.width), dtype = np.uint16)
        self.orig_image = Image.fromarray(self.data).convert('L')
        self.thumbnail_image = self.orig_image.copy()
        self.thumbnail_image.thumbnail(self.thumbnail_size)
        self.tk_image = ImageTk.PhotoImage(self.thumbnail_image)

        current_path = os.getcwd()
        self.folder_path = os.path.join(current_path, "Pattern_Gui_Data")
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

        self.file_path = None
        self.pattern_name = "Default"
        self.amplitude = 127

        self.entry_box_width = 6
        self.label_box_width = 8

    def create_frames(self):
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
        self.method_options = {'Old','Meshgrid'}
        self.method = StringVar(self.root)
        self.method.set('Old')
        OptionMenu(self.method_frame, self.method, *self.method_options).grid(row=0, column=1)

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
        self.types = ['Single Freq','Single Point [x,y]', 'Point of angle', 'Hor. Line', 'Ver. Line', 'Diagonal Line']
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
        Label(line_dim_frame, text="Line Width:", width=self.label_box_width).grid(row=0, column=0)
        self.line_width_entry = Entry(line_dim_frame, width=self.entry_box_width)
        self.line_width_entry.grid(row=0, column=1)

        Label(line_dim_frame, text="Line Height:", width=self.label_box_width).grid(row=0, column=2)
        self.line_height_entry = Entry(line_dim_frame, width=self.entry_box_width)
        self.line_height_entry.grid(row=0, column=3)

        process_frame = Frame(self.pattern_options_frame)
        process_frame.pack(side="top", fill="both", expand=True)
        self.process_button = Button(process_frame,
                                    text='Process',
                                    command= self.process)
        self.process_button.grid(row=0, column=0)


    def fill_right_frame(self):
        """
        Create various elements apart of the right GUI

        """
        # Frame on top of Original Image preview
        orig_header = Frame(self.r_frame)
        orig_header.grid(row=0, column=0)

        # Button which displays orginal image
        self.display_orig_button = Button(orig_header, 
                                            text='Default', 
                                            command= lambda: self.display_image(self.orig_image))
        self.display_orig_button.grid(row=0, column=0)

        # Button which saves original image
        self.save_orig_button = Button(orig_header,
                                        text='Save',
                                        command= lambda: self.save_image(self.orig_image))
        self.save_orig_button.grid(row=0, column=1)

        # Label which holds original image thumbnail
        self.orig_image_label = Label(self.r_frame, image=self.tk_image)
        self.orig_image_label.grid(row=1, column=0)

    def update_view(self):
        self.orig_image = Image.fromarray(self.data).convert('L')
        self.thumbnail_image = self.orig_image.copy()
        self.thumbnail_image.thumbnail(self.thumbnail_size)
        self.tk_image = ImageTk.PhotoImage(self.thumbnail_image)

        self.display_orig_button.config(text="Original: %s"%(self.pattern_name))
        self.orig_image_label.config(image=self.tk_image)

    def crop_image_corner(self, image):
        return image.crop((0,0,self.width, self.height))

    def crop_array_corner(self, arr):
        return arr[0:self.height, 0:self.width]

    def crop_image_center(self, image, array_width, array_height, width, height):
        x_margin = (array_width - width) //2
        y_margin = (array_height - height) // 2
        return image.crop((x_margin, y_margin, x_margin + width, y_margin + height))

    def crop_array_center(self,arr):
        x_margin = self.width//2
        y_margin = self.height//2
        return arr[y_margin:y_margin+self.height, x_margin:x_margin+self.width]

    def display_image(self, img: Image):
        img.show()

    def save_image(self, image: Image):
        if self.pattern_name:
            file_name = self.pattern_name
        else:
            file_name = "Default.png"
        file_name = os.path.join(self.folder_path, file_name)
        image.save(file_name)

    def process(self):
        try:
            if self.square_pattern.get():
                self.width = int(self.width_entry.get())
                self.height = self.width

            else:
                self.width = int(self.width_entry.get())
                self.height = int(self.height_entry.get())
        except:
            print("Set default dimensions because of Error")
            self.width = 2000
            self.height = self.width

        if self.method.get() == "Old":
            if self.p_type.get() == self.types[0]:
                self.single_freq()
            elif self.p_type.get() == self.types[1]:
                self.single_point()
            elif self.p_type.get() == self.types[2]:
                self.angle_point()
            elif self.p_type.get() == self.types[3]:
                self.hor_line()
            elif self.p_type.get() == self.types[4]:
                self.ver_line()
        elif self.method.get() == "Meshgrid":
            if self.p_type.get() == self.types[0]:
                self.single_freq_meshgrid()
            elif self.p_type.get() == self.types[1]:
                self.point_at_meshgrid()
            
        self.update_view()

    def single_freq(self):
        self.data = np.zeros((self.height, self.width), dtype = np.uint16)

        if float(self.freq_entry.get()):
            freq = float(self.freq_entry.get())
        else:
            freq = 1.2
            print("Freq set to 1.2")

        self.pattern_name = "freq_%s.png"%(freq)

        x = np.linspace(-np.pi, np.pi, self.width)

        for i in range(self.height):
            gray = self.amplitude * (np.sin(x * freq) + 1)
            self.data[i] = gray

    def single_point(self):
        self.data = np.zeros((2*self.height, 2*self.width), dtype = np.uint16)
        # pdb.set_trace()
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

        dist = np.floor(np.sqrt( x_pos**2 + y_pos**2))
        freq = self.get_coefficient(self.width, dist)

        if x_pos < 1:
            angle = 0
        else:
            angle = np.degrees(np.arctan(y_pos/x_pos))

        self.pattern_name = "point_at_[%s,%s].png"%(x_pos, y_pos)

        x = np.linspace(-np.pi, np.pi, 2*self.width)

        for i in range(2*self.height):
            gray = self.amplitude * (np.sin(x * (freq*2)) + 1)
            self.data[i] = gray
        # pdb.set_trace()
        img = Image.fromarray(self.data).convert('L')
        img = img.rotate(angle)
        self.data = np.asarray(img, dtype=np.uint16)
        self.data = self.crop_array_center(self.data)

    def angle_point(self):
        self.data = np.zeros((2*self.height, 2*self.width), dtype = np.uint16)
        # pdb.set_trace()
        if int(self.freq_entry.get()) or self.freq_entry.get() == '0':
            freq = int(self.freq_entry.get())
        else:
            freq = 10
            print("freq set to 10")

        if int(self.angle_entry.get()) or self.angle_entry.get() == '0':
            angle = int(self.angle_entry.get())
        else:
            angle = 10
            print("angle set to 10")

        self.pattern_name = "%s_point_of_%s\N{DEGREE SIGN}.png"%(freq, angle)

        x = np.linspace(-np.pi, np.pi, 2*self.width)

        for i in range(2*self.height):
            gray = self.amplitude * (np.sin(x * (freq*2)) + 1)
            self.data[i] = gray
        # pdb.set_trace()
        img = Image.fromarray(self.data).convert('L')
        img = img.rotate(angle)
        self.data = np.asarray(img, dtype=np.uint16)
        self.data = self.crop_array_center(self.data)

    def hor_line(self):
        self.data = np.zeros((2*self.height, 2*self.width))
        temp_data = np.zeros((2*self.height, 2*self.width))

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

        if int(self.line_width_entry.get()) or self.line_width_entry.get() == '0':
            line_width = int(self.line_width_entry.get())
        else:
            line_width = 10
            print("line_width set to 10")

        self.pattern_name = "hor_%s_[%s,%s].png"%(line_width, x_pos, y_pos)

        x = np.linspace(-np.pi, np.pi, 2*self.width)

        for i in range(x_pos, x_pos+line_width):
            print(i)
            dist = np.floor(np.sqrt( i**2 + y_pos**2))
            freq = self.get_coefficient(self.width, dist)

            if i < 1:
                angle = 0
            else:
                angle = np.degrees(np.arctan(y_pos/i))


            for i in range(2*self.height):
                gray = self.amplitude * (np.sin(x * (freq*2)) + 1)
                temp_data[i] = gray
                pdb.set_trace()
            img = Image.fromarray(temp_data).convert('L')
            img = img.rotate(angle)
            temp_data = np.asarray(img, dtype=np.uint16)
            self.data = temp_data + self.data
        self.data = self.data / line_width
        self.data = self.crop_array_center(self.data)

    def ver_line(self):
        self.data = np.zeros((2*self.height, 2*self.width), dtype = np.uint16)
        temp_data = np.zeros((2*self.height, 2*self.width), dtype = np.uint16)

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

        if int(self.line_height_entry.get()) or self.line_height_entry.get() == '0':
            line_height = int(self.line_height_entry.get())
        else:
            line_height = 10
            print("line_width set to 10")

        self.pattern_name = "ver_%s_[%s,%s].png"%(line_height, x_pos, y_pos)

        x = np.linspace(-np.pi, np.pi, 2*self.width)

        for i in range(y_pos, y_pos+line_height):
            print(i)
            dist = np.floor(np.sqrt( i**2 + y_pos**2))
            freq = self.get_coefficient(self.width, dist)

            if x_pos < 1:
                angle = 0
            else:
                angle = np.degrees(np.arctan(i/x_pos))


            for i in range(2*self.height):
                gray = self.amplitude * (np.sin(x * (freq*2)) + 1)
                temp_data[i] = gray
            img = Image.fromarray(temp_data).convert('L')
            img = img.rotate(angle)
            temp_data = np.asarray(img, dtype=np.uint16)
            self.data = temp_data + self.data
        self.data = self.data / line_height
        self.data = self.crop_array_center(self.data)

    def single_freq_meshgrid(self):
        if float(self.freq_entry.get()) or self.freq_entry.get() == '0':
            freq = float(self.freq_entry.get())
        else:
            freq = 10
            print("freq set to 10")

        x = np.linspace(0, 2*np.pi, self.width)
        y = np.linspace(0, 2*np.pi*(self.height/self.width), self.height)

        self.pattern_name = "freq_%s_meshgrid.png"%(freq)

        mesh_x, mesh_y = np.meshgrid(x, y)
        angle = 0
        angled_mesh = mesh_x*np.cos(angle)+mesh_y*np.sin(angle)
        self.data = self.amplitude * (np.sin(angled_mesh * freq) + 1)

    def point_at_meshgrid(self):
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

        x = np.linspace(0, 2*np.pi, self.width)
        y = np.linspace(0, 2*np.pi*(self.height/self.width), self.height)

        dist = np.sqrt( x_pos**2 + y_pos**2)
        freq = self.get_coefficient(self.width, dist)
        if x_pos < 1:
            angel = 0
        else:
            angle = - np.arctan(y_pos/x_pos)
        # angel = 0
        # print(dist, freq, coords, angel)

        self.pattern_name = "point_meshgrid_[%s,%s].png"%(x_pos, y_pos)

        mesh_x, mesh_y = np.meshgrid(x, y)
        angled_mesh = mesh_x*np.cos(angle)+mesh_y*np.sin(angle)
        self.data = self.amplitude * (np.sin(angled_mesh * freq) + 1)


    def get_coefficient(self, width, dist):
        scaling_constant = 1600.0
        return (dist/scaling_constant) * width



root = Tk()
gui = Pattern_GUI(root)
root.mainloop()

