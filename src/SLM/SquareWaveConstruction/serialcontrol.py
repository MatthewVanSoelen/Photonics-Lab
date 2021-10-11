"""
Control a number of serial devices using basic inheritence structure.

@author: Luke Kurlandski
@date: December 2019
@copyright: Copyright 2019, Luke Kurlandski, all rights reserved

Special thanks to Daniel Stolz, Matthew Van Soelen, and Dr. David McGee.

Read the Program Guide for detailed information about this program.
"""

import serial
import time

from exceptions import EquipmentError
from exceptions import ShutterError
from exceptions import MotorError
from exceptions import LaserError

class Equipment:
    """
    Control any piece of equipment that uses a serial port.
    """

    def __init__(self, configs:dict):
        """
        Equipment object with serial port and equipment configurations.
        """

        #Create a serial object, configure its serial connection and settings.
        self.ser = serial.Serial()
        self.configure_serial_port(configs)
        self.default_settings()
        self.configure_settings(configs)

    def configure_serial_port(self, configs:dict):
        """
        Set up the configurations of serial port.
        """

        if 'Port' not in configs:
            message = 'There was no serial port specified for equipment.'
            raise EquipmentError(message)
        self.ser.port = configs['Port']
        self.ser.baudrate = float(configs['Baudrate']) if 'Baudrate' in configs else 19200
        self.ser.timeout = float(configs['Timeout']) if 'Timeout' in configs else .1
        self.ser.stopbits = float(configs['Stopbits']) if 'Stopbits' in configs else 1
        self.ser.bytesize = float(configs['Bytesize']) if 'Bytesize' in configs else 8
        self.ser.parity = configs['Parity'][0] if 'Parity' in configs else 'N'

    def default_settings(self):
        """
        Assign default settings for equipment.
        """

        self.command_pause = .1

    def configure_settings(self, configs:dict):
        """
        Set settings shared by all serial objects, child should overload.
        """

        #Set a pause period after every command is written to prevent errors.
        if 'Command Pause' in configs:
            self.command_pause = float(configs['Command Pause'])

    def write_command(self, command:str, close_after=False):
        """
        Write a command with/without carriage return and opening of port.
        """

        #Check if port is open.
        if not self.ser.is_open:
            self.ser.open()
        #Attatch carriage return if not included.
        if command.find('\r') == -1:
            command += '\r'
        #Write to port and wait required period of time.
        try:
            self.ser.write(command.encode())
        except Exception as e:
            message = ('Could not write this command to serial device:\n\t'
                + command)
            raise EquipmentError(message, e)
        time.sleep(self.command_pause)
        #Close the port if needed.
        if close_after:
            self.ser.close()

class Shutter(Equipment):
    """
    Control the shutter.
    """
    
    def configure_serial_port(self, configs:dict):
        """
        Set up the configurations of serial port.
        """
        
        try:
            super().configure_serial_port(configs)
        except EquipmentError as e:
            advice = 'Ensure the correct serial info was supplied to Shutter.'
            raise ShutterError(e.message, e.exception, advice)

    def default_settings(self):
        """
        Assign default settings for the shutter.
        """

        super().default_settings()

    def configure_settings(self, configs:dict):
        """
        Configure the many settings of the shutter.
        """

        #Call to parent settings configuration.
        super().configure_settings(configs)
        #Shutter configurations.
        if 'Operating Mode' in configs:
            self.write_command('mode='+configs['Operating Mode'])
                
    def write_command(self, command:str, close_after=False):
        """
        Write a command with/without carriage return and opening of port.
        """
        
        try:
            super().write_command(command, close_after)
        except EquipmentError as e:
            advice = 'Read the manual for the shutter.'
            raise ShutterError(e.message, e.exception, advice)

    def toggle(self, pause:float):
        """
        Open shutter, pause, close Shutter.
        """

        self.write_command('ens')
        time.sleep(pause)
        self.write_command('ens')

class Motor(Equipment):
    """
    Control the motor.
    """
    
    def configure_serial_port(self, configs:dict):
        """
        Set up the configurations of serial port.
        """
        
        try:
            super().configure_serial_port(configs)
        except EquipmentError as e:
            advice = 'Ensure the correct serial info was supplied to Motor.'
            raise MotorError(e.message, e.exception, advice)

    def default_settings(self):
        """
        Assign default settings for the motor.
        """

        super().default_settings()

    def configure_settings(self, configs:dict):
        """
        Configure the many settings of the motor.
        """

        #Call to parent settings configuration.
        super().configure_settings(configs)
        #Configure for every axis provided inthe tuple of axes.
        if 'Axes' not in configs:
            message = 'Axes were not specified in the configurations for motor.'
            advice = 'Specify the axes: ex (1,2)'
            raise EquipmentError(message, None, advice)
        for axis in configs['Axes']:
            #Set the configurations for the motor.
            self.write_command(str(axis)+'MO')
            if 'Velocity' in configs:
                self.write_command(str(axis)+'VA'+str(configs['Velocity']))
            if 'Acceleration' in configs:
                self.write_command(str(axis)+'AC'+str(configs['Acceleration']))
            if 'Decceleration' in configs:
                self.write_command(str(axis)+'AG'+str(configs['Decceleration']))
                    
    def write_command(self, command:str, close_after=False):
        """
        Write a command with/without carriage return and opening of port.
        """
        
        try:
            super().write_command(command, close_after)
        except EquipmentError as e:
            advice = 'Read the manual for the Motor.'
            raise MotorError(e.message, e.exception, advice)

    def wait_motion_done(self, axis:int):
        """
        Halt the program until all motion is complete, checking every WAIT.
        """

        WAIT = .25
        while True:
            self.write_command(str(axis)+'MD?')
            byte_info = self.ser.read(4)
            try:
                str_info = str(byte_info.decode())
                if '1' in str_info:
                    return
                else:
                    time.sleep(WAIT)
            except Exception:
                pass

    def move_absolute(self, axis:int, go_to_position:float):
        """
        Move any axis to an absolute position.
        """

        self.write_command(str(axis)+'PA'+str(go_to_position))
        self.wait_motion_done(axis)

    def move_home(self, axis:int):
        """
        Move the motor to the home position.
        """

        self.write_command(str(axis)+'OR0')
        self.wait_motion_done(axis)

class Laser(Equipment):
    """
    Control the laser.
    """
    
    def configure_serial_port(self, configs:dict):
        """
        Set up the configurations of serial port.
        """
        
        try:
            super().configure_serial_port(configs)
        except EquipmentError as e:
            advice = 'Ensure the correct serial info was supplied to Shutter.'
            raise LaserError(e.message, e.exception, advice)

    def default_settings(self):
        """
        Assign default settings for the laser.
        """
        
        super().default_settings()
        self.max_power = -1
        self.power_change_pause = 0

    def configure_settings(self, configs:dict):
        """
        Configure the many settings of the laser.
        """

        #Call to parent configuration method.
        super().configure_settings(configs)
        #The laser cannot exceed this maximum power.
        if 'Max Power' in configs:
            self.max_power = float(configs['Max Power'])
        #The laser will pause for this long while changing power levels.
        if 'Power Change Pause' in configs:
            self.power_change_pause = float(configs['Power Change Pause'])
            
    def write_command(self, command:str, close_after=False):
        """
        Write a command with/without carriage return and opening of port.
        """
        
        try:
            super().write_command(command, close_after)
        except EquipmentError as e:
            advice = 'Read the manual for the Laser.'
            raise LaserError(e.message, e.exception, advice)

    def turn_on_off(self, on_off):
        """
        Turn laser on (True) or off (False.
        """

        if on_off:
            self.write_command('L=1')
        if not on_off:
            self.write_command('L=0')

    def change_power(self, new_power:float):
        """
        Alter the power of the laser, not exceeding the maximum power.
        """

        if new_power > self.max_power:
            message = ('Attempting to set a laser power greater than allowed:\n\t'
                + new_power + ' > ' + self.max_power)
            raise LaserError(message)
        else:
            self.write_command('P='+str(new_power))
        time.sleep(self.power_change_pause)









