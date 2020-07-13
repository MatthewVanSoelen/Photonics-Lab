


from __future__ import print_function
from pipython import GCSDevice, pitools
import time
import numpy
import ShutterControl
import threading


def check(app, pidevice):
    while not app.info.finished:
        if not app.begin_experiment:
            pidevice.STP("1")
            break
        else:
            time.sleep(app.info.stop_check)
        

def go_home(app, info):
    CONTROLLERNAME = 'E-873'
    STAGES = ['Q-545.240']
    REFMODES = ['FNL', 'FRF']
    comport = str(app.gui.entry_port_mot.get())
    

    with GCSDevice(CONTROLLERNAME) as pidevice:
        pidevice.ConnectRS232(comport=1, baudrate=115200)
        pitools.startup(pidevice, stages=STAGES, refmodes=REFMODES)

        rangemin = pidevice.qTMN()
        rangemax = pidevice.qTMX()
        curpos = pidevice.qPOS()
        pidevice.VEL("1",info.max_velocity)

        pidevice.MOV("1", rangemin["1"]) 
        pitools.waitontarget(pidevice, axes="1")
        print('current position of axis {} is {:.4f}'.format("1", pidevice.qPOS("1")["1"]))


def case_0_experiment(pidevice, app, info, rangemin, rangemax, curpos): # Shutter and not continuous
    info.port_shut = "COM%s"%info.port_shut
    shutter = ShutterControl.Shutter(info.port_shut)
    shutter.startup()

    print("The experiment is running0")
    if(info.total_distance > rangemax["1"] - curpos["1"]):
        info.total_distance = rangemax["1"]
    if(info.step_size < 0.00001):
        info.step_size = 0.00001
    
    # move to the minimum of the stage (-13)
    pidevice.MOV("1", rangemin["1"]) 
    pitools.waitontarget(pidevice, axes="1")
    print('current position of axis {} is {:.4f}'.format("1", pidevice.qPOS("1")["1"]))

    for axis in pidevice.axes:
        for target in numpy.arange(rangemin[axis] + info.step_size, rangemin[axis] + info.total_distance + info.step_size, info.step_size):
            if(app.begin_experiment):
                shutter.toggle_pause(info.exposure_time)
                time.sleep(info.motor_delay)
                pidevice.MOV(axis, target)
                pitools.waitontarget(pidevice, axes=axis)
                position = pidevice.qPOS(axis)[axis]
                print('current position of axis {} is {:.4f}'.format(axis, position))
            else:
                break

    print('done')
    shutter.ser.close()

def case_1_experiment(pidevice, app, info, rangemin, rangemax, curpos): # Shutter and continuous
    info.port_shut = "COM%s"%info.port_shut
    shutter = ShutterControl.Shutter(info.port_shut)
    shutter.startup()

    print("The experiment is running1")

    if(info.total_distance > rangemax["1"] - curpos["1"]):
        info.total_distance = rangemax["1"]
    
    # move to the minimum of the stage (-13)
    pidevice.MOV("1", rangemin["1"]) 
    pitools.waitontarget(pidevice, axes="1")
    print('current position of axis {} is {:.4f}'.format("1", pidevice.qPOS("1")["1"]))
    
    pidevice.VEL("1", info.velocity)
    
    for axis in pidevice.axes:
        target = rangemin[axis] + info.total_distance
        shutter.toggle_pause(info.exposure_time)
        time.sleep(info.motor_delay)
        pidevice.MOV(axis, target)
        pitools.waitontarget(pidevice, axes=axis)
        position = pidevice.qPOS(axis)[axis]
    print('current position of axis {} is {:.4f}'.format("1", pidevice.qPOS("1")["1"]))
    shutter.ser.close()
    print('done')

def case_2_experiment(pidevice, app, info, rangemin, rangemax, curpos): # No shutter and not continuous
    info.port_shut = "COM%s"%info.port_shut
    shutter = ShutterControl.Shutter(info.port_shut)
    shutter.startup()
    
    print("The experiment is running2")
    if(info.total_distance > rangemax["1"] - curpos["1"]):
        info.total_distance = rangemax["1"]
    if(info.step_size < 0.00001):
        info.step_size = 0.00001
    
    # move to the minimum of the stage (-13)
    pidevice.MOV("1", rangemin["1"]) 
    pitools.waitontarget(pidevice, axes="1")
    print('current position of axis {} is {:.4f}'.format("1", pidevice.qPOS("1")["1"]))
    shutter.toggle() #open shutter
    for axis in pidevice.axes:
        for target in numpy.arange(rangemin[axis] + info.step_size, rangemin[axis] + info.total_distance + info.step_size, info.step_size):
            if(app.begin_experiment):
                time.sleep(info.exposure_time)
                pidevice.MOV(axis, target)
                pitools.waitontarget(pidevice, axes=axis)
                position = pidevice.qPOS(axis)[axis]
                print('current position of axis {} is {:.4f}'.format(axis, position))
            else:
                break

    shutter.toggle()
    shutter.ser.close()                
    print('done')
def case_3_experiment(pidevice, app, info, rangemin, rangemax, curpos): # No shutter and continuous
    info.port_shut = "COM%s"%info.port_shut
    shutter = ShutterControl.Shutter(info.port_shut)
    shutter.startup()

    print("The experiment is running3")
    if(info.total_distance > rangemax["1"] - curpos["1"]):
        info.total_distance = rangemax["1"]
    
    # move to the minimum of the stage (-13)
    pidevice.MOV("1", rangemin["1"]) 
    pitools.waitontarget(pidevice, axes="1")
    print('current position of axis {} is {:.4f}'.format("1", pidevice.qPOS("1")["1"]))
    
    pidevice.VEL("1", info.velocity)
    shutter.toggle() #open Shutter
    for axis in pidevice.axes:
        target = rangemin[axis] + info.total_distance
        pidevice.MOV(axis, target)
        pitools.waitontarget(pidevice, axes=axis)
        position = pidevice.qPOS(axis)[axis]
    print('current position of axis {} is {:.4f}'.format("1", pidevice.qPOS("1")["1"])) 
    shutter.toggle()
    shutter.ser.close()                        
    print('done')
def case_4_experiment(pidevice, app, info, rangemin, rangemax, curpos): # Shutter not connected and not continuous
    print("The experiment is running4")
    if(info.total_distance > rangemax["1"] - curpos["1"]):
        info.total_distance = rangemax["1"]
    if(info.step_size < 0.00001):
        info.step_size = 0.00001
    
    # move to the minimum of the stage (-13)
    pidevice.MOV("1", rangemin["1"]) 
    pitools.waitontarget(pidevice, axes="1")
    print('current position of axis {} is {:.4f}'.format("1", pidevice.qPOS("1")["1"]))

    for axis in pidevice.axes:
        for target in numpy.arange(rangemin[axis] + info.step_size, rangemin[axis] + info.total_distance + info.step_size, info.step_size):
            if(app.begin_experiment):
                time.sleep(info.exposure_time)
                pidevice.MOV(axis, target)
                pitools.waitontarget(pidevice, axes=axis)
                position = pidevice.qPOS(axis)[axis]
                print('current position of axis {} is {:.4f}'.format(axis, position))
            else:
                break

    print('done')
def case_5_experiment(pidevice, app, info, rangemin, rangemax, curpos): # Shutter not connected and continuous
    print("The experiment is running5")
            
    if(info.total_distance > rangemax["1"] - curpos["1"]):
        info.total_distance = rangemax["1"]
    
    # move to the minimum of the stage (-13)
    pidevice.MOV("1", rangemin["1"]) 
    pitools.waitontarget(pidevice, axes="1")
    print('current position of axis {} is {:.4f}'.format("1", pidevice.qPOS("1")["1"]))
    
    pidevice.VEL("1", info.velocity)
    
    for axis in pidevice.axes:
        target = rangemin[axis] + info.total_distance
        pidevice.MOV(axis, target)
        pitools.waitontarget(pidevice, axes=axis)
        position = pidevice.qPOS(axis)[axis]
    print('current position of axis {} is {:.4f}'.format("1", pidevice.qPOS("1")["1"]))
    print('done')



def run_experiment(app,info):
    try:
        #perform experiment

        CONTROLLERNAME = 'E-873'
        STAGES = ['Q-545.240']
        REFMODES = ['FNL', 'FRF']
        comport = info.port_mot
       
        
        with GCSDevice(CONTROLLERNAME) as pidevice:
        # Choose the interface according to your cabling.

            pidevice.ConnectRS232(comport=1, baudrate=115200)

        # Each PI controller supports the qIDN() command which returns an
        # identification string with a trailing line feed character which
        # we "strip" away.

            print('connected: {}'.format(pidevice.qIDN().strip()))

        # Show the version info which is helpful for PI support when there
        # are any issues.

            if pidevice.HasqVER():
                print('version info:\n{}'.format(pidevice.qVER().strip()))

        # In the module pipython.pitools there are some helper
        # functions to make using a PI device more convenient. The "startup"
        # function will initialize your system. There are controllers that
        # cannot discover the connected stages hence we set them with the
        # "stages" argument. The desired referencing method (see controller
        # user manual) is passed as "refmode" argument. All connected axes
        # will be stopped if they are moving and their servo will be enabled.

            print('initialize connected stages...')
            pitools.startup(pidevice, stages=STAGES, refmodes=REFMODES)
        
        # Now we query the allowed motion range and current position of all
        # connected stages. GCS commands often return an (ordered) dictionary
        # with axes/channels as "keys" and the according values as "values".

            rangemin = pidevice.qTMN()
            rangemax = pidevice.qTMX()
            curpos = pidevice.qPOS()
            info.finished = False
            pidevice.VEL("1", info.max_velocity)
            stop_thread = threading.Thread(target=check, args=(app, pidevice))
            stop_thread.daemon = True
            stop_thread.start()
            
        # The GCS commands qTMN() and qTMX() used above are query commands.
        # They don't need an argument and will then return all availabe
        # information, e.g. the limits for _all_ axes. With setter commands
        # however you have to specify the axes/channels. GCSDevice provides
        # a property "axes" which returns the names of all connected axes.
        # So lets move our stages...
            
            if(info.shut_status and not info.continuous and info.shut_connected):       # Shutter and not continuous
                case_0_experiment(pidevice, app, info, rangemin, rangemax, curpos)
            elif(info.shut_status and info.continuous and info.shut_connected):         # Shutter and continuous
                case_1_experiment(pidevice, app, info, rangemin, rangemax, curpos)
            elif(not info.shut_status and not info.continuous and info.shut_connected): # No shutter and not continuous
                case_2_experiment(pidevice, app, info, rangemin, rangemax, curpos)
            elif(not info.shut_status and info.continuous and info.shut_connected):     # No shutter and continuous
                case_3_experiment(pidevice, app, info, rangemin, rangemax, curpos)
            elif(not info.continuous and not info.shut_connected):                      # Shutter not connected and not continuous
              case_4_experiment(pidevice, app, info, rangemin, rangemax, curpos)
            elif(info.continuous and not info.shut_connected):                         # Shutter not connected and continuous
               case_5_experiment(pidevice, app, info, rangemin, rangemax, curpos)
                
    except:
        print('An error has occured:')
    finally:
        app.info.finished = True
            
        print('Processes finished')
        
