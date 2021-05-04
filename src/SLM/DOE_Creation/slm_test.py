import tkinter as tk
from PIL import Image, ImageTk
from slm_window import SLM_window




def show(slm, image):
	slm.display(grating=image)
	print("pressed")
    
def show_text(slm, message):
    slm.display_text(message)
    print("text")

root = tk.Tk()

image = Image.open("C:\\Users\\mcgeed\\Documents\\GitHub\\Photonics-Lab\\src\\SLM\\DOE_Creation\\Images\\Sample_Grating.png")
image = image.convert('L')
image = ImageTk.PhotoImage(image)
print(type(image))
slm = SLM_window(root, grating = image)
# window = Toplevel(root)
# label = Label(window, image=image)
# label.pack()

show_button = tk.Button(root, text="Show", command= lambda: show(slm, image))
show_button.pack()

text_button = tk.Button(root, text="text", command= lambda: show_text(slm,message="test Message"))
text_button.pack()

root.mainloop()