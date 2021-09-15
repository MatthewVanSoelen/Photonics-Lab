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

class Pattern_Data:
    def __init__(self, root: Tk):
        self.root = root
        self.width = 1920
        self.height = self.width
        self.pattern_list = np.array([])
        self.thumbnail_size = (450,450)
        
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

        self.method_arr = ['Old','Meshgrid']
        self.method_options = set(self.method_arr)
        self.method = StringVar(self.root)
        self.method.set(self.method_arr[1])
        print(self.method)

    def get_method(self):
        return self.method

    def set_method(self, option):
        self.method = option
        return True