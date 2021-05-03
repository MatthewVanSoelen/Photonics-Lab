import numpy as np 
from PIL import Image
import pdb
# from scipy import signal


# N = 256
# x = np.linspace(-np.pi,np.pi, N)
# sine1D = 128.0 + (127.0 * np.sin(x * 8.0))
# sine1D = np.uint8(sine1D)
# sine2D = np.ndarray((N,N), dtype=np.uint8)
# for i in range(N):
#     sine2D[i]= np.roll(sine1D,-i)

# img = Image.fromarray(sine2D)
# img.show()


# width = 1920
# height = 1152
# data1 = np.zeros((width,height), dtype=np.uint16)
# data2 = np.zeros((width,height), dtype=np.uint16)

# x1 = np.linspace(-np.pi,np.pi, width)
# x2 = np.linspace(-np.pi,np.pi, width)

# for i in range(height):
#     gray = 127 * (np.sin(x1 * 36) + 1)
#     data1[:, i] = gray

# for i in range(height):
#     gray = 32 * (np.sin(x2 * 11) + 1)
#     data2[:, i] = gray

# data = data1 + data2
# print(data[:,0])
# img = Image.fromarray(data).convert('L')
# img.show()



width = 2000
# height = width
height = 2000
# data = np.zeros((width, height), dtype=np.uint16)
# ratio = width/height
# x = np.linspace(0, 255, width)
# y = np.linspace(0, 255, height)

# mesh_x, mesh_y = np.meshgrid(x, y)
# angel = np.radians(0)
# angled_mesh = mesh_x*np.cos(angel)+mesh_y*np.sin(angel)
# data = 127.0 * (np.sin(angled_mesh * 5) + 1)
# img = Image.fromarray(data).convert('L')

# img.show()
# print(mesh_x, mesh_y)


color1 = 255
color2 = 0
# white_width = 20
# black_width = 20
data = np.zeros((width, height), dtype=np.uint16)
# for x in range(width//4):
# 	if x % white_width
# period = 5
# num_cycles = width//period
# t = np.linspace(0, 1, height)
# plot = signal.square(2 * np.pi * num_cycles * t)
# plot = (plot + 1)/2 * (255)
# for i in range(width):
# 	data[i] = plot
# pdb.set_trace()
lpmm = 500
period = width // (2*lpmm)
count = 0
i = 0
while(i < width):
	if count % 2 == 0:
		for x in range(period):
			if x + i < width:
				data[x + i] = color1
				# i = i + period
	else:
		for x in range(period):
			if x + i < width:
				data[x + i] = color2
				# i = x + period
	count += 1
	i = i + period
	
	# print(i)
img = Image.fromarray(data).convert('L')

img.show()
# width_old = 1152
# height_old = 1920
# width = 1920
# height = 1152
# h_ratio = height/height_old
# w_ratio = width/width_old
# angle = np.radians(45)
# max_amplitude = 255
# lin_x = np.linspace(0, 255 * w_ratio,  width)
# lin_y = np.linspace(0, 255 * h_ratio,  height)

# mesh_x, mesh_y = np.meshgrid(lin_x, lin_y)

# angled_mesh = mesh_x*np.cos(angle)+mesh_y*np.sin(angle)
# angled_mesh = (angled_mesh * 4 %  max_amplitude)

# angled_mesh = np.round(angled_mesh)

# img = Image.fromarray(angled_mesh).convert('L')
# img.show()

# lin_x = np.linspace(0, 255,  width_old)
# lin_y = np.linspace(0, 255,  height_old)

# mesh_x, mesh_y = np.meshgrid(lin_x, lin_y)

# angled_mesh = mesh_x*np.cos(angle)+mesh_y*np.sin(angle)
# angled_mesh = (angled_mesh * 4 %  max_amplitude)

# angled_mesh = np.round(angled_mesh)

# img = Image.fromarray(angled_mesh).convert('L')
# img.show()