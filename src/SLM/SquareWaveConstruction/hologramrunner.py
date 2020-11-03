"""
A runner program which can run one of several GUI classes to run experiment.

@author: Matthew Van Soelen

Special thanks to Daniel Stolz, Luke Kurlanski, and Dr. David McGee.

Read the Program Guide for detailed information about this program.
"""

import tkinter as tk

from app import App
from sawtooth_hixel import Sawtooth_Hixel

def sawtooth_hixel():
    root.destroy()
    new_root = tk.Tk()
    app = Sawtooth_Hixel(new_root)
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
button_sawtooth_hixel = tk.Button(chooser.root, text='Sawtooth Hixel', 
    command=sawtooth_hixel)
button_sawtooth_hixel.pack()

root.mainloop()