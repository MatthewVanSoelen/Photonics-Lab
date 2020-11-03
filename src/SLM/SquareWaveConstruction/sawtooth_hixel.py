
import tkinter as tk
from tkinter import filedialog
from PIL import Image
from PIL import ImageTk
import ntpath
from datetime import datetime 
from datetime import timedelta 
import time
import threading
import numpy as np


class Sawtooth_Hixel():
    def __init__(self, root: tk.Tk, configs: dict):
        
        self.root = root
        self.window_configs = configs
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.item_list = []
        self.list_box = None

        window_title = (configs['Window Title'] if 'Window Title' 
            in configs else 'App')
        self.root.title(window_title)

        if 'Window Width' not in self.window_configs and 'Window Height' not in self.window_configs:
            return
        window_width = (self.window_configs['Window Width'] if 'Window Width' 
            in self.window_configs else 400)
        window_height = (self.window_configs['Window Height'] if 'Window Height' 
            in self.window_configs else 400)
        window_width = 800
        window_height = 500
        self.root.minsize(window_width, window_height)
        shift_x = self.window_configs['Shift x'] if 'Shift x' in self.window_configs else 0
        shift_y = self.window_configs['Shift y'] if 'Shift y' in self.window_configs else 0 
        #Place the root in center of screen then displace as needed.
        x = int((self.screen_width/2) - (window_width/2))
        y = int((self.screen_height/2) - (window_height/2))
        self.root.geometry("{}x{}+{}+{}".format(window_width, window_height, 
            x+shift_x, y+shift_y))


        self.create_base_frames()
        self.setup_grating_options(self.grating_options_frame)
        self.setup_list_view(self.grating_list_frame)
        # tk.Label(self.grating_options_frame, text = "Hello this is a test", bg = self.grating_options_frame_color[0]).pack()
        # test = tk.Button(self.grating_options_frame, text="Yo", command=self.test, bg = self.grating_options_frame_color[1])
        # test.pack()
        # print("After test")

    def test(self):
        print("Yo")

    def create_base_frames(self):
        # Setup window frames
        margin = 0.02
        frame_width  = 1 - 2 * margin
        frame_height = frame_width
        self.grating_options_frame_color = ['sea green', 'peach puff', 'navy', 'cyan']

        #Dimesions [relx, rely, relwidth, relheight]
        options_dim = [0.0 + margin, 0.0 + margin, .5 - 2 * margin, 0.5 - 2 * margin ]
        view_dim = [0.0 + margin, options_dim[3] + 2 * margin, .5 - 2 * margin, 0.5 - 3 * margin ]
        preview_dim = [options_dim[0] + options_dim[2] + margin, 0.0 + margin, .5 - 2 * margin, 0.5 - 2 * margin ]
        details_dim = [options_dim[0] + options_dim[2] + margin, options_dim[3] + 2 * margin, .5 - 2 * margin, 0.5 - 3 * margin ]
        print(options_dim)
        print(view_dim)
        print(preview_dim)
        print(details_dim)
        self.grating_options_frame = tk.Frame(self.root, bg = self.grating_options_frame_color[0], borderwidth = 2, relief = tk.SUNKEN)
        self.grating_options_frame.place(relx = options_dim[0], rely = options_dim[1], relwidth = options_dim[2], relheight = options_dim[3])

        self.grating_preview_frame = tk.Frame(self.root,  bg = self.grating_options_frame_color[1], borderwidth = 2, relief = tk.SUNKEN)
        self.grating_preview_frame.place(relx = preview_dim[0], rely = preview_dim[1], relwidth = preview_dim[2], relheight = preview_dim[3])

        self.grating_list_frame = tk.Frame(self.root,  bg = self.grating_options_frame_color[2], borderwidth = 2, relief = tk.SUNKEN)
        self.grating_list_frame.place(relx = view_dim[0], rely = view_dim[1], relwidth = view_dim[2], relheight = view_dim[3])

        self.item_details_frame = tk.Frame(self.root,  bg = self.grating_options_frame_color[3], borderwidth = 2, relief = tk.SUNKEN)
        self.item_details_frame.place(relx = details_dim[0], rely = details_dim[1], relwidth = details_dim[2], relheight = details_dim[3])


    def grating_select(self, file_path=None):
        """
        Select an image from a file dialogue box and update on screen.
        """
        
        if file_path is None:
            self.grating_file_path = filedialog.askopenfilename(initialdir='Images', 
                title="Select Image", filetypes=(("png images","*.png"),
                    ("jpeg images","*.jpeg"), ("All files","*.*")))
        else:
            self.grating_file_path = file_path
            
        self.grating_name = ntpath.basename(self.grating_file_path)
        self.type_var.set('Custom')

    def setup_grating_options(self, frame:tk.Frame):
        """
        Set up grating options entry widgets
        """
        frame.config(borderwidth=2, relief=tk.SUNKEN)

        tk.Label(frame, text='Rotation Angle', font='bold').grid(row=0, column=0)
        self.entry_angle = tk.Entry(frame, width = 15)
        self.entry_angle.grid(row=1, column=0)

        tk.Label(frame, text='Grating Type', font='bold').grid(row=0, column=1)
        self.types = {'SawTooth', 'Triangle', 'Circle', 'Custom'}
        self.type_var = tk.StringVar(frame)
        self.type_var.set('SawTooth')
        tk.OptionMenu(frame, self.type_var, *self.types).grid(row=1, column=1)

        tk.Label(frame, text='Ymin', font='bold').grid(row=2, column=0)
        self.entry_ymin = tk.Entry(frame, width = 15)
        self.entry_ymin.grid(row=3, column = 0)

        tk.Label(frame, text='Ymax', font='bold').grid(row=2, column=1)
        self.entry_ymax = tk.Entry(frame, width = 15)
        self.entry_ymax.grid(row=3, column = 1)

        tk.Label(frame, text='Period Width (pixels)', font='bold').grid(row=4, column=0)
        self.entry_period = tk.Entry(frame, width = 15)
        self.entry_period.grid(row=5, column = 0)

        self.g_reverse = tk.IntVar()
        tk.Checkbutton(frame, text = 'Reverse Grating', variable = self.g_reverse).grid(row=5, column=1)
        
        selection_frame = tk.Frame(frame, borderwidth=2, relief=tk.SOLID, pady=4)
        selection_frame.grid(row=6, column=0, columnspan=2)
        tk.Label(selection_frame, text='Grating Selection', font='bold').grid(row=0, column=0)
        self.button_image = tk.Button(selection_frame, text='Select a Grating', 
            command=self.grating_select)
        self.button_image.grid(row=0, column=1)
    # def collect_raw_data(self):

    def onselect(self, event):
        index = self.list_box.curselection()
        if not len(index) == 0:
            w = event.widget
            index = index[0]
            self.item = self.item_list[index]
            
            print("Selected item: index")
            # self.fill_item_deatils(self.item)
    

    # def add_item(self):
    #     if len(self.item_list) < 4:
    #         self.collect_raw_data()
    #         self.modify_and_map()
    #         self.item_details.update({
    #             'map_timing': self.map_timing,
    #             'map_laser_power': self.map_laser_power
    #             })
    #         self.grating = MyGrating(self.grating_configs)
    #         item = ListItem(self.image, self.grating, self.item_details)
    #         self.item_list.append(item)
    #         self.update_list()
            
    # def remove_item(self):
    
    #     index = self.list_box.curselection()
        
    #     if not len(index) == 0:
    #         index = index[0]
        
    #         self.list_box.delete(index)
    #         del self.item_list[index]

    # def clear_items(self):
    #     self.list_box.delete(0, tk.END)
    #     self.item_list.clear()

    def setup_list_view(self, frame:tk.Frame):
        
        self.list_box = tk.Listbox(frame, width=40)
        self.list_box.grid(row = 0, column= 0, columnspan=3)
        
        # self.add_button = tk.Button(frame, text = 'Add', command = self.add_item)
        # self.add_button.grid(row = 1, column = 0)

        # self.add_button = tk.Button(frame, text = 'Remove', command = self.remove_item)
        # self.add_button.grid(row = 1, column = 1)
        
        # self.clear_list_button = tk.Button(frame, text = 'Clear List', command = self.clear_items)
        # self.clear_list_button.grid(row = 1, column = 2)

        self.list_select = self.list_box.bind('<<ListboxSelect>>', lambda event: self.onselect(event))

        def update_list(self):
            self.list_box.delete(0, tk.END)
            for item in self.item_list:
                self.list_box.insert(tk.END, "%d: %s"%(self.item_list.index(item),item))


