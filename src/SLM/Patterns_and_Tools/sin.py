import numpy as np 
from PIL import Image


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



width = 1920
# height = width
height = 1152
data = np.zeros((width, height), dtype=np.uint16)
ratio = width/height
x = np.linspace(0, 4*np.pi, width)
y = np.linspace(0, 4*np.pi*height/width, height)

mesh_x, mesh_y = np.meshgrid(x, y)
angel = np.radians(45)
data = 127.0 * (np.sin((mesh_x*np.cos(angel)+mesh_y*np.sin(angel)) * 12) + 1)
img = Image.fromarray(data).convert('L')

img.show()
# print(mesh_x, mesh_y)