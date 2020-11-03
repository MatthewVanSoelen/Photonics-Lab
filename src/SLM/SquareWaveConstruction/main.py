import tkinter as tk

# from app import App
from sawtooth_hixel import Sawtooth_Hixel

class App_Selector:
    def __init__(self, root:tk.Tk, configs:dict):

        #Create the base root and determine screen dimentions.
        self.root = root
        self.configs = configs
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        window_title = (self.configs['Window Title'] if 'Window Title' 
            in self.configs else 'App')
        self.root.title(window_title)
        self.root.config()
        #Reconfigure size of window if nessecary and center.
        if 'Window Width' not in self.configs and 'Window Height' not in self.configs:
            return
        window_width = (self.configs['Window Width'] if 'Window Width' 
            in self.configs else 400)
        window_height = (self.configs['Window Height'] if 'Window Height' 
            in self.configs else 400)
        shift_x = self.configs['Shift x'] if 'Shift x' in self.configs else 0
        shift_y = self.configs['Shift y'] if 'Shift y' in self.configs else 0 
        #Place the root in center of screen then displace as needed.
        x = int((self.screen_width/2) - (window_width/2))
        y = int((self.screen_height/2) - (window_height/2))
        self.root.geometry("{}x{}+{}+{}".format(window_width, window_height, 
            x+shift_x, y+shift_y))

        self.setup_options()

    def setup_options(self):
        tk.Label(self.root, text='Select an Experiment').pack()

        button_sawtooth_hixel = tk.Button(self.root, text='Sawtooth_Hixel', command=self.sawtooth_hixel)
        button_sawtooth_hixel.pack()

    def sawtooth_hixel(self):
        print("Sawtooth_Hixel")
        self.root.destroy()
        new_root = tk.Tk()
        
        app = Sawtooth_Hixel(new_root, self.configs)
        app.root.mainloop()

root = tk.Tk()
configs = {
    'Window Title':'SLM Sawtooth Hixel -- '
            + 'Copyright 2020 Matthew Van Soelen, all rights reserved',
    'Window Width':300,
    'Window Height':300
}

chooser = App_Selector(root, configs)


root.mainloop()