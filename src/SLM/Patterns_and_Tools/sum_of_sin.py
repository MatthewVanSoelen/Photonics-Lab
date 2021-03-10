import numpy as np 
from PIL import Image
import os

current_path = os.getcwd()
folder_path = os.path.join(current_path, "data_points")
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

def single_freq(data, x, amplitude, freq, folder_path, width, height):
    file_name = "freq_%s.png"%(freq)

    for i in range(width):
        gray = amplitude * (np.sin(x * freq) + 1)
        data[i, :] = gray

    img = Image.fromarray(data).convert('L')
    file_name = os.path.join(folder_path, file_name)
    img.save(file_name)
    img.show()

def sin_sum(data,temp_data, x, amplitude, start, end, num_of_steps, folder_path, width, height):
    
    freq_range = np.linspace(start, end, num_of_steps)
    file_name = "sum_%s-%s-%s.png"%(start, end, num_of_steps)
    print(start, end, num_of_steps)
    print(freq_range)
    for freq in freq_range:
        print(freq)
        for i in range(height):
            gray = amplitude * (np.sin(x * freq) + 1)
            temp_data[:, i] = gray
        data = (temp_data + data)
        # amplitude = (amplitude + 20) % 127 

    data = data/len(freq_range)
    img = Image.fromarray(data).convert('L')
    file_name = os.path.join(folder_path, file_name)
    img.save(file_name)
    img.show()

def single_from_data(data, data_points, x, amplitude, folder_path, width, height):
    
    for freq in data_points:
        file_name = "freq_%s.png"%(freq)

        for i in range(height):
            gray = amplitude * (np.sin(x * freq) + 1)
            data[:, i] = gray

        img = Image.fromarray(data).convert('L')
        file_name = os.path.join(folder_path, file_name)
        img.save(file_name, "PNG")

def line_of_length(data, length, x, amplitude, folder_path, width, height):
    freq_range = np.array([])
    for i in range(length - 1):
        dist = np.sqrt( 0**2 + i**2)
        c = get_coefficient(width, dist)
        freq_range = np.append(freq_range, c)
    file_name = "line_%s_[0,0].png"%(length)
    print(freq_range)
    for freq in freq_range:
        print(freq)
        for i in range(height):
            gray = amplitude * (np.sin(x * freq) + 1)
            temp_data[:, i] = gray
        data = (temp_data + data)

    data = data/len(freq_range)
    img = Image.fromarray(data).convert('L')
    file_name = os.path.join(folder_path, file_name)
    img.save(file_name)
    img.show()

def point_at(x, coords, amplitude, folder_path, width, height):
    side = np.sqrt(width**2 + height**2)
    data = np.zeros((height,width), dtype=np.uint16)
    
    dist = np.sqrt( coords[0]**2 + coords[1]**2)
    freq = get_coefficient(width, dist)
    angel = np.degrees(np.arctan(coords[1]/coords[0]))
    print(dist, freq, coords, angel)
    file_name = "point_[%s,%s].png"%(coords[0], coords[1])
    
    for i in range(height):
        gray = amplitude * (np.sin(x * freq) + 1)
        data[i, :] = gray
    print(data)
    img = Image.fromarray(data).convert('L')
    img.show()
    img = img.rotate(angel)
    file_name = os.path.join(folder_path, file_name)
    img.save(file_name)
    img.show()

def point_at_2(coords, amplitude, folder_path, width, height):
    x = np.linspace(0, 2*np.pi, width)
    y = np.linspace(0, 2*np.pi*(height/width), height)
    
    dist = np.floor(np.sqrt( coords[0]**2 + coords[1]**2))
    freq = get_coefficient(width, dist)
    if coords[0] < 1:
        angel = 0
    else:
        angel = np.arctan(coords[1]/coords[0])
    # angel = 0
    print(dist, freq, coords, angel)

    file_name = "point_2_[%s,%s].png"%(coords[0], coords[1])

    mesh_x, mesh_y = np.meshgrid(x, y)
    angled_mesh = mesh_x*np.cos(angel)+mesh_y*np.sin(angel)
    data = amplitude * (np.sin(angled_mesh * freq) + 1)
    img = Image.fromarray(data).convert('L')

    file_name = os.path.join(folder_path, file_name)
    img.save(file_name)
    img.show()

def line_at(coords, length, amplitutde, folder_path, width, height):
    x = np.linspace(0, 2*np.pi, width)
    y = np.linspace(0, 2*np.pi*(height/width), height)
    data = np.zeros((height,width), dtype=np.uint16)
    file_name = "line_at_[%s,%s]_%s.png"%(coords[0], coords[1], length)

    row = coords[1]
    for i in range(length-1):
        column = coords[0] + i

        dist = np.sqrt( column**2 + row**2)
        freq = get_coefficient(width, dist)
        if column < 1:
            angel = 0
        else:
            angel = np.arctan(row/column)
        # angel = 0
        print(dist, freq, (column, row), angel)

        mesh_x, mesh_y = np.meshgrid(x, y)
        angled_mesh = mesh_x*np.cos(angel)+mesh_y*np.sin(angel)
        temp = amplitude * (np.sin(angled_mesh * freq) + 1)
        data = temp + data
    data = data/length
    img = Image.fromarray(data).convert('L')
    file_name = os.path.join(folder_path, file_name)
    img.save(file_name)
    img.show()


def get_coefficient(width, dist):
    scaling_constant = 1600
    return (dist/scaling_constant) * width

# height = 1152
width = 1920
height = width
mode = 7
temp_data = np.zeros((height,width), dtype=np.uint16)
data = np.zeros((height,width), dtype=np.uint16)

x = np.linspace(-np.pi,np.pi, width)

amplitude = 127 
if mode == 1:
    # single frequency
    freq = 12
    single_freq(data, x, amplitude, freq, folder_path, width, height)
elif mode == 2:
    # sum of range of frequencies
    start = 1
    end = 16 
    num_of_steps = 16
    sin_sum(data,temp_data, x, amplitude, start, end, num_of_steps, folder_path, width, height)

elif mode == 3:
    # single frequencies from list of data points
    data_points = [1.2,2.4,3.6,4.8,6,7.2,8.4,9.6,10.8,12,13.2,14.4,15.6,16.8,18,19.2]
    single_from_data(data, data_points, x, amplitude, folder_path, width, height)

elif mode == 4:
    # line of various length [no shift]
    length = 5
    line_of_length(data, length, x, amplitude, folder_path, width, height)

elif mode == 5: 
    # point at defined coords
    x_pos = 5
    y_pos = 5
    coords = [x_pos, y_pos]
    point_at(x, coords, amplitude, folder_path, width, height)

    # point_at_2(coords, amplitude, folder_path, width, height)

elif mode == 6:
    # point at defined coords [using a graph transform]
    x_pos = 10
    y_pos = 10
    coords = [x_pos, y_pos]

    point_at_2(coords, amplitude, folder_path, width, height)

elif mode == 7:
    # create a horizontal line starting at coords [using a graph transform]
    x_pos = 100
    y_pos = 100
    coords = [x_pos, y_pos]
    length = 50

    line_at(coords, length, amplitude, folder_path, width, height)