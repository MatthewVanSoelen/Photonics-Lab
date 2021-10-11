
import threading
from slm_window import SLM_window
import time


from tkinter import * # Graphical User Interface (GUI) package

class SLM_Image():

    def __init__(self):
        self.master = Tk()
        self.create_gui()
        self.master.mainloop()

    def create_gui(self):
        begin_button = Button(self.master, text='Begin?', command=self.run_experiment)
        begin_button.pack()
        Checkbutton(self.master, text="check").pack()


    #def initialize_equipment(self):
     #   self.slm_thread = threading.Thread(target=self.create_SLM_window)
      #  self.slm_thread.start()

    def create_SLM_window(self):
        self.slm = SLM_window(self.master)

    def run_experiment(self):
        
        x = threading.Thread(target=self.movement)
        x.start()
        
        
        


    def movement(self):
        self.create_SLM_window()
        for x in range(5):
            time.sleep(2)
            print(x)
            self.slm.change_text("number:%s"%(str(x)))
        

def run():
    a = SLM_Image()
    # a.initialize_equipment()
    
    # self.window = SLM_window(self.master)
    
    # a.run_experiment()

run()