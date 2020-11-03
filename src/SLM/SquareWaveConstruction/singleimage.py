"""
Provide GUI class to create a single image hologram.

@author: Luke Kurlandski
@date: December 2019
@copyright: Copyright 2019, Luke Kurlandski, all rights reserved

Special thanks to Daniel Stolz, Matthew Van Soelen, and Dr. David McGee.

Read the Program Guide for detailed information about this program.
"""

import tkinter as tk
from tkinter import filedialog
from datetime import datetime 
from datetime import timedelta 
import time
import threading
import numpy as np
import ntpath

from serialcontrol import Motor
from serialcontrol import Shutter
from serialcontrol import Laser
from exceptions import InputError
from exceptions import FileFormatError
from exceptions import NoFileError
from exceptions import MissingDataError
from exceptions import UnknownError
from exceptions import EquipmentError
from exceptions import UserInterruptError

from hologramcreator import HologramCreator
from imageprocessing import MyImage

class SingleImage(HologramCreator):

    def __init__(self, root: tk.Tk):
        """
        Constructor call with parent constructor.
        """

        #Create a root with HologramCreator, the parent.
        window_configs = {
            'Window Title':'Single Image Hologram Creator -- '
                + 'Copyright 2019, Luke Kurlandski, all rights reserved',
            'Frames Vertical':4,
            'Frames Horizontal':5
        }
        super().__init__(root, window_configs)
        #Apply some frame modifications for large wigits.
        self.frames[0][1].grid(row=0, column=1, pady=10, rowspan=200, columnspan=200, sticky='NW')
        self.frames[1][1].grid(row=1, column=1, pady=10, rowspan=200, columnspan=200, sticky='W')
        self.frames[0][2].grid(row=0, column=2, pady=10, rowspan=200, columnspan=200, sticky='NW', padx=250)
        self.frames[0][3].grid(row=0, column=3, pady=10, rowspan=200, columnspan=600, sticky='NE', padx=450)
        #Setup main window with HologramCreator, the parent.
        super().setup_film(self.frames[0][0])
        super().setup_image_select(self.frames[1][0])
        super().setup_initialize_experiment(self.frames[2][0])
        super().setup_while_running(self.frames[3][0])
        super().setup_exposure_details(self.frames[0][2])
        super().setup_ignore_details(self.frames[0][2])
        super().setup_laser_details(self.frames[0][2])
        super().setup_image_array(self.frames[0][3])
        #Setup main window with SingleImage, the self.
        self.setup_menu()
        self.setup_image_default(self.frames[0][1], self.frames[1][1])
        #Open the previous experiment
        self.open_experiment('Experiments/Previous Experiment.txt')

##############################################################################
#Setup Menu and Main Window
##############################################################################

    def setup_menu(self):
        """
        Set up the menu for the main window.
        """
        
        #Create label-command pairs in a dictionary for the various submenus.
        submenu_file = {
            'Quit':self.root.destroy,
            'Open Experiment':self.open_experiment,
            'Open Previous':lambda:self.open_experiment(
                'Experiments/Previous Experiment.txt'),
            'Open Example':lambda:self.open_experiment(
                'Experiments/Example Experiment.txt'),
            'Clear Inputs':self.clear_experiment
        }
        submenu_serial = {
            'Motor':lambda:self.set_serial_configs({'Serial Name':'Motor',
                'File Name':'Equipment/Motor Serial.txt'}),
            'Shutter':lambda:self.set_serial_configs({'Serial Name':'Shutter',
                'File Name':'Equipment/Shutter Serial.txt'}),
            'Laser':lambda:self.set_serial_configs({'Serial Name':'Laser',
                'File Name':'Equipment/Laser Serial.txt'}) 
        }
        submenu_equipment = {
            'Motor':lambda:self.set_equipment_settings(
                'Equipment/Motor Settings.txt', 'Motor'),
            'Shutter':lambda:self.set_equipment_settings(
                'Equipment/Shutter Settings.txt', 'Shutter'),
            'Laser':lambda:self.set_equipment_settings(
                'Equipment/Laser Settings.txt', 'Laser')
        }
        submenu_view = {
            'Image as Array':lambda:self.display_image_array(self.image),
            'Mapping Graph':self.generate_plot
        }
        submenu_help = {
            'General':lambda:self.help_window('Help/General.txt'),
            'Set Up Film':lambda:self.help_window('Help/Set Up Film.txt'),
            'Image Selection':lambda:self.help_window('Help/Exposure Details.txt'),
            'Exposure Details':lambda:self.help_window('Help/Set Up Film.txt'),
            'Initialize Experiment':lambda:self.help_window('Help/Initialize Experiment.txt'),
            'While Running':lambda:self.help_window('Help/While Running.txt')
        }
        #Dictionary of dictionaries to describe the whole menu.
        menu_total = {
            #Name of Submenu : dictionary of label-command pairs
            'File':submenu_file,
            'Serial':submenu_serial,
            'Equipment':submenu_equipment,
            'View':submenu_view,
            'Help':submenu_help
        }
        #Pass to parent method to create a main menu.
        self.main_menu = super().create_mainmenu(self.root, menu_total)
    
    def setup_image_default(self, frame_top:tk.Frame, frame_bottom:tk.Frame):
        """
        Set up the default images on main window.
        """

        image_configs = {
            'max_display_x':200,
            'max_display_y':200,
            'file_image':'Images/Sample Image.png',
            'name_image':'Sample Image'
        }
        try:
            self.image = MyImage(image_configs)
        except NoFileError as e:
            e.advice = 'Place a new default image in the correct directory.'
            super().error_window(e)
            return
        self.label_image_title = tk.Label(frame_top)
        self.label_image_title.pack()
        self.label_image = tk.Label(frame_top, 
            image=self.image.original_tkinter)
        self.label_image.pack()
        self.label_imagemod_title = tk.Label(frame_bottom, 
            text='Modified Sample Image')
        self.label_imagemod_title.pack()
        self.label_imagemod = tk.Label(frame_bottom, 
            image=self.image.modified_tkinter)
        self.label_imagemod.pack()

##############################################################################
#Choose Image
##############################################################################

    def image_select(self, file_image=None):
        """
        Select an image from a file dialogue box and update on screen.
        """
        
        if file_image is None:
            file_image = filedialog.askopenfilename(initialdir='Images', 
                title="Select Image", filetypes=(("png images","*.png"),
                    ("jpeg images","*.jpeg"), ("All files","*.*")))
            image_name = ntpath.basename(file_image)
        image_configs = {
            'max_display_x':200,
            'max_display_y':200,
            'file_image':file_image,
            'name_image':'%s'%(file_name)
        }
        try:
            self.image = MyImage(image_configs)
        except NoFileError as e:
            e.advice = 'Select a different image.'
            super().error_window(e)
            return
        self.label_image.configure(image=self.image.original_tkinter)
        self.label_imagemod.configure(image=self.image.modified_tkinter)
        self.label_image_title.configure(text='%s'%(file_name))
        self.label_imagemod_title.configure(text='%s, Modified'%(file_name))

##############################################################################
#Data Processing Driver Function
##############################################################################

    def prepare_for_experiment(self):
        """
        Drives the processes to process data, calls other methods.
        """
        
        #Read equipment data from non-consolidated files and store in variables.
        try:
            self.equipment_configs_motor = self.read_equipment_data('Motor')
        except FileFormatError as e:
            super().error_window(e)
            return
        try:
            self.equipment_configs_shutter = self.read_equipment_data('Shutter')
        except FileFormatError as e:
            super().error_window(e)
            return
        try:
            self.equipment_configs_laser = self.read_equipment_data('Laser')
        except FileFormatError as e:
            super().error_window(e)
            return
        #Get data from main window.
        try:
            self.collect_raw_data()
        except InputError as e:
            e.advice = 'Advice you read to the guide for proper input format.'
            super().error_window(e)
            return
        #Write main window data into an experiment file.
        try:
            self.write_experiment()
        except NoFileError as e:
            super().error_window(e)
            return
        #Store all data into a single file.
        try:
            self.consolidate_files()
        except NoFileError as e:
            super().error_window(e)
            return
        #Further processing of data into mappings, and modifify to images.
        self.modify_and_map()
        #Generate a time estimation
        self.run_time()

##############################################################################
#Data Processing Worker Functions
##############################################################################
       
    def read_equipment_data(self, equipment:str):
        """
        Get the equipment data from equipment files.
        """
        
        settings = super().read_file('Equipment/'+equipment+' Settings.txt')
        serial = super().read_file('Equipment/'+equipment+' Serial.txt')
        configs_old = {**serial, **settings}
        configs_new = {}
        try:
            for old_key in configs_old.keys():
                new_key = old_key.replace(equipment, '').replace('Serial', '').lstrip()
                configs_new[new_key] = configs_old[old_key]
            return configs_new
        except Exception as e:
            message = ('An error occurred processing data from ' + equipment +
                ' files:\n\tEquipment/' + equipment + ' Settings.txt\n\t'
                    'Equipment/' + equipment + ' Motor Serial.txt')
            advice = 'Delete these files.'
            raise FileFormatError(message, e, advice)

    def collect_raw_data(self):
        """
        Pull raw data from window and save in variables.
        """

        #Hologram width.
        try:
            self.hologram_width = float(self.entry_width.get().strip()) 
        except ValueError as e:
            message = 'Hologram width must be a floating point.'
            raise InputError(message, e)
        #Hologram height.
        try:
            self.hologram_height = float(self.entry_height.get().strip()) 
        except ValueError as e:
            message = 'Hologram height must be a floating point.'
            raise InputError(message, e)
        #Spot size
        try:
            val = self.entry_spot.get().strip()
            if val != '':
                self.spot_size = float(val)
            else:
                self.spot_size = -1
        except ValueError as e:
            message = 'Spot size must be a floating point.'
            raise InputError(message, e)
        #Pixels Horizontal.
        try:
            val = self.entry_pixel_x.get().strip()
            if val != '':
                self.pixels_x = int(val)
            else:
                self.pixels_x = self.image.original_PIL.width
        except ValueError as e:
            message = 'Horizontal Pixels must be an int.'
            raise InputError(message, e)
        #Pixels Vertical.
        try:
            val = self.entry_pixel_y.get().strip()
            if val != '':
                self.pixels_y = int(val)
            else:
                self.pixels_y = self.image.original_PIL.height
        except ValueError as e:
            message = 'Vertical Pixels must be an int.'
            raise InputError(message, e)
        self.cropping = self.entry_crop.get().strip()
        self.strings_exposure = self.text_exposure.get(1.0, 'end-1c').strip()
        self.strings_ignore = self.text_ignore.get(1.0, 'end-1c').strip()
        self.strings_laser = self.text_laser.get(1.0, 'end-1c').strip()
    
    def write_experiment(self):
        """
        Get a file from the user and write experiment data there.
        """
        
        #Get file from user in dialogue box and write to files.
        self.file_experiment = ''
        while self.file_experiment == '':
            self.file_experiment = super().get_save_file()
        #Put all data in a dictionary for writing to file.
        datas = {
            'Hologram Width':self.hologram_width,
            'Hologram Height':self.hologram_height,
            'Spot Size':self.spot_size,
            'Pixels Horizontal':self.pixels_x, 
            'Pixels Vertical':self.pixels_y,
            'Cropping' :self.cropping,
            'Strings Exposure':self.strings_exposure,
            'Strings Ignore':self.strings_ignore,
            'Strings Laser':self.strings_laser,
            'Image File':self.image.file_image
        }
        super().write_file('Experiments/Previous Experiment.txt', datas, 'w')
        super().write_file(self.file_experiment, datas, 'w')
    
    def consolidate_files(self):
        """
        Write all data files into one file for simple experiment documentation.
        """

        #Get all the data from the settings files and append to main save file.
        data_list = []
        try:
            data_list.append(super().read_file('Equipment/Motor Settings.txt'))
            data_list.append(super().read_file('Equipment/Shutter Settings.txt'))
            data_list.append(super().read_file('Equipment/Laser Settings.txt'))
            data_list.append(super().read_file('Equipment/Motor Serial.txt'))
            data_list.append(super().read_file('Equipment/Shutter Serial.txt'))
            data_list.append(super().read_file('Equipment/Laser Serial.txt'))
        except NoFileError as e:
            raise e
        data_dict = {}
        for data in data_list:
            data_dict.update(data)
        super().write_file(self.file_experiment, data_dict, 'a')
        super().write_file('Experiments/Previous Experiment.txt', data_dict, 'a')

    def modify_and_map(self):
        """
        Process the data by modifying images, creating mappings, delta x, y.
        """

        #Modify the image and display.
        self.image.downsize_image((self.pixels_x, self.pixels_y))
        self.image.crop_image(self.cropping)
        super().insert_image_array(self.image, self.text_array)
        self.label_imagemod.configure(image=self.image.modified_tkinter)
        #Process other data into mappings of pixel values and delta distances.
        configs_timing = {
            'Input Exposure':self.strings_exposure,
            'Input Ignore':self.strings_ignore,
            'Gradient Range':256
        }
        configs_laser = {
            'Input Laser':self.strings_laser,
            'Gradient Range':256
        }
        self.map_timing = super().map_timing(configs_timing)
        self.map_laser_power = super().map_laser_power(configs_laser)
        self.delta_x = self.hologram_width / self.pixels_x
        self.delta_y = self.hologram_height / self.pixels_y
        dpi = self.image.modified_PIL.width / (39.37 * self.hologram_width)
        self.label_dpi.configure(text='Image Resolution (dpi): '+str(int(dpi)))
    
    def run_time(self):
        """
        Generate a rough runtime estimation and display on window.
        """
        
        run_time = 0
        y_after_crop = self.image.modified_PIL.height
        x_after_crop = self.image.modified_PIL.width
        image_as_array = np.transpose(self.image.modified_array)
        #Loop through every potential grating on hologram
        for i in range (0, y_after_crop):
            visited_row = False
            farthest_x = 0
            #Calculate exposure time
            for j in range (0, x_after_crop):
                add = self.map_timing[image_as_array[j][i]]
                if add != 0:
                    visited_row = True
                    farthest_x = j
                    run_time += add
            #Calculate travel time in x direction
            if visited_row == True:
                run_time += ((farthest_x / x_after_crop) * self.hologram_width / .001)
        #Calculate travel time in y direction
        run_time += self.hologram_height / .001
        #Print on Main Window.
        end_time = (datetime.now() + timedelta(seconds=run_time)).strftime('%H:%M:%S -- %d/%m/%Y')
        self.label_est_time.configure(text='End Time Estimate: '+end_time)
    
    def generate_plot(self):
        """
        Display a plot of the mappings, if they have been produced.
        """

        try:
            data = {
                'Exposure Time (s)':self.map_timing, 
                'Laser Power (mW)':self.map_laser_power
            }
            super().generate_plot(data)
        except Exception:
            pass
                    
##############################################################################
#Run Experiment Driver Function
##############################################################################
       
    def run_experiment(self):
        """
        Run the experiment by calling methods to handle experiment.
        """

        #Update visuals on the main window.
        start = datetime.now().strftime('%H:%M:%S -- %d/%m/%Y')
        self.label_start_time.configure(text='Start Time: '+start)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(0)
        self.root.update()
        #Establish and initialize the equipment for experiment.
        try:
            #Use simple threading to prevent laggy main window.
            x = threading.Thread(target=self.initialize_equipment)
            x.start()
            while x.is_alive():
                self.root.update()
                time.sleep(.25)
            x.join()
        except EquipmentError as e: 
            super().error_window(e)
            super().close_ports(self.equipment)
            return
        except PermissionError as e:
            message = 'Could not establish connection with a serial port.'
            advice = 'Unplug the serial port from computer. Plug back in.'
            super().error_window(EquipmentError(message, e, advice))
            super().close_ports(self.equipment)
            return
        except Exception as e:
            message = 'Unknown error occured initializing equipment.'
            super().error_window(EquipmentError(message, e))
            super().close_ports(self.equipment)
            return
        #Conduct the movement and exposure process.
        try:
            #Use simple threading to prevent laggy main window.
            x = threading.Thread(target=self.movement)
            x.start()
            while x.is_alive():
                self.root.update()
                time.sleep(.25)
            x.join()
        except UserInterruptError as e:
            super().close_ports(self.equipment)
            super().error_window(e)
            return
        except EquipmentError as e:
            super().close_ports(self.equipment)
            super().error_window(e)
            return
        except Exception as e:
            super().close_ports(self.equipment)
            message = 'Unknown error occured running experiment.'
            super().error_window(UnknownError(message, e))
            return
        #Finally, perform clean up processes.
        self.experiment_finish()

##############################################################################
#Run Experiment Worker Functions
##############################################################################

    def initialize_equipment(self):
        """
        Alter equipment status to initial conditions for experiment.
        """
        
        #Create the objects amd store in a list.
        self.equipment = []
        self.motor = Motor({**self.equipment_configs_motor,**{'Axes':(1,2)}})
        self.equipment.append(self.motor)
        self.shutter = Shutter(self.equipment_configs_shutter)
        self.equipment.append(self.shutter)
        self.laser = Laser(self.equipment_configs_laser)
        self.equipment.append(self.laser)
        #Initialize to start positions.
        self.motor.move_home(1) 
        self.motor.move_home(2) 
        self.laser.turn_on_off(True)

    def movement(self):
        """
        Conduct the physical movement of machinery and such.
        """

        #Move through the image array, expose according to mappings.
        prev_pix = None
        prev_powr = None
        y_after_crop = self.image.modified_PIL.height
        x_after_crop = self.image.modified_PIL.width
        image_as_array = np.transpose(self.image.modified_array)
        for i in range(0, y_after_crop):
            on_this_row = False 
            for j in range(0, x_after_crop):
                self.check_pause_abort()
                pix = image_as_array[j][i]
                time = self.map_timing[pix]
                powr = self.map_laser_power[pix]
                #Enter conditional if the current pixel should be exposed.
                if not super().compare_floats(time, 0):
                    self.update_progress(pix,time,powr,i,j)
                    #Change the laser's power if the pixel value has changed.
                    if prev_pix is not None and prev_powr is not None:
                        if not super().compare_floats(powr, prev_powr):
                            self.laser.change_power(powr)
                    #Move motors to the correct positions and open shutter.
                    if not on_this_row:
                        self.motor.move_absolute(2, i*self.delta_y*1000) 
                        on_this_row = True
                    self.motor.move_absolute(1, j*self.delta_x*1000) 
                    self.shutter.toggle(time)
                    #Update previous pixel info to current pixel info
                    prev_pix = pix
                    prev_powr = powr

    def check_pause_abort(self):
        """
        Handle a pause or an abort operation during movement.
        """
        
        selection = self.listbox.curselection()
        if 0 in selection:
            return
        if 1 in selection:
            message = 'User paused the experiment.'
            advice = 'Click Run in listbox to continue.'
            super().error_window(UserInterruptError(message, None, advice))
            while 1 in selection:
                selection = self.listbox.curselection()
                time.sleep(.5)
        if 2 in selection:
            message = 'User aborted the experiment.'
            advice = 'Click Run Experiment Button to restart.'
            super().error_window(UserInterruptError(message, None, advice))
            raise UserInterruptError(message, None, advice)
            
    def update_progress(self, pix:int, time:float, powr:float, i:int, j:int):
        """
        Update the exposure information for the current pixel on main window.
        """

        self.label_position.configure(text='Location (x,y) : (' 
            +str(j)+','+str(i)+')')
        self.label_details.configure(text='Details (pxl,pwr,time) : ('
            +str(pix)+','+str(powr)+','+str(time) + ')')
        
    def experiment_finish(self):
        """
        Conduct final processes at end of experiment.
        """
        
        super().close_ports(self.equipment)
        end = datetime.now().strftime('%H:%M:%S -- %d/%m/%Y')
        self.label_end_time.configure(text='True Experiment End Time: '+end)
        screenshot = super().screenshot()
        screenshot.save(self.file_experiment.replace('.txt','.png'))

##############################################################################
#Open Prior Experiments
##############################################################################

    def open_experiment(self, file_name:str=None):
        """
        Open an experiment from file and populate wigits with data.
        """
        
        #Determine which experiment to open and get that data.
        if file_name is None:
            file_name = filedialog.askopenfilename(title="Open Experiment",
                filetypes=(("txt files","*.txt"),("All files","*.*")),
                    initialdir='Experiments')
        try:
            datas = super().read_file(file_name)
        except NoFileError as e:
            super().error_window(e)
            return
        #Clear the input in main window.
        self.clear_experiment()
        #Populate the main window with data from file.
        self.populate_main(datas)
        #Overwrite the settings and serial files with data.
        self.overwrite_settings_serials(datas)
        
    def clear_experiment(self):
        """
        Clear all the input wigits on the main window before open experiment.
        """

        wigits = [
            self.entry_pixel_x,
            self.entry_pixel_y,
            self.entry_spot,
            self.entry_width,
            self.entry_height,
            self.entry_crop,
            self.text_exposure,
            self.text_ignore,
            self.text_laser
        ]
        super().clear_wigits(wigits)
        
    def populate_main(self, datas:dict):
        """
        Fill wigits with datas from file.
        """
        
        #If data is not present, do not fill.
        if 'Hologram Width' in datas:
            self.entry_width.insert(1, datas['Hologram Width'])
        if 'Hologram Height' in datas:
            self.entry_height.insert(1, datas['Hologram Height'])
        if 'Spot Size' in datas:
            self.entry_spot.insert(1, datas['Spot Size'])
        if 'Pixels Horizontal' in datas:
            self.entry_pixel_x.insert(1, datas['Pixels Horizontal'])
        if 'Pixels Vertical' in datas:
            self.entry_pixel_y.insert(1, datas['Pixels Vertical'])
        if 'Cropping' in datas:
            self.entry_crop.insert(1, datas['Cropping'])
        if 'Strings Exposure' in datas:
            self.text_exposure.insert(1.0, datas['Strings Exposure'])
        if 'Strings Ignore' in datas:
            self.text_ignore.insert(1.0, datas['Strings Ignore'])
        if 'Strings Laser' in datas:
            self.text_laser.insert(1.0, datas['Strings Laser'])
        if 'Image File' in datas:
            self.image_select(datas['Image File'])
        
    def overwrite_settings_serials(self, datas):
        """
        Overwrite the equipment settings files in the case of loading experiment.
        """
        
        #Dictionaries for use within each special file.
        motor_settings = {}
        shutter_settings = {}
        laser_settings = {}
        motor_serials = {}
        shutter_serials = {}
        laser_serials = {}
        #Move through large data and organize according to headers.
        for key in datas.keys():
            KEY = key.upper()
            has_SERIAL = True if 'SERIAL' in KEY else False
            if 'MOTOR' in KEY:
                if has_SERIAL:
                    motor_serials[key] = datas[key]
                else:
                    motor_settings[key] = datas[key]
            if 'SHUTTER' in KEY:
                if has_SERIAL:
                    shutter_serials[key] = datas[key]
                else:
                    shutter_settings[key] = datas[key]
            if 'LASER' in KEY and 'STRINGS LASER' != KEY: 
                if has_SERIAL:
                    laser_serials[key] = datas[key]
                else:
                    laser_settings[key] = datas[key]
        #Overwite files with new information.
        super().write_file('Equipment/Motor Settings.txt', motor_settings)
        super().write_file('Equipment/Shutter Settings.txt', shutter_settings)
        super().write_file('Equipment/Laser Settings.txt', laser_settings)
        super().write_file('Equipment/Motor Serial.txt', motor_serials)
        super().write_file('Equipment/Shutter Serial.txt', shutter_serials)
        super().write_file('Equipment/Laser Serial.txt',laser_serials)