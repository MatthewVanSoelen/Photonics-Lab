import numpy as np 
from PIL import Image
import pdb
import sys

# np.set_printoptions(threshold=sys.maxsize)

width = 2000
height = width
max_amplitude = 255

freq = 10
angle = 30
angle = np.radians(angle)

period = width/freq
amplitude = 255

slope = amplitude/period
# pdb.set_trace()
lin_x = np.linspace(0, amplitude, width)
lin_y = np.linspace(0, amplitude, height)

mesh_x, mesh_y = np.meshgrid(lin_x, lin_y)

angled_mesh = mesh_x*np.cos(angle)+mesh_y*np.sin(angle)
angled_mesh = (angled_mesh * freq) % max_amplitude
print(angled_mesh)

img = Image.fromarray(angled_mesh)
img.show()