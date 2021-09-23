"""
pattern_creator.py : Matthew Van Soelen
Description : Creates a GUI which handles the creation of DOE patterns
"""

# Import  custom helper classes for views and data controll
from pattern_helper import Toggled_Frame, ToolTip, Pattern_Data

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

class Pattern_GUI:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title('Pattern Creator')
        self.root.minsize(700,500)
        self.thumbnail_size = (450,450)

        self.p_data = Pattern_Data(self.root)

        self.create_defaults()
        self.create_frames()

    def create_defaults(self):
        """ 
        Initialized GUI variables with default values
        """

        self.entry_colors = ['black', 'light cyan']
        self.bold_font = font.Font(weight="bold")
        self.button_color = "gainsboro"
        
    def create_frames(self):
        self.l_frame = Frame(self.root)
        self.l_frame.pack(side="left", anchor=NW)

        self.fill_left_frame()

        self.r_frame = Frame(self.root)
        self.r_frame.pack(side="left", anchor=NW)

        self.fill_right_frame()

    def fill_left_frame(self):

        # Method Frame ----------------------------------------------------------------------
        self.method_frame = Frame(self.l_frame, borderwidth=2, relief=SUNKEN)
        self.method_frame.pack(side="top", fill="both", expand=True)

        method_label = Label(self.method_frame,text="Method:")
        method_label.grid(row=0, column=0)
        self.create_tool_tip(widget=method_label, 
                                text="The method used to produce patterns.\nBoth methods are similar but\nmeshgrid should be slightly more accurate.")
        
        OptionMenu(self.method_frame, self.p_data.get_method(), *self.p_data.method_options).grid(row=0, column=1)

        # Upload Frame ----------------------------------------------------------------------
        upload_setting_frame = Toggled_Frame(self.l_frame, text="Upload Settings",relief="raised", borderwidth=1)
        upload_setting_frame.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")

        self.upload_pattern_button = Button(upload_setting_frame.sub_frame, 
                                            text='Select a Pattern', command=self.pattern_select, bg=self.button_color, highlightbackground=self.button_color)
        self.upload_pattern_button.grid(row=0, column=0)

        Radiobutton(upload_setting_frame.sub_frame, text="Only B&W", variable=self.p_data.upload_color_state, value=0, command=self.upload_color_select).grid(row=1, column=0)
        Radiobutton(upload_setting_frame.sub_frame, text="Grayscale", variable=self.p_data.upload_color_state, value=1, command=self.upload_color_select).grid(row=2, column=0)
        
        # Uplaod Frame --> grayscale frame --------------------------------------------------
        self.grayscale_frame = Frame(upload_setting_frame.sub_frame, relief="sunken", borderwidth=1)
        Label(self.grayscale_frame,text="Grayscale Range").grid(row=0, column=0, columnspan=2)
        Label(self.grayscale_frame, text="Min:").grid(row=1, column=0)
        self.gray_min_entry = Entry(self.grayscale_frame, width=self.p_data.entry_box_width)
        self.gray_min_entry.grid(row=1, column=1)
        Label(self.grayscale_frame, text="Max:").grid(row=2, column=0)
        self.gray_max_entry = Entry(self.grayscale_frame, width=self.p_data.entry_box_width)
        self.gray_max_entry.grid(row=2, column=1)

        # Dimension Frame ----------------------------------------------------------------------
        dimension_frame = Toggled_Frame(self.l_frame, text="Dimensions",relief="raised", borderwidth=1)
        dimension_frame.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")

        
        square_check = Checkbutton(dimension_frame.sub_frame,
                    text='Square Pattern',
                    variable=self.p_data.square_pattern)
        square_check.grid(row=0, column=0, columnspan=2)
        self.create_tool_tip(widget= square_check, 
            text="When pattern is square the dimensions will be [Width, Width].")

        Label(dimension_frame.sub_frame, text="Width:").grid(row=1, column=0)
        self.p_data.width_entry = Entry(dimension_frame.sub_frame, width=self.p_data.entry_box_width)
        self.p_data.width_entry.grid(row=1, column=1)

        Label(dimension_frame.sub_frame, text="Height:").grid(row=2, column=0)
        self.p_data.height_entry = Entry(dimension_frame.sub_frame, width=self.p_data.entry_box_width)
        self.p_data.height_entry.grid(row=2, column=1)


        # Custom Patterns Frame ----------------------------------------------------------------------
        pattern_frame = Toggled_Frame(self.l_frame, text="Custom Patterns", relief="raised", borderwidth=1)
        pattern_frame.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")

        select_frame = Frame(pattern_frame.sub_frame)
        select_frame.pack(side="top", fill="both", expand=True)
        Label(select_frame,text="Pattern Type:").grid(row=0, column=0)
   
        OptionMenu(select_frame, self.p_data.p_type, *self.p_data.type_options).grid(row=0, column=1)

        self.freq_frame = Frame(pattern_frame.sub_frame)

        Label(self.freq_frame, text="Freq:", width=self.p_data.label_box_width).grid(row=0, column=0)
        self.freq_entry = Entry(self.freq_frame, width=self.p_data.entry_box_width)
        self.freq_entry.grid(row=0, column=1)

        self.angle_frame = Frame(pattern_frame.sub_frame)

        Label(self.angle_frame, text="Angle:", width=self.p_data.label_box_width).grid(row=0, column=0)
        self.angle_entry = Entry(self.angle_frame, width=self.p_data.entry_box_width)
        self.angle_entry.grid(row=0, column=1)

        self.coords_frame = Frame(pattern_frame.sub_frame)

        Label(self.coords_frame, text="x:", width=self.p_data.label_box_width).grid(row=0, column=0)
        self.x_entry = Entry(self.coords_frame, width=self.p_data.entry_box_width)
        self.x_entry.grid(row=0, column=1)

        Label(self.coords_frame, text="y:", width=self.p_data.label_box_width).grid(row=1, column=0)
        self.y_entry = Entry(self.coords_frame, width=self.p_data.entry_box_width)
        self.y_entry.grid(row=1, column=1)        

        self.line_dim_frame = Frame(pattern_frame.sub_frame)

        Label(self.line_dim_frame, text="Line Length:", width=self.p_data.label_box_width).grid(row=0, column=0)
        self.line_len_entry = Entry(self.line_dim_frame, width=self.p_data.entry_box_width)
        self.line_len_entry.grid(row=0, column=1)

        self.upload_text_frame = Frame(pattern_frame.sub_frame)
        Label(self.upload_text_frame, text="Images can be uploaded \nusing the Upload Settings Section.").grid(row=0, column=0)

        self.p_data.p_type.trace("w", self.update_pattern_entries)
        self.update_pattern_entries()

        # Extra Options Frame ----------------------------------------------------------------------
        extra_frame = Toggled_Frame(self.l_frame, text="Extra Options", relief="raised", borderwidth=1)
        extra_frame.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")

        self.margin_pattern = BooleanVar(self.root)
        self.margin_pattern.set(True)
        self.margin_pattern_checkbox = Checkbutton(extra_frame.sub_frame, 
                    text='Scale Pattern', 
                    variable=self.margin_pattern)
        self.margin_pattern_checkbox.grid(row=0,column=0)
        self.create_tool_tip(widget = self.margin_pattern_checkbox, 
            text = "Adds a black margin to the \nright and bottom of the pattern.\nThis improves the defintion of the patterns.")

        Label(extra_frame.sub_frame, text="Margin(px):", width=self.p_data.label_box_width).grid(row=1, column=0)
        self.margin_size_entry = Entry(extra_frame.sub_frame, width=self.p_data.entry_box_width)
        self.margin_size_entry.grid(row=1, column=1)
        self.margin_size_entry.insert(0, '2000')

        self.fft_shift_state = BooleanVar(self.root)
        self.fft_shift_state.set(True)
        fft_checkbox = Checkbutton(extra_frame.sub_frame, 
                    text='Shift Fouier Tranform', 
                    variable=self.fft_shift_state)
        fft_checkbox.grid(row=2,column=0)
        self.create_tool_tip(widget=fft_checkbox,
                    text="When checked the Fourier Tranform's origin[0,0]\nwill be shifted to the center of the image.")

        # Process Frame ----------------------------------------------------------------------
        process_frame = Toggled_Frame(self.l_frame, text="Process", state=False, bg="AntiqueWhite1", relief="raised", borderwidth=1)
        process_frame.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")

        self.process_button = Button(process_frame.sub_frame,
                                    text='Process',
                                    command= self.process)
        self.process_button.grid(row=0, column=0)

        self.progress_bar = Progressbar(process_frame.sub_frame, orient = HORIZONTAL , length = 200, mode='determinate')
        self.progress_bar.grid(row=1, column=0, columnspan=2)

        self.gen_saw_button = Button(process_frame.sub_frame,
                                    text='Generate Sawtooth',
                                    command= self.run_sawtooth)
        self.gen_saw_button.grid(row=0, column=1)

    def fill_right_frame(self):
        """
        Create various elements apart of the the right GUI
        For example displays for the patterns and buttons to open the image using the computer's native 
        """
        display_frame = Toggled_Frame(self.r_frame, text="Produced Image", relief="raised", borderwidth=1)
        display_frame.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")

        self.cur_image_label = Label(display_frame.sub_frame, image=self.p_data.tk_fft_image)
        self.cur_image_label.pack(side="left")

        image_select_frame = Toggled_Frame(self.r_frame, text="Image Select", relief="raised", borderwidth=1)
        image_select_frame.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")

        select_frame = Frame(image_select_frame.sub_frame)
        select_frame.pack(side="top", fill="both", expand=True)
        Label(select_frame,text="Pattern Type:").grid(row=0, column=0)
        self.images = ['Single Freq','Single Point [x,y]', 'Hor. Line', 'Ver. Line', 'Diagonal Line', 'Upload']
        self.image_options = set(self.p_data.types)
        self.cur_image = StringVar(self.root)
        self.cur_image.set('Single Freq')
        OptionMenu(select_frame, self.cur_image, *self.image_options).grid(row=0, column=1)

        self.cur_image.trace("w", self.display_image)
        self.display_image()

    def display_image(self, *args ):
        print(self.cur_image.get())

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

        self.p_data.p_type.set('Upload')
        self.upload_image = Image.open(self.file_path).convert('L')
        self.update_view()

    def update_view(self):
        """
        Updates the view with the appropriate preview images
        """
        if self.p_data.p_type.get() == self.p_data.types[5]: 
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
        self.p_data.tk_fft_image = ImageTk.PhotoImage(self.thumbnail_fft_image)

        self.display_fft_button.config(text="FFT: %s"%(self.pattern_name))
        self.fft_image_label.config(image=self.p_data.tk_fft_image)

    def upload_color_select(self):
        if int(self.p_data.upload_color_state.get()) == 0:
            self.grayscale_frame.grid_forget()
        else:
            self.grayscale_frame.grid(row=3, column=0)

    def update_pattern_entries(self, *args):
        """
        Updates the entry boxes presented in the Custom Patterns frame
        based on the current pattern type selection.
        """
        self.freq_frame.forget()
        self.angle_frame.forget()
        self.coords_frame.forget()
        self.line_dim_frame.forget()
        self.upload_text_frame.forget()


        p_type = self.p_data.p_type.get()

        if p_type == self.p_data.types[0]: # Single Frequency
            self.freq_frame.pack(side="top", fill="both", expand=True)
            self.angle_frame.pack(side="top", fill="both", expand=True)
        elif p_type == self.p_data.types[1]: # Single Point [x,y]
            self.coords_frame.pack(side="top", fill="both", expand=True)
        elif p_type == self.p_data.types[2]: # Horizontal Line
            self.coords_frame.pack(side="top", fill="both", expand=True)
            self.line_dim_frame.pack(side="top", fill="both", expand=True)
        elif p_type == self.p_data.types[3]: # Vertical Line
            self.coords_frame.pack(side="top", fill="both", expand=True)
            self.line_dim_frame.pack(side="top", fill="both", expand=True)
        elif p_type == self.p_data.types[4]: # Diagnol Line
            self.angle_frame.pack(side="top", fill="both", expand=True)
            self.coords_frame.pack(side="top", fill="both", expand=True)
            self.line_dim_frame.pack(side="top", fill="both", expand=True)
        elif p_type == self.p_data.types[5]: # Upload
            self.upload_text_frame.pack(side="top", fill="both", expand=True)

    def create_tool_tip(self, widget, text):
        """
        Creates tool tip information hover over parameter
        """

        tool_tip = ToolTip(widget)
        def enter(event):
            tool_tip.showtip(text)
        def leave(event):
            tool_tip.hidetip()
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def run_sawtooth(self):
        print("Sawtooth: This method should be apart of a separate class")

    def process(self):
        print("Process: This method should be apart of a separate class")


