from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from matplotlib.image import imread
from matplotlib import cm

from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk, ImageFilter
import numpy as np 

import os
import ntpath

class SimGUI:
    def __init__(self, root: Tk):

        self.root = root
        self.root.title('Surface Grating Simulation')
        self.root.minsize(1000,500)
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

    def display_image(self, img: Image):
        img.show()

    def save_image(self, image: Image):
        if self.file_name:
            file_name = self.file_name
        else:
            file_name = "Blank.png"
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

        self.r_frame = Frame(self.root)
        self.r_frame.grid(row = 0, column = 1)

        self.fill_right_frame()

    def fill_left_frame(self):

        self.source_options = {'Blank','Upload'}
        self.pattern_source = StringVar(self.root)
        self.pattern_source.set('Blank')
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

        self.guassian_state = BooleanVar(self.root)
        self.guassian_state.set(False)
        
        blur_frame = Frame(self.l_frame, borderwidth=2, relief=SUNKEN)
        blur_frame.grid(row=1, column=1, columnspan=2)
        Checkbutton(blur_frame, 
                    text='Apply Gussain Blur', 
                    variable=self.guassian_state).grid(row=0,column=0)
        self.guassain_num = Spinbox(blur_frame, from_=0, to=100)
        self.guassain_num.grid(row=1, column=0)

        self.update_button = Button(self.l_frame,
                                    text='Update',
                                    command=self.update)
        self.update_button.grid(row=0, column=1)

    def fill_right_frame(self):
        orig_header = Frame(self.r_frame)
        orig_header.grid(row=0, column=0)
        self.display_orig_button = Button(orig_header, 
                                            text='Original-Gray: Default', 
                                            command= lambda: self.display_image(self.orig_image))
        self.display_orig_button.grid(row=0, column=0)

        self.save_orig_button = Button(orig_header,
                                        text='Save',
                                        command= lambda: self.save_image(self.orig_image))
        self.save_orig_button.grid(row=0, column=1)

        self.orig_image_label = Label(self.r_frame, image=self.tk_image)
        self.orig_image_label.grid(row=1, column=0)

        fft_header = Frame(self.r_frame)
        fft_header.grid(row=2, column=0)
        self.display_fft_button = Button(fft_header, 
                                            text='Fouier Tranform: Defualt', 
                                            command= lambda: self.display_image(self.fft_image))
        self.display_fft_button.grid(row=0, column=0)

        self.save_fft_button = Button(fft_header,
                                        text='Save',
                                        command= lambda: self.save_image(self.fft_image))
        self.save_fft_button.grid(row=0, column=1)

        self.fft_image_label = Label(self.r_frame, image=self.tk_fft)
        self.fft_image_label.grid(row=3, column=0)

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


    def create_fft(self, shift:bool ):
        fft = np.fft.fft2(self.data)

        if shift:
            fft = np.fft.fftshift(fft)

        self.fft = np.abs(fft)
        max_value = np.max(self.fft)
        if max_value <= 0:
            c = 0
        else:
            c = 255/(1 + np.log(max_value))

        self.fft = c * np.log(1 + self.fft)

        self.fft_image = Image.fromarray(self.fft)
        self.fft_image = self.fft_image.convert('L')
        self.thumbnail_fft = self.fft_image.copy()
        self.thumbnail_fft.thumbnail(self.thumbnail_size)
        self.tk_fft = ImageTk.PhotoImage(self.thumbnail_fft)

    def update(self):
        # update the labels and data 
        if self.pattern_source.get() == 'Upload':
            # try:
            self.orig_image = Image.open(self.file_path).convert('L')
            if self.guassian_state.get():
                self.orig_image = self.orig_image.filter(ImageFilter.GaussianBlur(radius=int(self.guassain_num.get())))
            self.data = np.asarray(self.orig_image, dtype=np.uint16)
            self.height, self.width = self.data.shape

            self.thumbnail_image = self.orig_image.copy()
            self.thumbnail_image.thumbnail(self.thumbnail_size)
            self.tk_image = ImageTk.PhotoImage(self.thumbnail_image)

            self.display_orig_button.config(text="Original-Gray: %s"%(self.pattern_name))
            self.create_fft(self.fft_shift_state.get())
            self.display_fft_button.config(text="Fouier Tranform: %s"%(self.pattern_name))

            # except Exception:
            #     print("Error: \' %s \' can not be opened"%(self.file_path))
            
        else:
            self.orig_image = Image.fromarray(self.data).convert('L')
            if self.guassian_state.get():
                self.orig_image = git self.orig_image.filter(ImageFilter.GaussianBlur(radius=int(self.guassain_num.get())))
            self.thumbnail_image = self.orig_image.copy()
            self.thumbnail_image.thumbnail(self.thumbnail_size)
            self.tk_image = ImageTk.PhotoImage(self.thumbnail_image)

            self.display_orig_button.config(text="Original-Gray: Blank")
            self.create_fft(self.fft_shift_state.get())
            self.display_fft_button.config(text="Fouier Tranform: Blank")

        self.orig_image_label.config(image=self.tk_image)
        self.fft_image_label.config(image=self.tk_fft)


root = Tk()
gui = SimGUI(root)
root.mainloop()

