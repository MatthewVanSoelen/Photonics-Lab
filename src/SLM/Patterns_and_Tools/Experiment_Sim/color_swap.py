import numpy as np 
from PIL import Image
import pdb 
file_name = "book.png"
file_path = "/Users/matthewvansoelen/Desktop/FFT drawings/%s"%(file_name)

img = Image.open(file_path).convert('L')
data = np.asarray(img)

threshold = 128
# data = np.where(data < threshold, data, 255)
# data = np.where(data >= threshold, data, 0)
# pdb.set_trace()
temp = np.array(255 * data.shape)
data = 255 - data


# black = np.where(data < threshold, data, 0)
# white = np.where(data >= threshold, data, 255)

# data = white + black





img = Image.fromarray(data).convert('L')
img.show()