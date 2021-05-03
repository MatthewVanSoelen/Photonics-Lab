"""
A runner program which can run one of several GUI classes to run experiment.

@author: Matthew Van Soelen

Special thanks to Daniel Stolz, Luke Kurlanski, and Dr. David McGee.

Read the Program Guide for detailed information about this program.
"""

import tkinter as tk

from app import App
from doe_app import DOE_App

def doe_app():
    root.destroy()
    new_root = tk.Tk()
    app = DOE_App(new_root)
    app.root.mainloop()

root = tk.Tk()
configs = {
    'Window Title':'Hologram Creator -- '
            + 'Copyright 2019, Matthew Van Soelen and Luke Kurlandski, all rights reserved',
    'Window Width':300,
    'Window Height':300
}
chooser = App(root, configs)
tk.Label(chooser.root, text='Select an Experiment').pack()
button_doe_app = tk.Button(chooser.root, text='DOE Creator', 
    command=doe_app)
button_doe_app.pack()

root.mainloop()