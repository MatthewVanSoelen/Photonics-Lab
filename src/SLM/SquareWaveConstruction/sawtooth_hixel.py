"""
Provide GUI class to create a single image hologram.

@author: Luke Kurlandski, Matthew Van Soelen
@date: July 16, 2020

Special thanks to Daniel Stolz, and Dr. David McGee.

"""

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
from grating_processing import MyGrating
from list_item import ListItem
from slm_window import SLM_window
import pdb

class Sawtooth_Hixel(HologramCreator):

    def __init__(self, root: tk.Tk):
        """
        Constructor call with parent constructor.
        """

        #Create a root with HologramCreator, the parent.
        window_configs = {
            'Window Title':'SLM Image Hologram Creator -- '
                + 'Copyright 2020, Luke Kurlandski and Matthew Van Soelen, all rights reserved',
            'Frames Vertical':4,
            'Frames Horizontal':5
        }
        super().__init__(root, window_configs)
        self.item_list = []
        self.list_box = None
        self.slm = None
        self.grating_name = None
        self.grating_file_path = None
        
        #Apply some frame modifications for large wigits.
        self.frames[1][2].grid(row=1, column=2, pady=10, rowspan=200,  sticky='NW')
        self.frames[2][2].grid(row=2, column=2, pady=10, rowspan=200,  sticky='W')
        self.frames[0][3].grid(row=0, column=3, pady=10, rowspan=200,  sticky='NW', padx=10)
        self.frames[0][4].grid(row=0, column=4, pady=10, rowspan=200,  sticky='NE', padx=10)
        
        #Setup main window with HologramCreator, the parent.
        '''
        super().setup_film(self.frames[0][0])
        super().setup_image_select(self.frames[1][0])
        '''
        super().setup_initialize_experiment(self.frames[0][0])
        super().setup_while_running(self.frames[1][0])
        super().setup_grating_options(self.frames[0][1])
        '''
        super().setup_exposure_details(self.frames[0][3])
        super().setup_ignore_details(self.frames[0][3])
        '''
        super().setup_laser_details(self.frames[2][2])
        '''
        super().setup_grating_details(self.frames[0][3])
        super().setup_image_array(self.frames[0][4])
        '''
        super().setup_experiment_details_view(self.frames[2][1])

        #Setup main window with Sawtooth_Hixel, the self.
        self.setup_menu()
        '''
        self.setup_image_default(self.frames[1][2], self.frames[2][2])
        '''
        self.setup_grating_default(self.frames[0][2])
        self.setup_list_view(self.frames[1][1])
        

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
            'Help':submenu_help
        }
        #Pass to parent method to create a main menu.
        self.main_menu = super().create_mainmenu(self.root, menu_total)


    def setup_grating_default(self, frame:tk.Frame):
        """
        Set up the default gratings on main window.
        """

        self.grating_configs = {
            'max_display_x':200,
            'max_display_y':200,
            'file_path':'Images/Sample_Grating.png',
            'grating_name':'Sample_Grating.png',
            'g_type' : 'SawTooth',
            'g_angle' : 0,
            'y_max' : 255,
            'y_min' : 0,
            'period' : 100,
            'reverse' : 0
        }
        grating_preview_configs = {
            'max_display_x':200,
            'max_display_y':200,
            'file_image':'Images/Sample_Grating.png',
            'name_image':'Sample_Grating.png'
            
        }
        try:
            self.label_grating_title = tk.Label(frame,
            text='Grating Preview')
            self.label_grating_title.pack()
            self.grating_preview = MyImage(grating_preview_configs)
            self.label_grating = tk.Label(frame,
            image=self.grating_preview.original_tkinter)
            self.label_grating.pack()
        except NoFileError as e:
            e.advice = 'Place a new default grating in the correct directory.'
            super().error_window(e)
            return
    def update_list(self):
        self.list_box.delete(0, tk.END)
        for item in self.item_list:
            self.list_box.insert(tk.END, "%d: %s"%(self.item_list.index(item),item))


    def add_item(self):
        if len(self.item_list) < 4:
            self.collect_raw_data()
            self.item_details.update({
                'map_laser_power': self.map_laser_power
                })
            self.grating = MyGrating(self.grating_configs)
            item = ListItem(self.grating, self.item_details)
            self.item_list.append(item)
            self.update_list()
            
    def remove_item(self):
    
        index = self.list_box.curselection()
        
        if not len(index) == 0:
            index = index[0]
        
            self.list_box.delete(index)
            del self.item_list[index]
    
    def clear_items(self):
        self.list_box.delete(0, tk.END)
        self.item_list.clear()
    
    def fill_item_deatils(self,item):
        
        # Change grating, images and titles
        self.label_grating.configure(image=item.grating.grating_preview_tk)
        
        # Change info in Selection Details view
        self.grating_type_label.config(text = "Grating Type: %s" %(item.grating.configs['g_type']))
        if item.grating.configs['g_type'] == 'Custom':
            self.rotation_angle_label.config(text = "Rotation Angle: N/A")
            self.grating_name_label.config(text = "Grating Name: %s" %(item.grating.configs['grating_name']))
            self.y_min_label.config(text = "Y min: N/A")
            self.y_max_label.config(text = "Y max: N/A")
            self.period_label.config(text = "Period: N/A")
            self.reverse_label.config(text = "Reverse: N/A")
        else:
            self.grating_name_label.config(text = "Grating Name: N/A")
            self.rotation_angle_label.config(text = "Rotation Angle: %s" %(item.grating.configs['g_angle']))
            self.y_min_label.config(text = "Y min: %s" %(item.grating.configs['y_min']))
            self.y_max_label.config(text = "Y max: %s" %(item.grating.configs['y_max']))
            self.period_label.config(text = "Period: %s" %(item.grating.configs['period']))
            if item.grating.configs['reverse'] == 1:
                result = "Yes"
            else:
                result = "No"
            self.reverse_label.config(text = "Reverse: %s" %(result))
        # Change text boxes info
        self.text_laser.delete(1.0,tk.END)
        self.text_laser.insert(1.0, item.item_details['strings_laser'])
                
    def onselect(self, event):
            index = self.list_box.curselection()
            if not len(index) == 0:
                w = event.widget
                index = index[0]
                self.item = self.item_list[index]
                
                self.fill_item_deatils(self.item)
                

    def setup_list_view(self, frame:tk.Frame):
        
        self.list_box = tk.Listbox(frame, width=40)
        self.list_box.grid(row = 0, column= 0, columnspan=3)
        
        self.add_button = tk.Button(frame, text = 'Add', command = self.add_item)
        self.add_button.grid(row = 1, column = 0)

        self.add_button = tk.Button(frame, text = 'Remove', command = self.remove_item)
        self.add_button.grid(row = 1, column = 1)
        
        self.clear_list_button = tk.Button(frame, text = 'Clear List', command = self.clear_items)
        self.clear_list_button.grid(row = 1, column = 2)

        self.list_select = self.list_box.bind('<<ListboxSelect>>', lambda event: self.onselect(event))
    
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
        
        #Grating Type
        try:
            val = self.type_var.get().strip()
            if val != '':
                self.grating_configs['g_type'] = str(val)
            else:
                self.grating_configs['g_type'] = 'SawTooth'
        except ValueError as e:
            message = 'Grating type must be a string'
            raise InputError(message, e)
        
        if self.grating_configs['g_type'] == 'Custom':
            self.grating_configs['max_display_x'] = 1920
            self.grating_configs['max_display_x'] = 1152
            self.grating_configs['grating_name'] = self.grating_name
            self.grating_configs['file_path'] = self.grating_file_path
        else:
            #Rotation Angle
            try:
                #pdb.set_trace()
                val = self.entry_angle.get().strip()
                if val != '':
                    self.grating_configs['g_angle'] = int(val)
                else:
                    self.grating_configs['g_angle'] = 0
                    #pdb.set_trace()
            except ValueError as e:
                message = 'Rotation angle must be an int'
                raise InputError(message, e)

            #Ymin
            try:
                val = self.entry_ymin.get().strip()
                if val != '':
                    self.grating_configs['y_min'] = int(val)
                else:
                    self.grating_configs['y_min'] = 0
            except ValueError as e:
                message = 'Y min must be an int'
                raise InputError(message, e)

            #Ymax
            try:
                val = self.entry_ymax.get().strip()
                if val != '':
                    self.grating_configs['y_max'] = int(val)
                else:
                    self.grating_configs['y_max'] = 0
            except ValueError as e:
                message = 'Y max must be an int'
                raise InputError(message, e)

            #Period
            try:
                val = self.entry_period.get().strip()
                if val != '' or val > 0:
                    self.grating_configs['period'] = int(val)
                else:
                    self.grating_configs['period'] = 100
            except ValueError as e:
                message = 'Period width (pixels) must be an int greater than 0'
                raise InputError(message, e)
            self.grating_configs['reverse'] = self.g_reverse.get()
            
        self.strings_laser = self.text_laser.get(1.0, 'end-1c').strip()
       
        self.item_details = {
            'strings_laser':self.strings_laser
            }
    
    def write_experiment(self):
        """
        Get a file from the user and write experiment data there.
        """
        
        #Get file from user in dialogue box and write to files.
        self.file_experiment = ''
        while self.file_experiment == '':
            self.file_experiment = super().get_save_file()
        #Put all data in a dictionary for writing to file.
        datas = {}
        index = 1
        
        for item in self.item_list:
            item_dict = {'Strings Laser %d'%index: item.item_details['strings_laser'],
                    'Grating File %d'%index: item.grating.file_path,
                    'grating_type %d'%index: item.grating.configs['g_type']
                    }
            if item_dict['grating_type %d'%index] != 'Custom':
                item_dict.update(
                    {'rotation_angle %d'%index: item.grating.configs['g_angle'],
                    'y_min %d'%index: item.grating.configs['y_min'],
                    'y_max %d'%index: item.grating.configs['y_max'],
                    'period %d'%index: item.grating.configs['period'],
                    'reverse %d'%index: item.grating.configs['reverse']
                    })
            print(item_dict)
            datas.update(item_dict)
            index += 1
        
        
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

    def run_time(self):
        """
        Generate a rough runtime estimation and display on window.
        """
        # sum all exposure times together
        runtime = 10 # number of seconds for experiment 
        end_time = (datetime.now() + timedelta(seconds=run_time)).strftime('%H:%M:%S -- %d/%m/%Y')
        self.label_est_time.configure(text='End Time Estimate: '+end_time)
    
                    
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
            print("test")
            #Use simple threading to prevent laggy main window.
            x = threading.Thread(target=self.initialize_equipment)
            x.start()
            while x.is_alive():
                self.root.update()
                time.sleep(.25)
            x.join()
            #pdb.set_trace()
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
            #self.slm.close_window()
            #self.slm_thread.join()

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
        #pdb.set_trace()
        self.motor = Motor({**self.equipment_configs_motor,**{'Axes':(1,2)}})
        #pdb.set_trace()
        self.equipment.append(self.motor)
        self.shutter = Shutter(self.equipment_configs_shutter)
        self.equipment.append(self.shutter)
        self.laser = Laser(self.equipment_configs_laser)
        self.equipment.append(self.laser)
        
        #Initialize to start positions.
        self.motor.move_home(1) 
        self.motor.move_home(2) 
        self.laser.turn_on_off(True)

    def create_SLM_window(self):
        self.slm = SLM_window(self.root)

    def movement(self):
        """
        Conduct the physical movement of machinery and such.
        """
        # Create SLM Window
        self.create_SLM_window()
        '''
        #Move through the image array, expose according to mappings.
        prev_pix = None
        prev_powr = None
        y_after_crop = self.image.modified_PIL.height
        x_after_crop = self.image.modified_PIL.width
        
        for item in self.item_list:
            item.image_as_array = np.transpose(item.image.modified_array)

        for i in range(0, y_after_crop):
            on_this_row = False 
            for j in range(0, x_after_crop):
                self.check_pause_abort()
                cur_item = self.item_list[self.grating_map(j, i)]
                pix = cur_item.image_as_array[j][i]
                e_time = cur_item.map_timing[pix]
                if e_time < 0:
                    e_time = 0
                powr = cur_item.map_laser_power[pix]
                #Enter conditional if the current pixel should be exposed.
                if not super().compare_floats(e_time, 0):
                    self.slm.display(cur_item.grating.grating_tk)
                    self.update_progress(pix,e_time,powr,i,j)
                    #Change the laser's power if the pixel value has changed.
                    if prev_pix is not None and prev_powr is not None:
                        if not super().compare_floats(powr, prev_powr):
                            self.laser.change_power(powr)
                    #Move motors to the correct positions and open shutter.
                    if not on_this_row:
                        self.motor.move_absolute(2, i*self.delta_y*1000) 
                        on_this_row = True
                    self.motor.move_absolute(1, j*self.delta_x*1000) 
                    self.shutter.toggle(e_time)
                    #Update previous pixel info to current pixel info
                    prev_pix = pix
                    prev_powr = powr
                '''
    

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
        #screenshot = super().screenshot()
        #screenshot.save(self.file_experiment.replace('.txt','.png'))

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
            self.entry_angle,
            self.entry_ymin,
            self.entry_ymax,
            self.entry_period,
            self.text_laser
        ]
        self.clear_items()
        self.g_reverse.set('0')
        super().clear_wigits(wigits)
        
    def populate_main(self, datas:dict):
        """
        Fill wigits with datas from file.
        """
        
        #If data is not present, do not fill
        for i in range(1,5):
            
            if 'Strings Laser %d' %(i) in datas:
                self.text_laser.delete(1.0,tk.END)
                self.text_laser.insert(1.0, datas['Strings Laser %d' %(i)])
            if 'Grating File %d' %(i) in datas:
                self.grating_select(datas['Grating File %d' %(i)])
            if 'grating_type %d' %(i) in datas:
                self.type_var.set(datas['grating_type %d' %(i)])
            if 'rotation_angle %d' %(i) in datas:
                self.entry_angle.delete(0,tk.END)
                self.entry_angle.insert(0, datas['rotation_angle %d' %(i)])
            if 'y_min %d' %(i) in datas:
                self.entry_ymin.delete(0,tk.END)
                self.entry_ymin.insert(0, datas['y_min %d' %(i)])
            if 'y_max %d' %(i) in datas:
                self.entry_ymax.delete(0,tk.END)
                self.entry_ymax.insert(0, datas['y_max %d' %(i)])
            if 'period %d' %(i) in datas:
                self.entry_period.delete(0,tk.END)
                self.entry_period.insert(0, datas['period %d' %(i)])
            if 'reverse %d' %(i) in datas:
                self.g_reverse.set(datas['reverse %d' %(i)])
            self.add_item()
        
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