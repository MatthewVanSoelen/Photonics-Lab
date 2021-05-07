from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from matplotlib.image import imread
from matplotlib import cm
import pdb
import csv


from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import numpy as np 

import os
import ntpath
import sys

class SimGUI:
    def __init__(self, root: Tk):

        self.root = root
        self.root.title('Surface Grating Simulation')
        self.root.minsize(800,500)
        self.root.config(bg='gainsboro')
        self.thumbnail_size = (450,450)

        self.create_defaults()
        self.create_frames()

    def create_defaults(self):
        self.width = 1920
        self.height = 1152

        self.data = np.zeros((self.height, self.width), dtype = np.uint16)
        self.orig_image = Image.fromarray(self.data).convert('L')
        self.thumbnail_image = self.orig_image.copy()
        self.thumbnail_image.thumbnail(self.thumbnail_size)
        self.tk_image = ImageTk.PhotoImage(self.thumbnail_image)

        self.fft = self.data
        self.fft_image = self.orig_image
        self.thumbnail_fft = self.thumbnail_image
        self.tk_fft = self.tk_image

        self.i_fft = self.data
        self.i_fft_image = self.orig_image
        self.thumbnail_i_fft = self.thumbnail_image
        self.tk_i_fft = self.tk_image

        current_path = os.getcwd()
        self.folder_path = os.path.join(current_path, "Patterns")
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

        self.file_path = None
        self.pattern_name = "Default"

        self.entry_width = 6

    def display_image(self, img: Image):
        img.show()

    def save_image(self, image: Image):
        if self.pattern_name:
            file_name = self.pattern_name
        else:
            file_name = "Canvas.png"
        file_name = os.path.join(self.folder_path, file_name)
        image.save(file_name)

    def display_fft_graph(self, mag_spectrum):
        lab_file = "/Users/matthewvansoelen/Desktop/Photonics-Lab/src/SLM/Patterns_and_Tools/Graph/DA001_50lpm_w0th_Data - DA001_50lpm_w0th_Data.csv"
        file_x = []
        file_y = []
        row_num = 0
        with open(lab_file, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            for row in spamreader:
                if row_num > 1:
                    file_x.append(float(row[0]))
                    file_y.append(float(row[1]))
                row_num += 1

            # pdb.set_trace()
        


        if self.raw_fft is None:
            print("Please run pattern first.")
        else:
            # pdb.set_trace()
            raw_data = np.fft.fftshift(self.raw_fft)
            raw_data = np.abs(raw_data)
            raw_data = np.power(raw_data, 2)
            height = np.unravel_index(np.argmax(raw_data), raw_data.shape)[0]
            
            y_range,x_range = raw_data.shape
            # x = range(0,x_range)
            x = np.linspace(0,x_range -1, x_range)
            x = x/ x[len(x)-1] * file_x[len(file_x)-1]

            with open("/Users/matthewvansoelen/Desktop/Photonics-Lab/src/SLM/Patterns_and_Tools/Graph/matt.csv", mode='w') as out_file:
                out_file = csv.writer(out_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)

                out_file.writerow(["LAB Distance (μm)", "LAB Intensity (cnts)","Matt Distance (μm)", "Matt Intensity (cnts)" ])
                for i in range(len(file_x)):
                    if i < len(x):
                        out_file.writerow([file_x[i], file_y[i], x[i], raw_data[height][i]])
                    else:
                        out_file.writerow([file_x[i], file_y[i]])

            plt.plot(x, raw_data[height], color="red")

            plt.show()


    def create_frames(self):
        self.l_frame = Frame(self.root)
        self.l_frame.grid(row = 0, column = 0)

        self.fill_left_frame()

        self.shape.trace("w", self.update_gui)

        self.r_frame = Frame(self.root)
        self.r_frame.grid(row = 0, column = 1)

        self.fill_right_frame()

        self.update_gui()

    def fill_left_frame(self):
        """
        Create various elements apart of the left GUI
        """

        self.source_options = {'Canvas','Upload'}
        self.pattern_source = StringVar(self.root)
        self.pattern_source.set('Canvas')
        OptionMenu(self.l_frame, self.pattern_source, *self.source_options).grid(row=0, column=0)

        scaling_method_frame = Frame(self.l_frame, borderwidth=2, relief=SUNKEN)
        scaling_method_frame.grid(row=1, column=0)

        self.scaling_method_state = IntVar(self.root)
        self.scaling_method_state.set(0)
        Radiobutton(scaling_method_frame, 
                    text='Linear scaling', 
                    variable=self.scaling_method_state,
                    value = 0).grid(row=0,column=0)
        Radiobutton(scaling_method_frame, 
                    text='Logarithmic scaling', 
                    variable=self.scaling_method_state,
                    value = 1).grid(row=1,column=0)

        self.upload_pattern_button = Button(self.l_frame, 
                                            text='Select a Pattern', 
                                            command=self.pattern_select)
        self.upload_pattern_button.grid(row=0, column=1)

        toggle_frame = Frame(self.l_frame)
        toggle_frame.grid(row=1, column=1)

        self.fft_shift_state = BooleanVar(self.root)
        self.fft_shift_state.set(True)
        Checkbutton(toggle_frame, 
                    text='Shift Fouier Tranform', 
                    variable=self.fft_shift_state).grid(row=0,column=0)

        self.zero_order_state = BooleanVar(self.root)
        self.zero_order_state.set(True)
        Checkbutton(toggle_frame, 
                    text='Zero Order', 
                    variable=self.zero_order_state).grid(row=1,column=0)

        i_fft_of_frame = Frame(self.l_frame, borderwidth=2, relief=SUNKEN)
        i_fft_of_frame.grid(row=2, column=0)
        Label(i_fft_of_frame, text="Inverse Fouier Tranform data source:").grid(row=0, column=0)

        self.i_fft_of_state = IntVar(self.root)
        self.i_fft_of_state.set(0)
        Radiobutton(i_fft_of_frame, 
                    text='Fouier Transform', 
                    variable=self.i_fft_of_state,
                    value = 0).grid(row=1,column=0)
        Radiobutton(i_fft_of_frame, 
                    text='Original Image', 
                    variable=self.i_fft_of_state,
                    value = 1).grid(row=2,column=0)

        
        blur_frame = Frame(self.l_frame, borderwidth=2, relief=SUNKEN)
        blur_frame.grid(row=3, column=0, rowspan=2, columnspan=2)
        self.blur_button = Button(blur_frame, 
                                    text="Apply blur",
                                    command=self.apply_blur)
        self.blur_button.grid(row=0,column=0)

        Label(blur_frame, text="Blur radius:").grid(row=1, column=0)
        self.guassain_num = IntVar()
        self.guassain_num_spinbox = Spinbox(blur_frame, textvariable=self.guassain_num, from_=0, to=100, width=self.entry_width)
        self.guassain_num_spinbox.grid(row=1, column=1)

        shape_options_frame = Frame(self.l_frame, borderwidth=2, relief=SUNKEN)
        shape_options_frame.grid(row=5, column=0, columnspan=2, rowspan=2)

        self.shape_options = {'Circle', 'Rectangle'}
        self.shape = StringVar(self.root)
        self.shape.set('Circle')
        OptionMenu(shape_options_frame, self.shape, *self.shape_options).grid(row=0, column=0)

        self.add_shape = Button(shape_options_frame,
                        text='Add',
                        command=self.add_shape)
        self.add_shape.grid(row=0, column=1)

        Label(shape_options_frame, text="Gray Value:").grid(row=1, column=0)
        self.gray_value_entry = Entry(shape_options_frame, width=self.entry_width)
        self.gray_value_entry.grid(row=1, column=1)

        self.coords_frame = Frame(shape_options_frame)
        self.coords_frame.grid(row=2, column=0) #, rowspan=1, columnspan=4)

        Label(self.coords_frame, text="X:").grid(row=0, column=0)
        self.x_entry = Entry(self.coords_frame, width=self.entry_width)
        self.x_entry.grid(row=0, column=1)

        Label(self.coords_frame, text="Y:").grid(row=0, column=2)
        self.y_entry = Entry(self.coords_frame, width=self.entry_width)
        self.y_entry.grid(row=0, column=3)

        self.dim_frame = Frame(shape_options_frame)
        self.dim_frame.grid(row=3, column=0)#, rowspan=1, columnspan=4)

        Label(self.dim_frame, text="Width:").grid(row=0, column=0)
        self.width_entry = Entry(self.dim_frame, width=self.entry_width)
        self.width_entry.grid(row=0, column=1)

        Label(self.dim_frame, text="Height:").grid(row=0, column=2)
        self.height_entry = Entry(self.dim_frame, width=self.entry_width)
        self.height_entry.grid(row=0, column=3)

        self.radius_frame = Frame(shape_options_frame)
        self.radius_frame.grid(row=4, column=0)#, columnspan=2)

        Label(self.radius_frame, text="Radius:").grid(row=0, column=0)
        self.radius_entry = Entry(self.radius_frame, width=self.entry_width)
        self.radius_entry.grid(row=0, column=1)

        self.reset_button = Button(self.l_frame,
                                    text='reset',
                                    command= self.reset_all)
        self.reset_button.grid(row=7, column=0)

        self.update_previews_button = Button(self.l_frame,
                                    text='update previews',
                                    command=lambda:self.update_previews(self.pattern_source.get()))
        self.update_previews_button.grid(row=7, column=1)

    def fill_right_frame(self):
        """
        Create various elements apart of the right GUI

        """
        # Frame on top of Original Image preview
        orig_header = Frame(self.r_frame)
        orig_header.grid(row=0, column=0)

        # Button which displays orginal image
        self.display_orig_button = Button(orig_header, 
                                            text='Original-Gray: Default', 
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

        # Frame on top of Fouier Trnasformed Image
        fft_header = Frame(self.r_frame)
        fft_header.grid(row=0, column=1)

        # Button which displays Fourier Tranformed image
        self.display_fft_button = Button(fft_header, 
                                            text='Fouier Tranform: Defualt', 
                                            command= lambda: self.display_image(self.fft_image))
        self.display_fft_button.grid(row=0, column=0)

        # Button which saves Fouier Tranformed image
        self.save_fft_button = Button(fft_header,
                                        text='Save',
                                        command= lambda: self.save_image(self.fft_image))
        self.save_fft_button.grid(row=0, column=1)

        # Label which holds Fouier Tranformed image thumbnail
        self.fft_image_label = Label(self.r_frame, image=self.tk_fft)
        self.fft_image_label.grid(row=1, column=1)

        # Button which displays Fouier Transformed as a 3D Graph
        self.display_fft_graph_button = Button(self.r_frame,
                                                text='Fouier Tranform Graph', 
                                                command= lambda: self.display_fft_graph(self.fft))
        self.display_fft_graph_button.grid(row=2, column=1)

        # Frame on top of Inverse Fouier Trnasformed Image
        i_fft_header = Frame(self.r_frame)
        i_fft_header.grid(row=0, column=2)

        # Button which displays Inverse Fourier Tranformed image
        self.display_i_fft_button = Button(i_fft_header, 
                                            text='Inverse Fouier Tranform: Defualt', 
                                            command= lambda: self.display_image(self.i_fft_image))
        self.display_i_fft_button.grid(row=0, column=0)

        # Button which saves Inverse Fouier Tranformed image
        self.save_i_fft_button = Button(i_fft_header,
                                        text='Save',
                                        command= lambda: self.save_image(self.i_fft_image))
        self.save_i_fft_button.grid(row=0, column=1)

        # Label which holds Inverse Fouier Tranformed image thumbnail
        self.i_fft_image_label = Label(self.r_frame, image=self.tk_i_fft)
        self.i_fft_image_label.grid(row=1, column=2)

    def pattern_select(self, file_path=None):
        
        if file_path is None:
            self.file_path = filedialog.askopenfilename(initialdir='Patterns', 
                                                        title="Select Image", 
                                                        filetypes=(("png images","*.png"),
                                                                ("jpeg images","*.jpeg"), 
                                                                ("All files","*.*")))
        else:
            self.file_path = file_path

        self.pattern_name = ntpath.basename(self.file_path)
        self.pattern_source.set('Upload')
        self.update_previews("Upload")


    def create_fft(self, scaling_method:int, shift:bool):
        self.raw_fft = np.fft.fft2(self.data)
        print(self.raw_fft)
        if shift:
            self.fft = np.fft.fftshift(self.raw_fft)
        else:
            self.fft = self.raw_fft

        self.fft = np.abs(self.fft)
        max_value = np.max(self.fft)
        # temp_index = np.unravel_index(np.argmax(self.fft), self.fft.shape)
        # temp_value = self.fft[temp_index]
        # self.fft[temp_index] = 0
        # max_value = np.max(self.fft)
        # if self.zero_order_state.get():
        #     self.fft[temp_index] = temp_value

        print(max_value, np.unravel_index(np.argmax(self.fft), self.fft.shape))
        if scaling_method == 0:
            if max_value <= 0:
                c = 0
            else:
                c = 255/(max_value)
            self.fft = c * self.fft

        elif scaling_method == 1:
            if max_value <= 0:
                c = 0
            else:
                c = 255/np.log(1 + max_value)
            self.fft = c * np.log(1+self.fft)
        else:
            print("Unknown scaling method")
        
        # self.fft = np.where(self.fft > 255, 255, self.fft)
        # print(type(self.fft))
        self.fft_image = Image.fromarray(self.fft)
        self.fft_image = self.fft_image.convert('L')
        self.thumbnail_fft = self.fft_image.copy()
        self.thumbnail_fft.thumbnail(self.thumbnail_size)
        self.tk_fft = ImageTk.PhotoImage(self.thumbnail_fft)

    def create_inverse_fft(self, data_source: int, shift: bool):
        if data_source == 0 and shift:
            i_fft = np.fft.ifftshift(self.raw_fft)
        elif data_source == 0 and not shift:
            i_fft = self.raw_fft
        if data_source == 1 and shift:
            i_fft = np.fft.ifftshift(self.data)
        elif data_source == 1 and not shift:
            i_fft = self.data

        
            # i_fft = np.fft.ifftshift(self.data)
        # i_fft = np.fft.ifftshift(self.raw_fft)
        i_fft = np.fft.ifft2(i_fft)
        self.i_fft = np.abs(i_fft)

        self.i_fft_image = Image.fromarray(self.i_fft)
        self.i_fft_image = self.i_fft_image.convert('L')
        self.thumbnail_i_fft = self.i_fft_image.copy()
        self.thumbnail_i_fft.thumbnail(self.thumbnail_size)
        self.tk_i_fft = ImageTk.PhotoImage(self.thumbnail_i_fft)

    def apply_blur(self):
        self.orig_image = self.orig_image.filter(ImageFilter.GaussianBlur(radius=int(self.guassain_num.get())))
        self.update_previews("Draw")

    def add_shape(self):
        print("add shape")
        x_pos = int(self.x_entry.get()) if int(self.x_entry.get()) else 0
        y_pos = int(self.y_entry.get()) if int(self.y_entry.get()) else 0

        gray_value = int(self.gray_value_entry.get()) if (int(self.gray_value_entry.get()) and int(self.gray_value_entry.get()) in range(0,256)) else 100
        if self.shape.get() == "Circle":
            radius = int(self.radius_entry.get()) if int(self.radius_entry.get()) else 10
            bounding_box = (x_pos-radius,y_pos-radius, x_pos+radius, y_pos+radius)
            drawing = ImageDraw.Draw(self.orig_image, 'L')
            drawing.ellipse(bounding_box, fill = gray_value)

        elif self.shape.get() == "Rectangle":
            width = int(self.width_entry.get()) if int(self.width_entry.get()) else 10
            height = int(self.height_entry.get()) if int(self.height_entry.get()) else 10
            bounding_box = (x_pos, y_pos, x_pos+width, y_pos+height)
            drawing = ImageDraw.Draw(self.orig_image, 'L')
            drawing.rectangle(bounding_box, fill = gray_value)


        self.update_previews("Draw")

    def update_gui(self, *args):
        print("body")
        if self.shape.get() == "Circle":
            self.radius_frame.grid(row=4, column=0, columnspan=2)
            self.dim_frame.grid_forget()
        elif self.shape.get() == "Rectangle":
            self.radius_frame.grid_forget()
            self.dim_frame.grid(row=3, column=0, rowspan=1, columnspan=4)


    def update_previews(self, reason:str):
        # update_previews the labels and data 
    
        if reason == "Upload":
            # try:
            self.orig_image = Image.open(self.file_path).convert('L')
            self.data = np.asarray(self.orig_image, dtype=np.uint16)
            self.height, self.width = self.data.shape

            self.thumbnail_image = self.orig_image.copy()
            self.thumbnail_image.thumbnail(self.thumbnail_size)
            self.tk_image = ImageTk.PhotoImage(self.thumbnail_image)

            self.display_orig_button.config(text="Original-Gray: %s"%(self.pattern_name))
            self.create_fft(self.scaling_method_state.get(), self.fft_shift_state.get())
            self.display_fft_button.config(text="Fouier Tranform: %s"%(self.pattern_name))

            self.create_inverse_fft(self.i_fft_of_state.get(), self.fft_shift_state.get())
            self.display_i_fft_button.config(text="Inverse Fouier Tranform: %s"%(self.pattern_name))

            # except Exception:
            #     print("Error: \' %s \' can not be opened"%(self.file_path))
            
        elif reason == "Canvas":
            self.orig_image = Image.fromarray(self.data).convert('L')
            self.thumbnail_image = self.orig_image.copy()
            self.thumbnail_image.thumbnail(self.thumbnail_size)
            self.tk_image = ImageTk.PhotoImage(self.thumbnail_image)

            self.display_orig_button.config(text="Original-Gray: Canvas")
            self.create_fft(self.scaling_method_state.get(),self.fft_shift_state.get())
            self.display_fft_button.config(text="Fouier Tranform: Canvas")
            self.create_inverse_fft(self.i_fft_of_state.get(), self.fft_shift_state.get())
            self.display_i_fft_button.config(text="Inverse  Fouier Tranform: Canvas")

        elif reason == "Draw":
            print("Draw")
            self.data = np.asarray(self.orig_image, dtype=np.uint16)
            self.thumbnail_image = self.orig_image.copy()
            self.thumbnail_image.thumbnail(self.thumbnail_size)
            self.tk_image = ImageTk.PhotoImage(self.thumbnail_image)

            self.display_orig_button.config(text="Original-Gray: Canvas")
            self.create_fft(self.scaling_method_state.get(),self.fft_shift_state.get())
            self.display_fft_button.config(text="Fouier Tranform: Canvas")
            self.create_inverse_fft(self.i_fft_of_state.get(), self.fft_shift_state.get())
            self.display_i_fft_button.config(text="Inverse Fouier Tranform: Canvas")

        elif reason == "Reset":
            self.guassain_num.set(0)
            self.pattern_source.set("Canvas")
            self.fft_shift_state.set(True)
            self.display_orig_button.config(text="Original-Gray: Default")
            self.create_fft(self.scaling_method_state.get(),self.fft_shift_state.get())
            self.display_fft_button.config(text="Fouier Tranform: Default")
            self.create_inverse_fft(self.i_fft_of_state.get(), self.fft_shift_state.get())
            self.display_i_fft_button.config(text="Inverse Fouier Tranform: Default")

        self.orig_image_label.config(image=self.tk_image)
        self.fft_image_label.config(image=self.tk_fft)
        self.i_fft_image_label.config(image=self.tk_i_fft)

    def reset_all(self):
        self.create_defaults()
        self.update_previews("Reset")

root = Tk()
gui = SimGUI(root)
root.mainloop()