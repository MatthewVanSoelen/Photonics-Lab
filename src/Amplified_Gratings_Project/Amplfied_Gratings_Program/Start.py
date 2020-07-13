import tkinter
import create_amplified
import time
import datetime
import threading
import movement_amplified
import testingThreading

class Experiment:
    def __init__(self, total_distance=None, step_size=None, exposure_time=None, port_mot=None, port_shut=None,shut_status=None, shut_connected=None, motor_delay=None, continuous=None, velocity=None, width_film=None, height_film=None):
        self.total_distance = total_distance
        self.step_size = step_size
        self.exposure_time = exposure_time
        self.port_mot = port_mot
        self.port_shut = port_shut
        self.shut_status = shut_status
        self.shut_connected = shut_connected
        self.motor_delay = motor_delay
        self.continuous = continuous
        self.velocity = velocity
        self.max_velocity = float(10.0)
        self.width_film = width_film
        self.height_film = height_film
        self.finished = True
        self.stop_check = 1 # The number of seconds inbetween checking whether the motor should stop.

class RunApp:
    """
    Launches the GUI and creates a thread for which the experiment can be run asychnolodly from the GUI.
    RunApp cordinates running and an experiment with the GUI.
    """
    def __init__(self, window):
        """
        Starts the GUI passing it the tkinter window and the press button function,
        so the GUI can trigger the pressed button function within the RunApp class.
        Initilizes the begin_experiement var to False.
        Defines experiment_thread with a target to run the worker_thread() function.
        """
        self.window = window
        
        self.info = Experiment()
        
        
        self.gui = create_amplified.MyGUI(window, pressed_button=self.pressed_button, pressed_home=self.pressed_home)
        
        self.begin_experiment = False
        self.run_experiment = movement_amplified.run_experiment
        self.go_home = movement_amplified.go_home
        #self.go_home = testingThreading.go_home
        
        self.run_experiment = testingThreading.run_experiment

        self.experiment_thread = threading.Thread(target=self.worker_thread)


    def worker_thread(self):
        """
        Runs experiment inside experiment_thread.
        Once finished sets begin_experiment to true and changes text on button.
        Then updates the start time.
        """

        self.run_experiment(self,self.info)
        self.begin_experiment = False
        self.gui.button_text.set("Begin Experiment")
        self.update_start_time()
        print("Finished experiment")

    def run(self):
        '''
        Collects total_distance, step_size, exposure_time, motor port number, and film dimensions from the GUI.
        if not all fields are filled out then the try will fail and the experiment will not run.
        '''
        try:
            self.info.continuous = self.gui.continuous.get()
            self.info.shut_connected = self.gui.shut_connected.get()

            entry_dimentions = str(self.gui.entry_dimentions.get())
            entry_dimentions = entry_dimentions.replace("(", "")
            entry_dimentions = entry_dimentions.replace(")", "")
            entry_dimentions = entry_dimentions.split(",")
            self.info.width_film = float(entry_dimentions[0].strip())
            self.info.height_film = float(entry_dimentions[1].strip())
            
            if not self.info.continuous:
                self.info.step_size = float(self.gui.convert(self.gui.step_var.get(),self.gui.step_dropdown.get()))
                self.info.exposure_time = float(self.gui.exposure_var.get())
                self.info.motor_delay = self.gui.motor_delay
            else:
                self.info.velocity = float(self.gui.velocity.get())

            self.info.total_distance = float(self.gui.convert(self.gui.distance_var.get(),self.gui.distance_dropdown.get()))
            self.info.port_mot = str(self.gui.entry_port_mot.get())
            self.info.port_shut = str(self.gui.entry_port_shut.get())
            self.info.shut_status = self.gui.shut_status.get()
                
            # Start the experiment in experiment thread only if the thread is already not running
            print(self.experiment_thread)
            if not self.experiment_thread.isAlive(): 
                print("Experiment started")
                self.begin_experiment = True
                self.gui.button_text.set("Abort Experiment")
                self.update_start_time()
                self.experiment_thread = threading.Thread(target=self.worker_thread)
                self.experiment_thread.start()
        except:
            print("failed to start experiment")

    def stop_experiment(self):
        self.begin_experiment = False
        self.gui.button_text.set("Begin Experiment")
        self.update_start_time()

    def pressed_home(self):
        self.go_home(self,self.info)

    def pressed_button(self): # button press: if (begin_experiment) stop experiment else run experiment
        self.stop_experiment() if self.begin_experiment else self.run()
        
    def update_start_time(self):
        if self.begin_experiment:
            start_time = str(time.strftime("%H:%M:%S"))
            self.gui.start_time.configure(text=start_time)
        else:
            self.gui.start_time.configure(text=str(datetime.timedelta(seconds=0.0)))


HEIGHT = 400
WIDTH = 800

window = tkinter.Tk()
window.title("Amplified Gratings")
window.minsize(WIDTH, HEIGHT)

client = RunApp(window)
window.mainloop()


