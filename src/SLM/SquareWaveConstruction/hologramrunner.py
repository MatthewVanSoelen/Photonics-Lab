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
from singleimage import SingleImage
from slm_image import SLM_Image
from slm_single_image import SLM_Single_Image

def single_image():
    root.destroy()
    new_root = tk.Tk()
    app = SingleImage(new_root)
    app.root.mainloop()

def slm_image():
    root.destroy()
    new_root = tk.Tk()
    app = SLM_Image(new_root)
    app.root.mainloop()
    
def slm_single_image():
    root.destroy()
    new_root = tk.Tk()
    app = SLM_Single_Image(new_root)
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
button_singleimage = tk.Button(chooser.root, text='Single Image', 
    command=single_image)
button_singleimage.pack()

button_slm_image = tk.Button(chooser.root, text='SLM Merge Image', command=slm_image)
button_slm_image.pack(pady=20)

button_slm_image = tk.Button(chooser.root, text='SLM Single Image', command=slm_single_image)
button_slm_image.pack()

root.mainloop()