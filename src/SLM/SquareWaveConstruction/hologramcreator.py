"""
Provide GUI base class to create image holograms.

@author: Luke Kurlandski
@date: December 2019
@copyright: Copyright 2019, Luke Kurlandski, all rights reserved

Special thanks to Daniel Stolz, Matthew Van Soelen, and Dr. David McGee.

Read the Program Guide for detailed information about this program.
"""

import numpy as np
import tkinter as tk
from tkinter import ttk
import serial 
import serial.tools.list_ports 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pandas import DataFrame

from app import App
from imageprocessing import MyImage
from exceptions import NoFileError
from exceptions import UnknownError

class HologramCreator(App):

##############################################################################
#Constructor
##############################################################################

    def __init__(self, root:tk.Tk, configs:dict):
        """
        Constructor call with parent constructor.
        """

        #Data from arguments.
        frames_horizontal = (configs['Frames Horizontal'] if 'Frames Horizontal'
            in configs else 0)
        frames_vertical = (configs['Frames Vertical'] if 'Frames Vertical' 
            in configs else 0)
        if 'Window Title' not in configs:
            configs['Window Title'] = ('Sastooth Hixel Creator -- '
                + 'Copyright 2019, Matthew Van Soelen, all rights reserved')
        #Call to parent consructor.
        super().__init__(root, configs)
        #Create the frames for main window.
        self.frames = super().create_frames(self.root, 
            {'Frames Horizontal':frames_horizontal, 
            'Frames Vertical':frames_vertical})

##############################################################################
#Main Window Set Up Frames
##############################################################################

    def setup_initialize_experiment(self, frame:tk.Frame):
        """
        Set up the initialization of experiment section.
        """

        tk.Label(frame, text='Initialize Experiment', font="bold").pack()
        self.button_update = tk.Button(frame, text='Process and Save', 
            command=self.prepare_for_experiment)
        self.button_update.pack()
        self.label_dpi = tk.Label(frame, text='Image Resolution (dpi)')
        self.label_dpi.pack()
        self.button_run = tk.Button(frame, text = 'Run Experiment', 
            command=self.run_experiment)
        self.button_run.pack()

    def setup_while_running(self, frame:tk.Frame):
        """
        Set up main window for wigits related to while running experiment.
        """

        tk.Label(frame, text='While Running', font="bold").pack()
        self.listbox = tk.Listbox(frame, height=3, selectmode=tk.SINGLE)
        self.listbox.config(width=20)
        self.listbox.pack(fill = tk.BOTH)
        self.listbox.insert(1, "Run")
        self.listbox.insert(2, "Pause")
        self.listbox.insert(3, "Abort")
        self.listbox.activate(1)
        self.listbox.config(width=80)
        self.label_start_time = tk.Label(frame, text='Start Time: ')
        self.label_start_time.pack()
        self.label_est_time = tk.Label(frame, text='End Time Estimate: ')
        self.label_est_time.pack()
        self.label_end_time = tk.Label(frame, text='True Experiment End Time: ')
        # self.label_end_time.pack()
        # self.label_position = tk.Label(frame, text='Current Location (x,y) : ')
        # self.label_position.pack() 
        self.label_details = tk.Label(frame, text='Details (pxl,pwr,time) : ')
        self.label_details.pack()

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
        
        tk.Label(frame, text='Exposure time (s)', font='bold').grid(row=4, column=1)
        self.entry_exp_time = tk.Entry(frame, width = 15)
        self.entry_exp_time.grid(row=5, column = 1)

        self.g_reverse = tk.IntVar()
        tk.Checkbutton(frame, text = 'Reverse Grating', variable = self.g_reverse).grid(row=6, column=1)
        
        selection_frame = tk.Frame(frame, borderwidth=2, relief=tk.SOLID, pady=4)
        selection_frame.grid(row=6, column=0)
        tk.Label(selection_frame, text='Custom Grating', font='bold').grid(row=0, column=0)
        self.button_image = tk.Button(selection_frame, text='Select a Grating', 
            command=self.grating_select)
        self.button_image.grid(row=0, column=1)

    def setup_laser_details(self, frame:tk.Frame):
        """
        Set up the exposure textbox.
        """

        sub_frame = tk.Frame(frame)
        sub_frame.pack()
        tk.Label(sub_frame, text='Laser Powers (mW)').grid(row=0, column=0)
        text_configs = {
            'Frame':sub_frame,
            'y Row':1,
            'x Row':2
        }
        self.text_laser = super().text_apply_scrollbars(self.root, text_configs)
        self.text_laser.configure(width=20, height=10)
        self.text_laser.grid(row=1, column=0)
        
    
    def setup_experiment_details_view(self, frame:tk.Frame):
        '''
        '''
        
        sub_frame = tk.Frame(frame, borderwidth=2, relief=tk.SUNKEN)
        sub_frame.pack()
        
        tk.Label(sub_frame, text = "Selection Details", font='bold').grid(row=0, column=0, columnspan=2)
        self.image_name_label = tk.Label(sub_frame, text = "Image Name: ")
        self.image_name_label.grid(row=1, column=0)
        self.grating_name_label = tk.Label(sub_frame, text = "Grating Name: ")
        self.grating_name_label.grid(row=2, column=0)
        self.grating_type_label = tk.Label(sub_frame, text= "Grating Type: ")
        self.grating_type_label.grid(row=3, column=0)
        self.rotation_angle_label = tk.Label(sub_frame, text = "Rotation Angle: ")
        self.rotation_angle_label.grid(row=4, column=0)
        self.y_min_label = tk.Label(sub_frame, text = "Y min: ")
        self.y_min_label.grid(row=1, column=1)
        self.y_max_label = tk.Label(sub_frame, text = "Y max: ")
        self.y_max_label.grid(row=2, column=1)
        self.period_label = tk.Label(sub_frame, text = "Period: ")
        self.period_label.grid(row=3, column=1)
        self.reverse_label = tk.Label(sub_frame, text = "Reverse: ")
        self.reverse_label.grid(row=4, column=1)
        self.exp_time_label = tk.Label(sub_frame, text="Exposure Time: ")
        self.exp_time_label.grid(row=5, column=0)
        
##############################################################################
#Data Processing
##############################################################################

    def process_user_string(self, user_lines:str, configs:dict):
        """
        Process raw user string input into usful data arrays.

        Returns: 
            data : list[float]
        """

        #Data from arguments.
        gradient_range = (configs['Gradient Range'] if 'Gradient Range' 
            in configs else 256)   
        #Process the input string based upon comman and bracket location.
        data = [-1] * gradient_range
        for line in user_lines.splitlines():
            comma = line.find(',')
            bracket = line.find(']')
            start = int(line[1:comma])
            end = int(line[comma+1:bracket])
            x = line.find('x')
            #If 'x' exists, use a linear mapping for the data values.
            if x >= 0:
                factor = float(line[bracket+2:x])
                for i in range(start,end):
                    data[i] = round(factor*i,2)
            #If 'x' does not exist, populate data range with a constant.
            elif x == -1:
                if ':' in line:
                    value = float(line[bracket+2:len(line)])
                else:
                    value = 0
                for i in range(start, end):
                    data[i] = value
        return data

    def map_timing(self, configs:dict):
        """
        Generate the array which maps a (pixel) value to an exposure length.
        """

        #Data from arguments.
        gradient_range = (configs['Gradient Range'] if 'Gradient Range' 
            in configs else 256)
        input_ignore = (configs['Input Ignore'] if 'Input Ignore' 
            in configs else [-1] * gradient_range)
        input_exposure = (configs['Input Exposure'] if 'Input Exposure' 
            in configs else [1] * gradient_range)
        #Process exposure input and override with ignore input.
        try:
            map_timing = self.process_user_string(input_exposure, 
                {'Gradient Range':gradient_range})
        except Exception as e:
            raise e #Exception('Error: exposure string is improperly formatted.')
        try:
            ignore_override = self.process_user_string(input_ignore, 
                {'Gradient Range':gradient_range})
        except Exception:
            raise Exception('Error: ignore string is improperly formatted.')
        for i in range(0, gradient_range):
            if ignore_override[i] == 0:
                map_timing[i] = 0
        return map_timing

    def map_laser_power(self, configs:dict):
        """
        Generate the array which maps a (pixel) value to a laser power.
        """

        #Data from arguments.
        gradient_range = (configs['Gradient Range'] if 'Gradient Range' 
            in configs else 256)
        input_laser = (configs['Input Laser'] if 'Input Laser' 
            in configs else [0] * gradient_range)
        try:
            map_laser_power = self.process_user_string(input_laser, 
                {'Gradient Range':gradient_range})
        except Exception:
            raise Exception('Error: laser string is improperly formatted.')
        return map_laser_power
        
    
    def map_gratings(self, configs:dict):
        def cycle_image( j, i):
            if j % 2 == 0 and i % 2 == 0:
                return 0
            elif j % 2 == 0 and i % 2 == 1:
                return 1
            elif j % 2 == 1 and i % 2 == 0:
                return 2
            elif j % 2 == 1 and i % 2 == 1:
                return 3
            else:
                return -1
        
        gradient_range = (configs['Gradient Range'] if 'Gradient Range' 
            in configs else 256)
        grating_color = (configs['Input Grating Color'] if 'Input Grating Color' 
            in configs else [-1] * gradient_range)
        
        try:
            grating_color_map = self.process_user_string(grating_color, 
                {'Gradient Range':gradient_range})
        except Exception:
            raise Exception('Error: Grating by Color string is improperly formatted')
        
        y_after_crop = self.image.modified_PIL.height
        x_after_crop = self.image.modified_PIL.width
    
        if self.item_list and len(self.item_list) > 3:
            grating_map = np.zeros((y_after_crop,x_after_crop), dtype=np.uint16)
            grating_map = np.transpose(grating_map)
            
            self.final_array = grating_map
            
            temp_array_list = []
            for i,item in enumerate(self.item_list):
                temp_array_list[i] = np.transpose(item[i].image_as_array)
            
            for i in range(0, y_after_crop):
                for j in range(0, x_after_crop):
                    grating_map[j][i] = cycle_image(j,i)
                    current_color = temp_array_list[grating_map[j][i]][j][i]
                    self.final_array[j][i] = current_color
                    grating_option = grating_color_map[current_color]
                    if grating_option != -1:
                        grating_map[j][i]= grating_option
                    
            print(grating_map)
            print(self.final_array)
        return grating_map

##############################################################################
#Data Display
##############################################################################

    def display_image_array(self, image:MyImage):
        """
        Display a MyImage object as an array representation in popup window.
        """

        #Get the display window for the image.
        configs = {
            'Window Width':600, 
            'Window Height':600, 
            'Window Title':image.name_image+', as Array'
        }
        window = super().popup_window(self.root, configs)
        super().close_help_menu(window, 'Help/Image As Array.txt')
        #Get the text wigit and fill with image as array.
        text, frame = self.text_fill_window(window, True)
        self.insert_image_array(image, text)
            
    def insert_image_array(self, image:MyImage, text:tk.Text):
        """
        Fill a text wigit with the contents of an image as array.
        """
        
        super().clear_wigits([text])
        image_as_array = np.transpose(image.modified_array)
        for i in image_as_array:
            for j in i:
                if j <= 9:
                    spaces = '   '
                if j > 9:
                    spaces = '  '
                if j > 99:
                    spaces = ' '
                text.insert(tk.END, str(j)+spaces)
            text.insert(tk.END,'\n')

        
##############################################################################
#Read and Write to Files in Special Format
##############################################################################

    def read_file(self, file_name:str):
        """
        Process a file containing datas separated by a '######' and '::'.

        Returns:
            items : dict : [headings, values]
        """
        
        try:
            with open(file_name, 'r') as file:
                contents = file.read().split('####################')
        except FileNotFoundError as e:
            message = 'The file could not be located:\n' + file_name
            advice = ('If loading an experiment, choose another file.\nIf this'
                ' is a file that stores equipment data, then re-enter the data'
                ' and save. The file will be re-created')
            raise NoFileError(message, e, advice)
        items = {}
        for pair in contents:
            data = pair.split('::')
            try:
                items[data[0].strip('\n')] = data[1].strip('\n')
            except IndexError: 
                break 
        return items

    def write_file(self, file_name:str, configs:dict, mode:str='w'):
        """
        Write to a file containing datas separated by a '########' and '::'.
        """
        
        try:
            with open(file_name, mode) as file:
                for key in configs.keys():
                    file.write(str(key) + '::\n')
                    file.write(str(configs[key]) + '\n####################\n')
        except Exception as e:
            message = 'Error ocured writing to a file for unknown reasons.'
            super().error_window(UnknownError(message,e))

##############################################################################
#Serial Ports
##############################################################################

    def set_serial_configs(self, configs:dict):
        """
        Create a window to let the user specify serial port configs.
        """

        #Data from arguments.
        if 'Serial Name' in configs:
            serial_name = configs['Serial Name'] 
        else:
            raise Exception('Error: unspecified serial port.')
        if 'File Name' in configs:
            file_name = configs['File Name']
        else:
            raise Exception('Error: unspecified serial save file.')

        def serial_save():
            """
            Save the specifications of comboboxes into file_name.
            """
            serial_configs = {}
            for key in comboboxes.keys():
                serial_configs[key] = comboboxes[key].get()
            self.write_file(file_name, serial_configs)
            window.destroy()

        #Create and configure a serial port window.
        window_configs = {
            'Window Title':serial_name+' Serial Configs',
            'Window Width':240,
            'Window Height':220
        }
        window = super().popup_window(self.root, window_configs)
        super().close_help_menu(window, 'Help/Serial Configurations.txt')
        #Create labels for the user's choices.
        tk.Label(window, text="Port:").grid(row=0, column=0, pady=5, padx=10)
        tk.Label(window, text="Baudrate:").grid(row=1, column=0, pady=5, padx=10)
        tk.Label(window, text="Timeout:").grid(row=2, column=0, pady=5, padx=10) 
        tk.Label(window, text="Stopbits:").grid(row=3, column=0, pady=5, padx=10)
        tk.Label(window, text="Bytesize:").grid(row=4, column=0, pady=5, padx=10)
        tk.Label(window, text="Parity:").grid(row=5, column=0, pady=5, padx=10)
        #Construct the users choices for serial configurations.
        ports = []
        comlist = serial.tools.list_ports.comports()
        for i in comlist:
            ports.append(i.device)
        baudrates = ['150','300','600','1200','2400','4800','9600','19200']
        timeouts = ['.1','.5','1','1.5','2']
        stopbits = ['1','1.5','2']
        bytesizes = ['4','5','6','7','8']
        parities = ['None','Even','Odd','Space','Mark']
        #Create comboboxes displaying the user's choices.
        comboboxes = {
            serial_name+' Serial Port':ttk.Combobox(window, values=ports),
            serial_name+' Serial Baudrate':ttk.Combobox(window, values=baudrates),
            serial_name+' Serial Timeout':ttk.Combobox(window, values=timeouts),
            serial_name+' Serial Stopbits':ttk.Combobox(window, values=stopbits),
            serial_name+' Serial Bytesize':ttk.Combobox(window, values=bytesizes),
            serial_name+' Serial Parity':ttk.Combobox(window, values=parities),
        }
        row = 0
        for combobox in comboboxes.values():
            combobox.grid(row=row, column=1)
            row += 1
        #Fill comboboxes with previous data.
        try:
            previous_items = self.read_file(file_name)
            for key in previous_items.keys():
                comboboxes[key].set(previous_items[key])
        except NoFileError as e:
            super().error_window(e)
        #Create a save button for saving the data.
        button_save = tk.Button(window, text='Save Settings', command=serial_save)
        button_save.grid(row=row, column=0, columnspan=2, sticky=tk.W+tk.E)
        #Run the configuration window.
        window.mainloop()

    def close_ports(self, ports:list):
        """
        Safely close all serial ports in case of error, or end of program.
        """

        for port in ports:
            port.ser.close()

##############################################################################
#Equipment Settings
##############################################################################

    def set_equipment_settings(self, file_name:str, equipment_name:str):
        """
        Create a window for user to enter equipment configs.
        """

        def equipment_save():
            """
            Save the specifications of comboboxes into file_name.
            """
            equipment_configs = {}
            for key in entries.keys():
                equipment_configs[key] = entries[key].get()
            self.write_file(file_name, equipment_configs) 
            window.destroy()

        #Call the correct configuration-window-creator method.
        if equipment_name.upper() == 'MOTOR':
            equipment_things =  self.set_motor_settings(file_name)
        elif equipment_name.upper() == 'SHUTTER':
            equipment_things =  self.set_shutter_settings(file_name)
        elif equipment_name.upper() == 'LASER':
            equipment_things =  self.set_laser_settings(file_name)
        else:
            raise Exception('Error: equipment name not recognized.')
        next_row = equipment_things['Next Row']
        window = equipment_things['Window']
        entries = equipment_things['Entries']
        #Warning and save button
        label_warning = tk.Label(window, text='Incorrect Settings Damage Equipment')
        label_warning.grid(row=next_row, columnspan=2, sticky=tk.E+tk.W)
        button_save = tk.Button(window, text='Save', command=equipment_save)
        button_save.grid(row=next_row+1, columnspan=2, sticky=tk.E+tk.W)

    def set_motor_settings(self, file_name:str):
        """
        Create a window for user to enter motor configs.
        """

        #Create a equipment confiugrations window
        window_configs = {
            'Window Title':'Motor Settings',
            'Window Width':240,
            'Window Height':170
        }
        window = super().popup_window(self.root, window_configs)
        super().close_help_menu(window, 'Help/Motor Settings.txt')
        #Create labels, entry wigits, alter size of window.
        tk.Label(window, text = 'Serial port pause time (s):').grid(row=0)
        tk.Label(window, text = 'Motor Speed (mm/s):').grid(row=1)
        tk.Label(window, text = 'Acceleration (mm/s^2):').grid(row=2)
        tk.Label(window, text = 'Decceleration (mm/s^2):').grid(row=3)
        entries = {
            'Motor Command Pause':tk.Entry(window, width=10),
            'Motor Velocity':tk.Entry(window, width=10),
            'Motor Acceleration':tk.Entry(window, width=10),
            'Motor Decceleration':tk.Entry(window, width=10),
        }
        row = 0
        for key in entries.keys():
            entries[key].grid(row=row, column=1, pady=5, padx=10, sticky=tk.W)
            row += 1
        #Fill with previous data
        try:
            previous_items = self.read_file(file_name)
        except NoFileError as e:
            super().error_window(e)
            previous_items = {}
        for key in previous_items.keys():
            if key in entries:
                entries[key].insert(0, previous_items[key])
        #dict to return.
        equipment_things = {
            'Next Row':row,
            'Window':window,
            'Entries':entries
        }
        return equipment_things

    def set_shutter_settings(self, file_name:str):
        """
        Create a window for user to enter shutter configs.
        """

        #Create a equipment confiugrations window
        window_configs = {
            'Window Title':'Shutter Settings',
            'Window Width':240,
            'Window Height':120
        }
        window = super().popup_window(self.root, window_configs)
        super().close_help_menu(window, 'Help/Shutter Settings.txt')
        #Create labels, entry wigits, alter size of window.
        tk.Label(window, text = 'Serial port pause time (s):').grid(row=0)
        tk.Label(window, text = 'Operating Mode:').grid(row=1)
        entries = {
            'Shutter Command Pause':tk.Entry(window, width=10),
            'Shutter Operating Mode':tk.Entry(window, width=10),
        }
        row = 0
        for key in entries.keys():
            entries[key].grid(row=row, column=1, pady=5, padx=10, sticky=tk.W)
            row += 1
        #Fill with previous data
        try:
            previous_items = self.read_file(file_name)
        except NoFileError as e:
            super().error_window(e)
            previous_items = {}
        for key in previous_items.keys():
            if key in entries:
                entries[key].insert(0, previous_items[key])
        #dict to return.
        equipment_things = {
            'Next Row':row,
            'Window':window,
            'Entries':entries
        }
        return equipment_things
    
    def set_laser_settings(self, file_name:str):
        """
        Create a window for user to enter laser configs.
        """
        
        #Create a equipment confiugrations window
        window_configs = {
            'Window Title':'Laser Settings',
            'Window Width':250,
            'Window Height':145
        }
        window = super().popup_window(self.root, window_configs)
        super().close_help_menu(window, 'Help/Laser Settings.txt')
        #Create labels, entry wigits, alter size of window.
        tk.Label(window, text = 'Serial port pause time (s):').grid(row=0)
        tk.Label(window, text = 'Maximum Laser Power (mW):').grid(row=1)
        tk.Label(window, text = 'Power-Change Pause (s):').grid(row=2)
        entries = {
            'Laser Command Pause':tk.Entry(window, width=10),
            'Laser Max Power':tk.Entry(window, width=10),
            'Laser Power Change Pause':tk.Entry(window, width=10)
        }
        row = 0
        for key in entries.keys():
            entries[key].grid(row=row, column=1, pady=5, padx=10, sticky=tk.W)
            row += 1
        #Fill with previous data
        try:
            previous_items = self.read_file(file_name)
        except NoFileError as e:
            super().error_window(e)
            previous_items = {}
        for key in previous_items.keys():
            if key in entries:
                entries[key].insert(0, previous_items[key])
        #dict to return.
        equipment_things = {
            'Next Row':row,
            'Window':window,
            'Entries':entries
        }
        return equipment_things
        
##############################################################################
#Other
##############################################################################

    def compare_floats(self, x:float, y:float, imprecision:float=.05):
        """
        Compare two floating point values with an imprecision.

        Returns:
            True/False if equal/inequal
        """

        if x-imprecision < y < x+imprecision:
            return True
        else:
            return False