"""
Create any generic tkinter app.

@author: Luke Kurlandski
@date: December 2019
@copyright: Copyright 2019, Luke Kurlandski, all rights reserved

Special thanks to Daniel Stolz, Matthew Van Soelen, and Dr. David McGee.

Read the Program Guide for detailed information about this program.
"""

import tkinter as tk
from PIL import ImageGrab
from tkinter import filedialog

from exceptions import MyError

class App: 

    def __init__(self, root:tk.Tk, configs:dict):
        """
        Create an tkinter main app.
        """
        
        #Create the base root and determine screen dimentions.
        self.root = root
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        window_title = (configs['Window Title'] if 'Window Title' 
            in configs else 'App')
        self.root.title(window_title)
        self.root.config(bg='gainsboro')
        #Reconfigure size of window if nessecary and center.
        if 'Window Width' not in configs and 'Window Height' not in configs:
            return
        window_width = (configs['Window Width'] if 'Window Width' 
            in configs else 400)
        window_height = (configs['Window Height'] if 'Window Height' 
            in configs else 400)
        shift_x = configs['Shift x'] if 'Shift x' in configs else 0
        shift_y = configs['Shift y'] if 'Shift y' in configs else 0 
        #Place the root in center of screen then displace as needed.
        x = int((self.screen_width/2) - (window_width/2))
        y = int((self.screen_height/2) - (window_height/2))
        self.root.geometry("{}x{}+{}+{}".format(window_width, window_height, 
            x+shift_x, y+shift_y))

##############################################################################
#SubFrames
##############################################################################

    def create_frames(self, window, configs:dict):
        """
        Create a set of frames for the main window.
        Returns:
            frames : list[list[tk.Frame]] : a list of frames
        """

        #Data from arguments.
        horizontal = (configs['Frames Horizontal'] if 'Frames Horizontal' 
            in configs else 0)
        vertical = (configs['Frames Vertical'] if 'Frames Vertical' 
            in configs else 0)
        #Create 2D list of frames and grid.
        frames = []
        for i in range (0, vertical):
            temp = []
            frames.append(temp)
            for j in range (0, horizontal):
                frame = tk.Frame(window)
                frame.grid(row = i, column = j, pady = 10)
                temp.append(frame)
        return frames

##############################################################################
#Menu Creation
##############################################################################

    def create_menu(self, window, configs:dict):
        """
        Create a menu with labels and commands specified by dictionary.
        Arguments: 
            configs : dict{str:function} : label-command pairs for menu
        Returns:
            menu : tk.Menu : the menu with functional buttons
        """

        menu = tk.Menu()
        window.config(menu=menu)
        for pair in configs.items():
            menu.add_command(label=pair[0], command=pair[1])
        return menu

    def create_mainmenu(self, window, configs:dict):
        """
        Create a menu of submenus, based upon a dict of dicts.
        Arguments:
            configs : dict{str:dict{str:function}} : label-submenu pairs
        Returns:
            menu_main : tk.Menu : the main menu containing submenues
        """

        #Create the main menu.
        menu_main = self.create_menu(window, {})
        window.config(menu=menu_main)
        #Take every sub dictionary and create a submenu out of it.
        for submenu_pair in configs.items():
            self.create_submenu(menu_main, submenu_pair[0], submenu_pair[1])
        return menu_main

    def create_submenu(self, menu:tk.Menu, submenu_name:str, configs:dict):
        """
        Create a submenu with labels and commands attatched to a menu.
        Arguments: 
            configs : dict{str:function} : label-command pairs for submenu
        Returns:
            submenu : tk.Menu : the submenu, added as a cascade to menu
        """

        submenu = tk.Menu(menu)
        menu.add_cascade(label=submenu_name, menu=submenu)
        for pair in configs.items():
            submenu.add_command(label=pair[0], command=pair[1])
        return submenu

    def close_help_menu(self, window, file_help:str): 
        """
        Create a menu on the desired window with a close and help button.
        Returns:
            menu : tk.Menu : the menu with 'Close' and 'Help' buttons
        """

        commands = {
            'Close':window.destroy,
            'Help':lambda:self.help_window(file_help)
        }
        menu = self.create_menu(window, commands)
        return menu

##############################################################################
#Popup Windows
##############################################################################

    def popup_window(self, window, configs:dict):
        """
        Create a popup window based on a window, centered on screen.
        Returns:
            window_popup : tk.Toplevel : the popup window
        """

        #Data from arguments.
        window_width = (configs['Window Width'] if 'Window Width' 
            in configs else 200)
        window_height = (configs['Window Height'] if 'Window Height' 
            in configs else 200)
        window_title = (configs['Window Title'] if 'Window Title'
            in configs else 'Popup Window')
        shift_x = configs['Shift x'] if 'Shift x' in configs else 0
        shift_y = configs['Shift y'] if 'Shift y' in configs else 0  
        #Create popup window, center on screen. 
        window_popup = tk.Toplevel(window) 
        window_popup.title(window_title)
        x = int((self.screen_width/2) - (window_width/2))
        y = int((self.screen_height/2) - (window_height/2))
        window_popup.geometry("{}x{}+{}+{}".format(window_width, window_height,
            x+shift_x, y+shift_y))
        return window_popup

    def help_window(self, file_name:str): 
        """
        Create a popup window displaying helpful information from file_name.
        Returns:
            window_help : tk.Toplevel : the help window with information
        """
        
        def help_save(): 
            """
            Alters the text file in storage.
            """
            try:
                with open(file_name, 'w') as file:
                    file.write(text.get(1.0, 'end-1c'))
            except Exception:
                pass
                    
        #Configure the help window.
        window_configs = {
            'Window Width':600, 
            'Window Height':600, 
            'Window Title':'Help'
        }
        window_help = self.popup_window(self.root, window_configs)
        menu = self.close_help_menu(window_help, 'Help/Help.txt')
        menu.add_command(label='Save Changes', command=help_save)
        text, frame = self.text_fill_window(window_help, True)
        #Fill the textbox with the text from file.
        try:
            with open(file_name, 'r') as file:
                text.insert(tk.END, file.read())
        except FileNotFoundError:
            text.insert(tk.END, 'Sorry, could not locate this file:\n\t'
                + file_name + '\nMost likely, not module has been written.')
        return window_help
            
    def error_window(self, exception:MyError): 
        """
        Display a popup window containing information from MyError object.
        Returns:
            window_error : tk.Toplevel : the error window with information
        """
        
        #Configure the help window.
        window_configs = {
            'Window Width':400, 
            'Window Height':400, 
            'Window Title':'An Error Has Occurred'
        }
        window_error = self.popup_window(self.root, window_configs)
        self.close_help_menu(window_error, 'Help/Exceptions.txt')
        text, frame = self.text_fill_window(window_error, True)
        #Insert the error message
        text.insert(tk.END, 'Exception Type:\n' + str(type(exception))
            + '\n\nAuthor\'s Message:\n' + exception.message
                + '\n\nAdvice:\n' + str(exception.advice)
                    + '\n\nPython\'s Message:\n' + str(exception))
        return window_error

##############################################################################
#Text Wigit Manipulation
##############################################################################

    def text_apply_scrollbars(self, window, configs:dict):
        """
        Apply scrollbars to a Text wigit.
        Returns:
            text : tk.Text : the text wigit with scrollbars
        """

        #Data from arguments.
        frame = configs['Frame']
        text = configs['Text'] if 'Text' in configs else tk.Text(frame)
        apply_x = configs['Apply x'] if 'Apply x' in configs else True
        apply_y = configs['Apply y'] if 'Apply y' in configs else True
        y_row = configs['y Row'] if 'y Row' in configs else 0
        y_col = configs['y Col'] if 'y Col' in configs else 1
        x_row = configs['x Row'] if 'x Row' in configs else 1
        x_col = configs['x Col'] if 'x Col' in configs else 0
        #Apply the scrollbars in horizontal and vertical directions.
        if apply_x:
            scrollbar_x = tk.Scrollbar(frame, orient=tk.HORIZONTAL, 
                command=text.xview)
            scrollbar_x.grid(row=x_row, column=x_col, sticky=tk.W+tk.E)
            text.configure(xscrollcommand=scrollbar_x.set, wrap=tk.NONE)
        if apply_y:
            scrollbar_y = tk.Scrollbar(frame, orient=tk.VERTICAL, 
                command = text.yview)
            scrollbar_y.grid(row=y_row, column=y_col, sticky=tk.N+tk.S)
            text.configure(yscrollcommand=scrollbar_y.set)
        return text

    def text_fill_window(self, window, scrollbars:bool): 
        """
        Create a Text wigit that fills window, can have scrollbars.
        Returns:
            text : tk.Text : the text wigit with scrollbars, sticky to screen
            frame : tk.Frame : a frame, packed, the text wigit lives in
        """

        frame = tk.Frame(window)
        frame.pack(fill=tk.BOTH, expand=True)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        text = tk.Text(frame)
        text.grid(sticky=tk.N+tk.S+tk.E+tk.W)
        text_configs = {
            'Frame':frame, 
            'Text':text
        }
        if scrollbars:
            self.text_apply_scrollbars(window, text_configs)
        return text, frame

##############################################################################
#Other
##############################################################################

    def clear_wigits(self, wigits:list):
        """
        Clear input from a variety of wgitis.
        """

        for wigit in wigits:
            if isinstance(wigit, tk.Entry):
                wigit.delete(0, tk.END)
            elif isinstance(wigit, tk.Text):
                wigit.delete(1.0, tk.END)
            else:
                #This is an unkown wigit.
                pass
            
    def screenshot(self):
        """
        Take a screenshot of the main window and return.
        """
        
        self.root.update()
        x1 = self.root.winfo_x()
        y1 = self.root.winfo_x()
        x2 = self.root.winfo_width()
        y2 = self.root.winfo_height()
        return ImageGrab.grab((x1,y1,x2,y2))

    def get_save_file(self):
        """
        Get the save file from the user with file dialogue box.
        Returns:
            file : str : the file user selected from dialogue box
        """
        
        file = filedialog.asksaveasfilename(defaultextension='.txt',
            initialdir='Experiments', title='Save Experiment As', 
                filetypes=(("txt files","*.txt"),("All Files","*.*")))
        return file

        
        
        