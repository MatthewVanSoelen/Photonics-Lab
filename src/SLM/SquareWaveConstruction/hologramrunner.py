"""
A runner program which can run one of several GUI classes to run experiment.

@author: Luke Kurlandski
@date: December 2019
@copyright: Copyright 2019, Luke Kurlandski, all rights reserved

Special thanks to Daniel Stolz, Matthew Van Soelen, and Dr. David McGee.

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
            + 'Copyright 2019, Luke Kurlandski and Matthew Van Soelen, all rights reserved',
    'Window Width':300,
    'Window Height':300
}
chooser = App(root, configs)
tk.Label(chooser.root, text='Select an Experiment').pack()
button_sawtooth_hixel = tk.Button(chooser.root, text='Sawtooth Hixel', 
    command=sawtooth_hixel)
button_sawtooth_hixel.pack()

root.mainloop()