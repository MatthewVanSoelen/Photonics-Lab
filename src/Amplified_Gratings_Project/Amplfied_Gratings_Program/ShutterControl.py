#Matthew Van Soelen
import serial
import time #package used to reduce communications with serial port

class Shutter:
    '''
    ser: serial port (serial object)
    '''
    
    ser = serial.Serial()
    
    def __init__(self, port, baudrate=9600, timeout=.1, stopbits=1, bytesize=8):
        '''
        Construct an object and configure the serial port.
        #flow control = 1?
        '''
        
        
        self.ser.port = port
        self.ser.baudrate = baudrate
        self.ser.timeout = timeout
        self.ser.stopbits = stopbits
        self.ser.bytesize = bytesize
        
    def writeCommand(self, command, closeAfter=False):
        '''
        Send any command to a serial port.
        (arg1) self 
        (arg2) command: the command to send to the motor (string)
        (arg3) closeAfter: close port after command, if true (boolean)
        '''
        
        cmd = command
        if cmd.find('\r') == -1:
            cmd = cmd + '\r'
        if self.ser.is_open == False:
            self.ser.open()
        self.ser.write(cmd.encode())
        if closeAfter == True:
            self.ser.close()
            
    def toggle_pause(self, pause):
        '''
        Opens the shutter. Pauses for a certain amount of time. Closes
            the shutter.
        (arg1) pause : number of seconds to pause (float)
        '''
        self.writeCommand('ens')
        time.sleep(pause)
        self.writeCommand('ens')

    def toggle(self):
        self.writeCommand('ens')

    def startup(self):
        response = self.writeCommand('ens?')
        if response == "0":
            self.writeCommand('ens')
        
        
def test():
    s = Shutter('COM3')
    
    s.toggle_shutter(4)
    s.toggle_shutter(1)
    s.ser.close()

