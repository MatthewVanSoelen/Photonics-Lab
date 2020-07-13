# grab the middle row of ftl file.
import time
from datetime import date 
from tqdm import tqdm
import os 
from tkinter import filedialog
from tkinter import *
import codecs
import sys
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import csv
import re

######################################################################
'''
Read file 
'''

current_path = os.getcwd() #get current directory
folder_path = os.path.join(current_path,"Results(%s)" %(date.today()))
if not os.path.exists(folder_path):
	os.makedirs(folder_path)

file_names = []
file_end = ".flt.txt"

with open(os.path.join(folder_path,"fileSet.csv"),"w+") as out_file: #open a new file to store the data
     pass

for file_name in os.listdir(current_path):  # loop through all files in current directory
    if file_name.endswith(file_end):        # if the file ends with ".FTL.txt" then add to the list of file names
        file_names.append(file_name)



for i in tqdm(range(len(file_names))): # loops through each file with ".FTL.txt", updates progress bar after each loop
    file_name = file_names[i]
    data = []
    

    with codecs.open(file_name, encoding='utf-8', errors='ignore') as file:
        x_res = 0
        y_res = 0
        scan_range_x = 0

        '''
        reads file one line at a time
        if the line contains the x or y resolution or the scanning range then save those values
            try to convert those values into integers.
        if the values are 0 then program could not find values
        '''
        for line in file: 
            if "ResolutionX" in line:                       
                x_res = int(line[line.find("=")+1:line.rfind("\"")])
            if "ResolutionY" in line:
                y_res = int(line[line.find("=")+1:line.rfind("\"")])
            if "ScanRangeX" in line:
                scan_range_x = float(line[line.find("=")+1:line.rfind("\"")-3])

            try:# if the line can be converted into a number than save it too data array
                float(line.strip()) # delete extra spaces and convert to decimal number
                data.append(line.strip()) # save number to data array
            except:
                pass
        
        if x_res == 0 or y_res == 0 or scan_range_x == 0.0:
            print("could not find nessesary values \n xres: %s \t yres: %s \t scanRangeX: %s" %(x_res, y_res, scan_range_x))
            sys.exit()

    data = np.asarray(data) # convert data array to numpy array (needed to use graphing functions)
    '''
    The FTL.txt files provide a list of height values which we save in y_middle_slice
    in order to create an x axis we divide the scanning range by the x resolution
    '''
    middle_index = x_res * (y_res//2) + 1 # index of middle slice
    y_middle_slice = data[middle_index : middle_index + x_res - 1] # get height data from middle slice (y coord)
    
    x_middle_slice = np.zeros((len(y_middle_slice))) # create array for x coord
    unit = scan_range_x/x_res   # each unit is the width between data points 

    for index in range(len(x_middle_slice)):
        x_middle_slice[index] = unit * (index + 1) # fill in values for the x axis


    ######################################################################
    '''
    Begin Graphing 
    '''

    # convert numbers in the arrays to decimal values
    y1 = y_middle_slice.astype(float) 
    x1 = x_middle_slice.astype(float)
    
    linear_fit = np.polyfit(x1, y1, 1) # create line of best fit
    linear_1d = np.poly1d(linear_fit) # create a polynomial equation which represents the line of best fit

    y1 = y1 - linear_1d(x1) # subtract the y values by the y value line of best fit (correcting the angle created by the AFM)

    poly_grade = 15 
    range_value_x1 = np.floor(x1[0]) # the beginning if the x axis 
    range_value_x2 = np.ceil(x1[len(x1)-1]) # the end of the x axis
    line_width = .3 # the line width for the poly fit graph



    # find the maxima
    max_indices = signal.find_peaks(y1, distance=5)[0] # returns the indexes where maximas 
    maxima_value_x1 = x1[max_indices] # creates an array of the x values where maximas are
    maxima_value_y1 = y1[max_indices] # creates an array of the y values where maximas are

    max_peak = 0
    max_peak_index = 0

    """
    Loops through all the maximas and finds the highest max
    """
    for index in range(len(maxima_value_y1)):
        if float(maxima_value_y1[index]) > max_peak:
            max_peak = maxima_value_y1[index]
            max_peak_index = index

    num_peaks_avg = 5 # the number of periods on each side of the max peak used to calculate the period average
    period_sum = 0
    start = max_peak_index - num_peaks_avg # the index of the first max to use
    end = max_peak_index + num_peaks_avg # the index of the last max to use

    """
    if the first index is smaller than the 0 replace the index with 0
    if the last index is greater than the length of the array then replace it with the last element in the array
    """
    if end > len(maxima_value_x1):
        end = len(maxima_value_x1)
    elif start < 0:
        start = 0


    # find the distance between maximas and average them to find the avg period
    for index in range(start, end):
        dist = maxima_value_x1[index + 1] - maxima_value_x1[index]
        period_sum += dist
    period = period_sum/(end-start)

    """
    In order to find the minimums we invert the y values and look for the maxiums
    """
    y2 = y1*-1

    # find the minima
    peak_distance = (scan_range_x/period/3) # the minimum x distance between peaks
    min_indices = signal.find_peaks(y2, distance= peak_distance)[0] # returns the indicies where peaks exist 

    minima_value_x1 = x1[min_indices] # creates an array of the x values where minima are
    minima_value_y1 = y1[min_indices] # creates an array of the y values where minima are


    # calculate polynomial for the maxima
    polyfit_maxima = np.polyfit(maxima_value_x1, maxima_value_y1, poly_grade)
    poly1d_maxima = np.poly1d(polyfit_maxima)

    # calculate polynomial for the minima
    polyfit_minima = np.polyfit(minima_value_x1, minima_value_y1, poly_grade)
    poly1d_minima = np.poly1d(polyfit_minima)
    
    y_poly1d_maxima = poly1d_maxima(maxima_value_x1)
    y_poly1d_minima = poly1d_minima(minima_value_x1)

    # find the max. height of a hixel 
    maximum_poly_curve = poly1d_maxima - poly1d_minima
    maximum_poly_curve_ranges = np.arange(range_value_x1, range_value_x2, 0.0001)    
    y_max = np.max(maximum_poly_curve(maximum_poly_curve_ranges))

    plt.figure() #create figure

    plt.plot(x1, y1,lineWidth = line_width, label="Data") # add axis information

    plt.plot(maxima_value_x1, maxima_value_y1,'o', markersize = 3) # add maximas to graph
    plt.plot(minima_value_x1, minima_value_y1,'o', markersize = 3) # add minimas to graph
    
    plt.plot(maxima_value_x1, y_poly1d_maxima) # add max poly fit to graph
    plt.plot(minima_value_x1, y_poly1d_minima) # add min poly fit to graph

    plt.plot(maximum_poly_curve_ranges, maximum_poly_curve(maximum_poly_curve_ranges),
     color = 'orange', label="Height (PolyFit)" + '\n' "= "+ str(round(y_max, 2)) + " [nm]")
    
    
    
    legend_1 = plt.legend(loc = 'lower right', ncol = 1, fontsize = 'xx-small')
    # naming the x axis 
    plt.xlabel('width [\u03BCm]') 
    # naming the y axis 
    plt.ylabel('height [nm]')

    plt.xticks( fontsize=8)
    plt.yticks( fontsize=8)
    plt.grid(linewidth = .3)
    # save the plot as .png
    plt.savefig(os.path.join(folder_path,"%s.png"%(file_name)), dpi = 1000)

    ######################################################################
    '''
    Writing to new file 
    '''
    
    # CREATE: max, min, and polyfit info .csv file 

    with open(os.path.join(folder_path,"%s_CURVE_DATA.csv"%(file_name)), "w") as file: # create file in folder
    	file.write("%s,\n" %(file_name)) 
    	file.write("max_poly_fit, %s\n" %(",".join(str(x) for x in polyfit_maxima))) # insert max polyfit data points
    	file.write("min_poly_fit, %s\n" %(",".join(str(x) for x in polyfit_minima)))
    	file.write("\n,x_Max, y_Max, x_Min, y_Min,\n")
    	
    	num = max([maxima_value_x1.size, minima_value_x1.size])
    	i = 0
    	while(i < num):
    		string = ""
    		if(i < maxima_value_x1.size):
    			string += ",%s,%s" %(maxima_value_x1[i], maxima_value_y1[i])

    		if(i < minima_value_x1.size):
    			string += ",%s,%s" %(minima_value_x1[i], minima_value_y1[i])

    		string += "\n"
    		file.write(string)
    		i += 1




    
    # CREATE: list of files.csv

    with open(os.path.join(folder_path,"fileSet.csv"),"r+", newline='\n') as out_file:
        out_string = "" #line printed to file 
        period = str(period)
        y_max = str(y_max)
        out_string += "\n %s," %file_name 
        file_name_copy = file_name
        
        num_fields = file_name_copy.count("_") # the number of columns in the csv file
        file_name_copy = file_name_copy[:file_name_copy.find(file_end)] # cut off the .FLT.txt endding
        count = 0 #number of columns created
        """
        for each "_" save part of the file name to a column and add "," after
        """
        for i in range(num_fields):
            column =  file_name_copy[:file_name_copy.find("_")] + "," 
            file_name_copy = file_name_copy[file_name_copy.find("_")+1:]
            out_string += column
            count = i;
        out_string += "%s,%s,%s" %(file_name_copy, period, y_max) # add the period and y_max to the end of the line
            
        if "File" not in out_file.read(10):# if no header then add header
            header = "File,"
            for x in range(i+2): # add ","s to the header for every column created
                header += " ,"
            header += "Period, Y_max" # add titles to header
            out_file.write(header) # write header to csv file
        out_file.write(out_string) # write line to file
        


