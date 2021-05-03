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
import os
import json

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
from pattern_item import PatternItem 
from slm_window import SLM_window
import pdb

class DOE_App(HologramCreator):

    def __init__(self, root: tk.Tk):
        """
        Constructor call with parent constructor.
        """

        #Create a root with HologramCreator, the parent.
        window_configs = {
            'Window Title':'DOE Creator',
            'Frames Vertical':4,
            'Frames Horizontal':5
        }
        super().__init__(root, window_configs)
        self.item_list = []
        self.list_box = None
        self.item_len = 2
        self.slm = None
        self.grating_name = None
        self.grating_file_path = None
        
        #Apply some frame modifications for large wigits.
        self.frames[1][2].grid(row=1, column=2, pady=10, rowspan=200,  sticky='NW')
        self.frames[2][2].grid(row=2, column=2, pady=10, rowspan=200,  sticky='W')
        self.frames[0][3].grid(row=0, column=3, pady=10, rowspan=200,  sticky='NW', padx=10)
        self.frames[0][4].grid(row=0, column=4, pady=10, rowspan=200,  sticky='NE', padx=10)
      
        super().setup_initialize_experiment(self.frames[0][0])
        super().setup_while_running(self.frames[2][0])
        super().setup_grating_options(self.frames[1][0])
    
        super().setup_experiment_details_view(self.frames[2][1])

        #Setup main window with Sawtooth_Hixel, the self.
        self.setup_menu()
        self.setup_list_view(self.frames[1][1])
        self.setup_grating_default(self.frames[0][1])
        
        

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

        self.experiment_configs = {
            'max_display_x':200,
            'max_display_y':200,
            'file_path':'Images/Sample_Grating.png',
            'grating_name':'Sample_Grating.png',
            'g_type' : 'SawTooth',
            'g_angle' : 0,
            'y_max' : 255,
            'y_min' : 0,
            'period' : 100,
            'reverse' : 0, 
            'exp_time' : 0
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
            self.label_grating = tk.Label(frame)
            self.label_grating.pack()
            folder_path = os.path.abspath(os.getcwd())
            folder_path = os.path.join(folder_path, "Images/Sample")
            self.pattern_folder_select(folder_path)
            # pdb.set_trace()
            self.list_box.activate(0)
        except NoFileError as e:
            e.advice = 'Place a new default grating in the correct directory.'
            super().error_window(e)
            return
    def update_list(self):
        self.list_box.delete(0, tk.END)
        for item in self.item_list:
            self.list_box.insert(tk.END, "%d: %s"%(self.item_list.index(item),item))
            
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
        self.label_grating.configure(image=item.tk_preview_image)
        
        # Change info in Selection Details view
        freq = np.around(item.frequency, 2)
        angle = np.around(item.angle, 2)
        self.folder_name_label.config(text = "Folder Name: %s" %(item.folder_name))
        self.file_name_label.config(text = "File Name: %s" %(item.file_name))
        self.id_label.config(text = "id_label: %s"%(item.id_num))
        self.x_label.config(text = "X: %s" %(item.x_pos))
        self.y_label.config(text = "Y: %s" %(item.y_pos))
        self.freq_label.config(text = "Frequency: %s" %(freq))
        self.angle_label.config(text = "Angle: %s" %(angle))
        self.amplitude_label.config(text = "Amplitude: %s" %(item.amplitude))
        
                
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
        
        self.add_button = tk.Button(frame, text = 'Upload Patterns', command = self.pattern_folder_select)
        self.add_button.grid(row = 1, column = 0)

        self.add_button = tk.Button(frame, text = 'Remove', command = self.remove_item)
        self.add_button.grid(row = 1, column = 1)
        
        self.clear_list_button = tk.Button(frame, text = 'Clear List', command = self.clear_items)
        self.clear_list_button.grid(row = 1, column = 2)

        self.list_select = self.list_box.bind('<<ListboxSelect>>', lambda event: self.onselect(event))
    
    def pattern_folder_select(self, folder_path=None):
        """
        Select an image from a file dialogue box and update on screen.
        """
        # pdb.set_trace()
        if folder_path is None:
            self.pattern_folder_path = filedialog.askdirectory(initialdir='Images',title="Select Grating Folder")
        else:
            self.pattern_folder_path = folder_path
            
        self.clear_items()

        data_file_path = os.path.join(self.pattern_folder_path, "data.json")
        with open(data_file_path,) as data_file:
            self.pattern_dict = json.load(data_file)

        for key in self.pattern_dict:
            image_name = self.pattern_dict[key]['file_name']
            img_file_path = os.path.join(self.pattern_folder_path, image_name)
            pattern_image = Image.open(img_file_path).convert('L')
            item = PatternItem(
                file_name= image_name, 
                folder_path= self.pattern_folder_path, 
                id_num= key, 
                x_pos= self.pattern_dict[key]['x'], 
                y_pos= self.pattern_dict[key]['y'], 
                angle= self.pattern_dict[key]['angle'], 
                frequency= self.pattern_dict[key]['freq'], 
                amplitude= self.pattern_dict[key]['value'], 
                image= pattern_image)
            self.item_list.append(item)
            self.update_list()


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
        '''self.modify_and_map()'''
        #Generate a time estimation
        self.run_time()

##############################################################################
# Data Processing Worker Functions
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
        #Exposure Time 
        try: 
            val = self.entry_exp_time.get().replace(" ","")
            if val != '':
                self.experiment_configs['exp_time'] = float(val)
            else:
                self.experiment_configs['exp_time'] = 0
        except ValueError as e:
            message = 'Exposure Time must be a Decimal Value'
            
        #Laser Power
        try:
            val = self.entry_laser_power.get().replace(" ","")
            if len(val) > 0 and float(val) > -1:
                self.experiment_configs['laser_power'] = float(val)
            else:
                self.experiment_configs['laser_power'] = 0.0
        except ValueError as e:
            message = 'Laser power must be an integer greater than -1'
            raise InputError(message, e)

        #Vertical Step Size
        try: 
            val = self.entry_ver_step.get().replace(" ","")
            if val != '':
                self.experiment_configs['ver_step_size'] = float(val)
            else:
                self.experiment_configs['ver_step_size'] = 0
        except ValueError as e:
            message = 'Vertical Step Size must be an integer greater than -1'

        #Horizontal Step Size
        try: 
            val = self.entry_hor_step.get().replace(" ","")
            if val != '':
                self.experiment_configs['hor_step_size'] = float(val)
            else:
                self.experiment_configs['hor_step_size'] = 0
        except ValueError as e:
            message = 'Horizontal Step Size must be an integer greater than -1'
       
    
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
        grating_options = {
                'exp_time': self.experiment_configs['exp_time'],
                'laser_power': self.experiment_configs['laser_power'],
                'ver_step_size': self.experiment_configs['ver_step_size'],
                'hor_step_size': self.experiment_configs['hor_step_size'],
                }
        datas.update(grating_options)
        datas["pattern_folder_path"] = self.pattern_folder_path
        
        
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
        run_time = 0 # number of seconds for experiment 
        for item in self.item_list:
            run_time += self.experiment_configs['exp_time']
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
        '''
        try:
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
        '''
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
            ''' super().close_ports(self.equipment)
            super().error_window(e) '''
            return
        ''' except EquipmentError as e:
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
        '''
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
        Loop through gratings for single pixel,
        expose pixel with approriate time and grating.
        """
        # Create SLM Window
        print("movement")
        self.create_SLM_window()
        items = self.map_items(self.item_list)
        powr = self.experiment_configs['laser_power']
        e_time = self.experiment_configs['exp_time']
        delta_x = self.experiment_configs['hor_step_size']
        delta_y = self.experiment_configs['ver_step_size']
        if e_time < 0:
            e_time = 0
        # prev_powr = powr
        for x, row in enumerate(items):
            for y, item in enumerate(row):
                if item is not None:
                    self.check_pause_abort()
                    self.slm.display(item.image_tk)
                    print("step_x: %s"%(x*delta_x*1000))
                    # self.motor.move_absolute(1, x*delta_x*1000)
                    time.sleep(e_time)
                    # self.shutter.toggle(e_time)
            print("step_y: %s"%(y*delta_y*1000))
            # self.motor.move_absolute(2, y*delta_y*1000)
        self.slm.close_window()

    def map_items(self, item_list):

        items = item_list
        dim = int((np.ceil(np.sqrt(len(items)))).astype(int))
        pad_r = dim**2 - len(items)
        print(dim, pad_r, items, len(items), items[0])
        print(type(pad_r))
        items = np.pad(items, (0, pad_r), mode='constant', constant_values=items[0])
        items = np.reshape(items, (dim,dim), order="C")
        return items
            

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
        # pdb.set_trace()
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
            self.entry_exp_time,
            self.entry_laser_power
        ]
        self.clear_items()
        super().clear_wigits(wigits)
        
    def populate_main(self, datas:dict):
        """
        Fill wigits with datas from file.
        """
        # print(datas)
        #If data is not present, do not fill
        if 'pattern_folder_path' in datas:
            self.pattern_folder_select(datas['pattern_folder_path'])

        if 'laser_power' in datas:
            self.entry_laser_power.delete(0,tk.END)
            self.entry_laser_power.insert(0, datas['laser_power'])
            
        if 'exp_time'in datas:
            self.entry_exp_time.delete(0,tk.END)
            self.entry_exp_time.insert(0, datas['exp_time'])
            
        if 'ver_step_size'in datas:
            self.entry_ver_step.delete(0,tk.END)
            self.entry_ver_step.insert(0, datas['ver_step_size'])
            
        if 'hor_step_size'in datas:
            self.entry_hor_step.delete(0,tk.END)
            self.entry_hor_step.insert(0, datas['hor_step_size'])
            

        
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
            if 'LASER' in KEY and 'laser_power' != KEY: 
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