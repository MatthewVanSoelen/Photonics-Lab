
import tkinter as tk
from tkinter import *
import datetime
# import movement_amplified

class MyGUI:
    def __init__(self, window, pressed_button, pressed_home):
        self.window = window
        self.window.attributes('-fullscreen', False)
        self.window.title('Amplified Grated Creation')
        self.convert = convert_units
        self.motor_delay = 0.2 #(sec) time inbetween shutter close and stage move

        zero_time = str(datetime.timedelta(seconds=0.0)) # variable holding the value time 0:0:0

        '''
        distance_var, step_var, exposure_var:
            variables which hold values for their respectice text entries.

        Tkinters trace function on a StringVar object will call the update_time_estimation method 
        when a text entry changes

        '''
        self.distance_var = StringVar()
        self.distance_var.trace("w", lambda name, index, mode, distance_var=self.distance_var: self.update_time_estimation())

        self.step_var = StringVar()
        self.step_var.trace("w", lambda name, index, mode, step_var=self.step_var: self.update_time_estimation())

        self.exposure_var = StringVar()
        self.exposure_var.trace("w", lambda name, index, mode, exposure_var=self.exposure_var: self.update_time_estimation())

        self.button_text = StringVar()
        self.button_text.set("Begin Grating")

        self.shut_status = BooleanVar()
        self.shut_status.set(True)
        
        self.shut_connected = BooleanVar()
        self.shut_connected.set(True)
        self.shut_connected.trace("w", lambda name, index, mode, shut_connected=self.shut_connected: self.shutter_connection())

        self.unit_var = StringVar()
        self.unit_var.set("s")

        self.velocity = StringVar()
        self.velocity.trace("w", lambda name, index, mode, velocity=self.velocity: self.update_time_estimation())


        
        frame0 = tk.Frame(window)
        frame0.place(relx = 0.05, rely = 0.05, relwidth = 0.9, relheight = 0.1)

        frame1 = tk.Frame(window, borderwidth = 2,relief=SUNKEN) 
        frame1.place(relx = 0.05, rely = 0.15, relwidth = 0.6, relheight = 0.4)

        frame2 = tk.Frame(window)
        frame2.place(relx = 0.05, rely = 0.55, relwidth = 0.9, relheight = 0.2)

        option_frame = tk.Frame(window, borderwidth=1, relief=SUNKEN)
        option_frame.place(relx = 0.65, rely = 0.15, relwidth = 0.3, relheight = 0.4)

        self.exposure_label = tk.Label(frame1, text='Exposure time') # exposure time label
        self.exposure_time = tk.Entry(frame1, textvariable=self.exposure_var) #exposure time text field

        self.continuous = BooleanVar()
        self.continuous.set(False)
        self.continuous.trace("w", lambda name, index, mode, continuous=self.continuous: self.show_velocity())
        

        self.vel_label = tk.Label(frame1, text="Velocity: ")
        self.vel_entry = tk.Entry(frame1, textvariable=self.velocity)
        
        self.shut_cont = tk.Checkbutton(option_frame, text="Shutter Connected", variable=self.shut_connected)
        self.shut_cont.grid(row=0)

        self.shut_check = tk.Checkbutton(option_frame, text="Enable Shutter", variable=self.shut_status)
        self.shut_check.grid(row=1, column=0)

        self.continuous_check = tk.Checkbutton(option_frame, text="Continuous Movement", variable=self.continuous)
        self.continuous_check.grid(row=2, column=0)

        tk.Label(frame1, textvariable=self.unit_var).grid(row=2, column=3)

        

        '''
        Frame0: the top frame of MyGUI containing total time estimation, a spacer and starting time of the experiment
        '''

        

        # Total time estimation of the experiment 
        tk.Label(frame0, text="Estimated Time:").grid(row=0, column=0) # Estimated time Label 
        self.total_time = tk.Label(frame0, text=zero_time, bg="white", borderwidth=2,relief=SOLID) # Time display
        self.total_time.grid(row=0, column=1)
        
        self.show_velocity()
        
        # Spacer, by default columns within a grid have a width of zero. 
        # The Spacer is an empty Label giving the column a width of 2.
        spacer1 = tk.Label(frame0, text="", width=2)
        spacer1.grid(row=0, column=2) # the spacer is placed inbetween estimated time display and start time label


        #Start time of the experiment
        tk.Label(frame0, text="Started at: ").grid(row=0, column=3) # Start time Label
        self.start_time = tk.Label(frame0, text=zero_time, bg="white", borderwidth=2,relief=SOLID) # Start time display
        self.start_time.grid(row=0, column=4)

        

        '''
        frame1: the middle frame of MyGUI containing:
            total distance, step size, exposure time, dimensions of film, unit drop downs, and begin/abort experiment button
        '''

        

        tk.Label(frame1, text='Total Distance').grid(row=0) # Total distance label
        self.total_distance = tk.Entry(frame1, textvariable=self.distance_var) # distance text field 
        self.total_distance.grid(row=0, column=1)  

        tk.Label(frame1, text='Step size').grid(row=1) # step size label
        self.step_size = tk.Entry(frame1, textvariable=self.step_var) # step size text field
        self.step_size.grid(row=1, column=1)

        

        tk.Label(frame1, text='Dimesions of film: (Width,Height)').grid(row=3) # film dimensions
        self.entry_dimentions = tk.Entry(frame1) # film dimensions text field
        self.entry_dimentions.grid(row=3, column=1)
        self.entry_dimentions.insert(0,"(10,10)")


        tk.Label(frame1, text='(mm)').grid(row=3, column=3) # film dimension units

        

        '''
        Unit Drop Down Menus
        '''
        self.choices = {'mili','micro','nano'} # options for the drop down menu

        self.distance_dropdown = tk.StringVar(frame1) # string var that holds the distance unit
        self.distance_dropdown.trace("w", lambda name, index, mode, distance_dropdown=self.distance_dropdown: self.update_time_estimation())
        self.distance_dropdown.set('mirco') # sets mirco as the default unit
        self.popup_menu = tk.OptionMenu(frame1, self.distance_dropdown, *self.choices) # sets up the unit option menu
        self.popup_menu.grid(row = 0, column = 3)

        self.step_dropdown = tk.StringVar(frame1) # string var that holds the step size unit
        self.step_dropdown.trace("w", lambda name, index, mode, step_dropdown=self.step_dropdown: self.update_time_estimation())
        self.step_dropdown.set('mirco') # sets micro as the default unit       
        self.popup_menu = tk.OptionMenu(frame1, self.step_dropdown, *self.choices) # sets up the unit option menu
        self.popup_menu.grid(row = 1, column = 3)

        # def change_dropdown(*args):
        #     print(self.distance_dropdown.get())
        #     self.distance_dropdown.trace('w', change_dropdown)
        

        '''
        Frame2: the bottom frame of MyGUI, includes the text entry for the serial number of the motor
        '''
        
        tk.Label(frame2, text='Serial Ports', font='Helvetica 18 bold').grid(row=0,column=0)
        tk.Label(frame2, text='Motor port #:').grid(row='1', column='0')
        tk.Label(frame2, text='Shutter port #:').grid(row='2', column='0')
        self.entry_port_mot = tk.Entry(frame2, width = 10)
        self.entry_port_mot.grid(row=1,column=1)
        self.entry_port_mot.insert(1, 1)

        self.entry_port_shut = tk.Entry(frame2, width = 10)
        self.entry_port_shut.grid(row=2,column=1)
        self.entry_port_shut.insert(1, 3)

        self.update_time_estimation() # calls update_time_estimation() 

        # begin/abort button initialized at the end when all varibles are decalred.
        self.begin_button = Button(frame1, textvariable=self.button_text, height=2, width=12, command=pressed_button)
        self.begin_button.grid(row=4, column=0)

        self.home_button = Button(option_frame, text="Go Home", command=pressed_home)
        self.home_button.grid(row = 3, column=0)


    def estimate_time(self):
        try:
            if (not self.continuous.get()):
                total_distance = float(convert_units(self.distance_var.get(),self.distance_dropdown.get()))
                step_size = float(convert_units(self.step_var.get(),self.step_dropdown.get()))
                exposure_time = float(self.exposure_var.get())
                experiment_time = (total_distance/step_size) * exposure_time
                return float(experiment_time)
            else:
                total_distance = float(convert_units(self.distance_var.get(),self.distance_dropdown.get()))
                velocity = float(self.velocity.get())
                experiment_time = total_distance / velocity
                return float(experiment_time)
        except:
            return float(0.0)


    def update_time_estimation(self):
        if self.total_time is not None :
            total_time = str(datetime.timedelta(seconds=self.estimate_time()))
            self.total_time.configure(text=total_time)
            
            # self.window.after(2000, self.update_time_estimation)

    def show_velocity(self):
        self.update_time_estimation()        
        if self.continuous.get():
            self.exposure_label.grid_forget()
            self.exposure_time.grid_forget()
            self.vel_label.grid(row=2)
            self.vel_entry.grid(row=2, column=1)
            self.unit_var.set("mm/s")
            self.shut_status.set(False)
        else:
            self.vel_label.grid_forget()
            self.vel_entry.grid_forget()
            self.exposure_label.grid(row=2)
            self.exposure_time.grid(row=2, column=1)
            self.unit_var.set("s")
            

    def shutter_connection(self):
        if self.shut_connected.get():
            self.shut_check.config(state="normal")
        else:
            self.shut_status.set(False)
            self.shut_check.config(state="disabled")

    

def convert_units(value, unit):
        value = float(value)
        result = -1
        if unit == "mili":
            result = value / 1.0 #converts mili to mili        
        elif unit == "nano":
            result = value / 1000000.0 #converts nano to mili
        else:
            result = value / 1000.0 #converts micro to mili

        #converts to milimeters, which is the unit the E-873 controller uses
        return result

        