"""
Provide basic exception handling for common errors that may arise.

@author: Luke Kurlandski
@date: December 2019
@copyright: Copyright 2019, Luke Kurlandski, all rights reserved

Special thanks to Daniel Stolz, Matthew Van Soelen, and Dr. David McGee.

Read the Program Guide for detailed information about this program.
"""

class MyError(Exception):
    """
    Exceptions for common errors.
    """
    
    def __init__(self, message:str=None, exception:Exception=None, advice:str=None):
        """
        Create exceptions of this class with these three properties.
        """
        
        self.message = message
        self.exception = exception
        self.advice = advice

class FileFormatError(MyError):
    """
    Raise when a storage file is written to in the wrong format.
    """
    pass

class InputError(MyError):
    """
    Raise when the user has input data incorrectly.
    """
    pass

class NoFileError(MyError):
    """
    Raise when any type of file cannot be located.
    """
    pass

class UnknownError(MyError):
    """
    Raise when an unexpected error occurs.
    """
    pass

class MissingDataError(MyError):
    """
    Raise when nessecary data is not available.
    """
    pass

class UserInterruptError(MyError):
    """
    Raise when user halts a process.
    """
    pass

class EquipmentError(MyError):
    """
    Provide framework for any kind of equipment error.
    """
    pass

class ShutterError(EquipmentError):
    """
    Raise when an error occurs with shutter.
    """
    pass

class MotorError(EquipmentError):
    """
    Raise when an error occurs with motor.
    """
    pass

class LaserError(EquipmentError):
    """
    Raise when an error occurs with laser.
    """
    pass