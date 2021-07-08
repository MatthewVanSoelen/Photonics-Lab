"""
pattern_creator.py : Matthew Van Soelen
Description : Creates a GUI which handles the creation of DOE patterns
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
        print("toggled", self.show.get())
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


class Pattern_GUI:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title('Pattern Creator')
        self.root.minsize(500,500)
        self.thumbnail_size = (450,450)

        self.create_defaults()
        self.create_frames()

    def create_defaults(self):
        """ 
        Initialized variables with default values
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
        self.method_arr = ['Old','Meshgrid']
        self.method_options = set(self.method_arr)
        self.method = StringVar(self.root)
        self.method.set(self.method_arr[1])
        OptionMenu(self.method_frame, self.method, *self.method_options).grid(row=0, column=1)

        # Upload Frame ----------------------------------------------------------------------
        upload_setting_frame = Toggled_Frame(self.l_frame, text="Upload Settings",relief="raised", borderwidth=1)
        upload_setting_frame.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")

        self.upload_pattern_button = Button(upload_setting_frame.sub_frame, 
                                            text='Select a Pattern', command=self.pattern_select, bg=self.button_color, highlightbackground=self.button_color)
        self.upload_pattern_button.grid(row=0, column=0)

        self.upload_color_state = IntVar()
        Radiobutton(upload_setting_frame.sub_frame, text="Only B&W", variable=self.upload_color_state, value=0, command=self.upload_color_select).grid(row=1, column=0)
        Radiobutton(upload_setting_frame.sub_frame, text="Grayscale", variable=self.upload_color_state, value=1, command=self.upload_color_select).grid(row=2, column=0)
        # Uplaod Frame --> grayscale frame --------------------------------------------------
        self.grayscale_frame = Frame(upload_setting_frame.sub_frame, relief="sunken", borderwidth=1)
        Label(self.grayscale_frame,text="Grayscale Range").grid(row=0, column=0, columnspan=2)
        Label(self.grayscale_frame, text="Min:").grid(row=1, column=0)
        self.gray_min_entry = Entry(self.grayscale_frame, width=self.entry_box_width)
        self.gray_min_entry.grid(row=1, column=1)
        Label(self.grayscale_frame, text="Max:").grid(row=2, column=0)
        self.gray_max_entry = Entry(self.grayscale_frame, width=self.entry_box_width)
        self.gray_max_entry.grid(row=2, column=1)

        # Dimension Frame ----------------------------------------------------------------------
        dimension_frame = Toggled_Frame(self.l_frame, text="Dimensions",relief="raised", borderwidth=1)
        dimension_frame.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")

        self.square_pattern = BooleanVar(dimension_frame.sub_frame)
        self.square_pattern.set(True)
        
        square_check = Checkbutton(dimension_frame.sub_frame,
                    text='Square Pattern',
                    variable=self.square_pattern)
        square_check.grid(row=0, column=0, columnspan=2)
        self.create_tool_tip(widget= square_check, 
            text="When pattern is square the dimensions will be [Width, Width].")

        Label(dimension_frame.sub_frame, text="Width:").grid(row=1, column=0)
        self.width_entry = Entry(dimension_frame.sub_frame, width=self.entry_box_width)
        self.width_entry.grid(row=1, column=1)

        Label(dimension_frame.sub_frame, text="Height:").grid(row=2, column=0)
        self.height_entry = Entry(dimension_frame.sub_frame, width=self.entry_box_width)
        self.height_entry.grid(row=2, column=1)


        # Custom Patterns Frame ----------------------------------------------------------------------
        pattern_frame = Toggled_Frame(self.l_frame, text="Custom Patterns", relief="raised", borderwidth=1)
        pattern_frame.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")

        select_frame = Frame(pattern_frame.sub_frame)
        select_frame.pack(side="top", fill="both", expand=True)
        Label(select_frame,text="Pattern Type:").grid(row=0, column=0)
        self.types = ['Single Freq','Single Point [x,y]', 'Hor. Line', 'Ver. Line', 'Diagonal Line', 'Upload']
        self.type_options = set(self.types)
        self.p_type = StringVar(self.root)
        self.p_type.set('Single Freq')
        OptionMenu(select_frame, self.p_type, *self.type_options).grid(row=0, column=1)

        self.freq_frame = Frame(pattern_frame.sub_frame)

        Label(self.freq_frame, text="Freq:", width=self.label_box_width).grid(row=0, column=0)
        self.freq_entry = Entry(self.freq_frame, width=self.entry_box_width)
        self.freq_entry.grid(row=0, column=1)

        self.angle_frame = Frame(pattern_frame.sub_frame)

        Label(self.angle_frame, text="Angle:", width=self.label_box_width).grid(row=0, column=0)
        self.angle_entry = Entry(self.angle_frame, width=self.entry_box_width)
        self.angle_entry.grid(row=0, column=1)

        self.coords_frame = Frame(pattern_frame.sub_frame)

        Label(self.coords_frame, text="x:", width=self.label_box_width).grid(row=0, column=0)
        self.x_entry = Entry(self.coords_frame, width=self.entry_box_width)
        self.x_entry.grid(row=0, column=1)

        Label(self.coords_frame, text="y:", width=self.label_box_width).grid(row=1, column=0)
        self.y_entry = Entry(self.coords_frame, width=self.entry_box_width)
        self.y_entry.grid(row=1, column=1)        

        self.line_dim_frame = Frame(pattern_frame.sub_frame)

        Label(self.line_dim_frame, text="Line Length:", width=self.label_box_width).grid(row=0, column=0)
        self.line_len_entry = Entry(self.line_dim_frame, width=self.entry_box_width)
        self.line_len_entry.grid(row=0, column=1)

        self.upload_text_frame = Frame(pattern_frame.sub_frame)
        Label(self.upload_text_frame, text="Images can be uploaded \nusing the Upload Settings Section.").grid(row=0, column=0)

        self.p_type.trace("w", self.update_pattern_entries)
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

        Label(extra_frame.sub_frame, text="Margin(px):", width=self.label_box_width).grid(row=1, column=0)
        self.margin_size_entry = Entry(extra_frame.sub_frame, width=self.entry_box_width)
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
        t3 = Toggled_Frame(self.r_frame, text="Right Side", relief="raised", borderwidth=1)
        t3.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")

        self.label3 = Label(t3.sub_frame, text="yo! 3")
        self.label3.pack(side="left")

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

    def upload_color_select(self):
        if int(self.upload_color_state.get()) == 0:
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


        p_type = self.p_type.get()

        if p_type == self.types[0]: # Single Frequency
            self.freq_frame.pack(side="top", fill="both", expand=True)
            self.angle_frame.pack(side="top", fill="both", expand=True)
        elif p_type == self.types[1]: # Single Point [x,y]
            self.coords_frame.pack(side="top", fill="both", expand=True)
        elif p_type == self.types[2]: # Horizontal Line
            self.coords_frame.pack(side="top", fill="both", expand=True)
            self.line_dim_frame.pack(side="top", fill="both", expand=True)
        elif p_type == self.types[3]: # Vertical Line
            self.coords_frame.pack(side="top", fill="both", expand=True)
            self.line_dim_frame.pack(side="top", fill="both", expand=True)
        elif p_type == self.types[4]: # Diagnol Line
            self.angle_frame.pack(side="top", fill="both", expand=True)
            self.coords_frame.pack(side="top", fill="both", expand=True)
            self.line_dim_frame.pack(side="top", fill="both", expand=True)
        elif p_type == self.types[5]: # Upload
            self.upload_text_frame.pack(side="top", fill="both", expand=True)

    def create_tool_tip(self, widget, text):
        """
        Creates tool tip information hover over parameter
        """

        tool_tip = ToolTip(widget)
        def enter(event):
            tool_tip.showtip(text)
            print("Show tooltip")
        def leave(event):
            tool_tip.hidetip()
            print("Hide tooltip")
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def run_sawtooth(self):
        print("Sawtooth: This method should be apart of a separate class")

    def process(self):
        print("Process: This method should be apart of a separate class")

# class Pattern_data:
#   def _init__():


root = Tk()
gui = Pattern_GUI(root=root)
root.mainloop()