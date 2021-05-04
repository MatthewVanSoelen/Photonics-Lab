import serial
import time

from exceptions import EquipmentError
from exceptions import MotorError

class Motor():

    def __init__(self, port):
        self.ser = serial.Serial()

        self.ser.port = port
        self.ser.baudrate = float(19200)
        self.ser.timeout = float(.1)
        self.ser.stopbits = float(1)
        self.ser.bytesize = float(8)
        self.ser.parity = 'N'
        self.command_pause = .1

        for axis in (1,2):
            self.write_command(str(axis)+'MO')      # Turns Motor on
            self.write_command(str(axis)+'VA'+'1')  # Sets velocity to 1
            self.write_command(str(axis)+'AC'+'4')  # Sets acceleration to 4
            self.write_command(str(axis)+'AG'+'4')  # Sets deceleration to 4


    def write_command(self, command:str):
        if not self.ser.is_open:
            self.ser.open()

        if command.find('\r') == -1:
            command += '\r'

        try:
            self.ser.write(command.encode())
        except Exception as e:
            message = ('Could not write this command to serial device:\n\t' + command)
            raise EquipmentError(message, e)
        time.sleep(self.command_pause)

    def wait_motion_done(self, axis:int):
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

    def move_rel(self, axis:int, increment:float):
        """
        Move the axis to a relative position
        """

        self.write_command(str(axis)+'PR'+str(increment))
        self.wait_motion_done(axis)
        



def start():
    motor = Motor('COM25')

    
    # motor.move_rel(1, 0.01)  # moves axis 1 0.5 units posititve
    # motor.move_rel(1, -0.5)  # moves axis 1 0.5 units negative
    '''
    motor.move_rel(0, 0.5)  # moves axis 0 0.5 units posititve
    motor.move_rel(0, -0.5)  # moves axis 0 0.5 units negative

    motor.move_home(0)  # moves axis 0 home
    motor.move_home(1)  # moves axis 1 home'''

    motor.move_absolute(1, 0.01) # moves axis 0 to position 20
    motor.move_absolute(2, 0) # moves axis 1 to position 20


start()

