"""
pattern_start.py : Matthew Van Soelen
Description : Creates an instance of "Pattern Creator" 
			using implementation in pattern_gui.py and pattern_helper.py
			pattern_gui.py : Creates the GUI and manages the view
			pattern_helper : Contains implemention of some 
					helper classes for the view, and Pattern_Data 
					which manages creating and manipulating the data and images.
"""
# Tkinter Imports - GUI creation
from tkinter import *

# Import Gui creator
from pattern_gui import Pattern_GUI

# Import  custom helper classes for views and data controll
from pattern_helper import Toggled_Frame, ToolTip, Pattern_Data

root = Tk()
gui = Pattern_GUI(root=root)
root.mainloop()

def start_pattern_creator():
    root = Tk()
    gui = Pattern_GUI(root=root)
    root.mainloop()