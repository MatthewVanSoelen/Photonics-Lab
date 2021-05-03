from tkinter import *
from PIL import Image, ImageTk
from slm_window import SLM_window




def show(slm, image):
	slm.display(grating=image)
	print("pressed")

root = Tk()

image = Image.open("/Users/matthewvansoelen/Desktop/Photonics-Lab/src/SLM/DOE_Creation/Images/Sample_Grating.png").convert('L')
image = ImageTk.PhotoImage(image)
slm = SLM_window(root, grating = image)
# window = Toplevel(root)
# label = Label(window, image=image)
# label.pack()

show_button = Button(root, text="Show", command= lambda: show(slm, image))
show_button.pack()

root.mainloop()