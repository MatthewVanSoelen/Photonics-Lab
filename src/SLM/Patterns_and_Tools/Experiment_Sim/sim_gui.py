from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from matplotlib.image import imread
from matplotlib import cm


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
        print("Displays fft graph")
        fig = plt.figure()
        ax = fig.gca(projection='3d')

        x = np.arange(0, self.width, 1)
        y = np.arange(0, self.height, 1)
        X, Y = np.meshgrid(x, y)
        Z = mag_spectrum


        surface = ax.plot_surface(X, Y, Z, cmap=cm.cividis)
        fig.colorbar(surface, shrink=0.5, aspect=5)
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

        

        self.upload_pattern_button = Button(self.l_frame, 
                                            text='Select a Pattern', 
                                            command=self.pattern_select)
        self.upload_pattern_button.grid(row=1, column=0)

        self.fft_shift_state = BooleanVar(self.root)
        self.fft_shift_state.set(True)
        Checkbutton(self.l_frame, 
                    text='Shift Fouier Tranform', 
                    variable=self.fft_shift_state).grid(row=1,column=1)

        
        blur_frame = Frame(self.l_frame, borderwidth=2, relief=SUNKEN)
        blur_frame.grid(row=2, column=0, rowspan=2, columnspan=2)
        self.blur_button = Button(blur_frame, 
                                    text="Apply blur",
                                    command=self.apply_blur)
        self.blur_button.grid(row=0,column=0)

        Label(blur_frame, text="Blur radius:").grid(row=1, column=0)
        self.guassain_num = IntVar()
        self.guassain_num_spinbox = Spinbox(blur_frame, textvariable=self.guassain_num, from_=0, to=100, width=self.entry_width)
        self.guassain_num_spinbox.grid(row=1, column=1)

        shape_options_frame = Frame(self.l_frame, borderwidth=2, relief=SUNKEN)
        shape_options_frame.grid(row=4, column=0, columnspan=2, rowspan=2)

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
        self.coords_frame.grid(row=2, column=0, rowspan=1, columnspan=4)

        Label(self.coords_frame, text="X:").grid(row=0, column=0)
        self.x_entry = Entry(self.coords_frame, width=self.entry_width)
        self.x_entry.grid(row=0, column=1)

        Label(self.coords_frame, text="Y:").grid(row=0, column=2)
        self.y_entry = Entry(self.coords_frame, width=self.entry_width)
        self.y_entry.grid(row=0, column=3)

        self.dim_frame = Frame(shape_options_frame)
        self.dim_frame.grid(row=3, column=0, rowspan=1, columnspan=4)

        Label(self.dim_frame, text="Width:").grid(row=0, column=0)
        self.width_entry = Entry(self.dim_frame, width=self.entry_width)
        self.width_entry.grid(row=0, column=1)

        Label(self.dim_frame, text="Height:").grid(row=0, column=2)
        self.height_entry = Entry(self.dim_frame, width=self.entry_width)
        self.height_entry.grid(row=0, column=3)

        self.radius_frame = Frame(shape_options_frame)
        self.radius_frame.grid(row=4, column=0, columnspan=2)

        Label(self.radius_frame, text="Radius:").grid(row=0, column=0)
        self.radius_entry = Entry(self.radius_frame, width=self.entry_width)
        self.radius_entry.grid(row=0, column=1)

        self.reset_button = Button(self.l_frame,
                                    text='reset',
                                    command= self.reset_all)
        self.reset_button.grid(row=6, column=0)

        self.update_previews_button = Button(self.l_frame,
                                    text='update previews',
                                    command=lambda:self.update_previews("Draw"))
        self.update_previews_button.grid(row=6, column=1)

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
        fft_header.grid(row=2, column=0)

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
        self.fft_image_label.grid(row=3, column=0)

        # Button which displays Fouier Transformed as a 3D Graph
        self.display_fft_graph_button = Button(self.r_frame, 
                                                text='Fouier Tranform Graph', 
                                                command= lambda: self.display_fft_graph(self.fft))
        self.display_fft_graph_button.grid(row=4, column=0)

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


    def create_fft(self, shift:bool ):
        fft = np.fft.fft2(self.data)

        if shift:
            fft = np.fft.fftshift(fft)
        
        self.fft = np.abs(fft)

        max_value = np.max(self.fft)
        if max_value <= 0:
            c = 0
        else:
            c = 255/(1 + max_value)

        self.fft = c * self.fft
        print(type(self.fft))
        self.fft_image = Image.fromarray(self.fft)
        self.fft_image = self.fft_image.convert('L')
        self.thumbnail_fft = self.fft_image.copy()
        self.thumbnail_fft.thumbnail(self.thumbnail_size)
        self.tk_fft = ImageTk.PhotoImage(self.thumbnail_fft)


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
            try:
                self.orig_image = Image.open(self.file_path).convert('L')
                self.data = np.asarray(self.orig_image, dtype=np.uint16)
                self.height, self.width = self.data.shape

                self.thumbnail_image = self.orig_image.copy()
                self.thumbnail_image.thumbnail(self.thumbnail_size)
                self.tk_image = ImageTk.PhotoImage(self.thumbnail_image)

                self.display_orig_button.config(text="Original-Gray: %s"%(self.pattern_name))
                self.create_fft(self.fft_shift_state.get())
                self.display_fft_button.config(text="Fouier Tranform: %s"%(self.pattern_name))

            except Exception:
                print("Error: \' %s \' can not be opened"%(self.file_path))
            
        elif reason == "Canvas":
            self.orig_image = Image.fromarray(self.data).convert('L')
            self.thumbnail_image = self.orig_image.copy()
            self.thumbnail_image.thumbnail(self.thumbnail_size)
            self.tk_image = ImageTk.PhotoImage(self.thumbnail_image)

            self.display_orig_button.config(text="Original-Gray: Canvas")
            self.create_fft(self.fft_shift_state.get())
            self.display_fft_button.config(text="Fouier Tranform: Canvas")

        elif reason == "Draw":
            print("Draw")
            self.data = np.asarray(self.orig_image, dtype=np.uint16)
            self.thumbnail_image = self.orig_image.copy()
            self.thumbnail_image.thumbnail(self.thumbnail_size)
            self.tk_image = ImageTk.PhotoImage(self.thumbnail_image)

            self.display_orig_button.config(text="Original-Gray: Canvas")
            self.create_fft(self.fft_shift_state.get())
            self.display_fft_button.config(text="Fouier Tranform: Canvas")

        elif reason == "Reset":
            self.guassain_num.set(0)
            self.pattern_source.set("Canvas")
            self.fft_shift_state.set(True)
            self.display_orig_button.config(text="Original-Gray: Default")
            self.create_fft(self.fft_shift_state.get())
            self.display_fft_button.config(text="Fouier Tranform: Default")

        self.orig_image_label.config(image=self.tk_image)
        self.fft_image_label.config(image=self.tk_fft)

    def reset_all(self):
        self.create_defaults()
        self.update_previews("Reset")

root = Tk()
gui = SimGUI(root)
root.mainloop()

