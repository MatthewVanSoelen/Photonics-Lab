
import numpy
import time

def run_experiment(client,total_distance, step_size, exposure_time, width_film, height_film, port_mot):

    
    distance = total_distance
    step = step_size
    minrange = -13

    print(minrange)
    for target in numpy.arange(minrange + step, minrange + distance, step):
        if (client.begin_experiment):
            time.sleep(exposure_time)
            msg = str(target)
            print("target: %s" %msg)
        else:
            print("quitting")
            break
            # self.thread_client.queue.put(msg)

def go_home():
    print("go home")