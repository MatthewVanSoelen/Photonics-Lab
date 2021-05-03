from tkinter import *
from tkinter.ttk import *

tk=Tk()
process_frame = Frame(tk, borderwidth=2, relief=SUNKEN)
process_frame.pack(side="top", fill="both", expand=True)
progress=Progressbar(tk,orient=HORIZONTAL,length=100,mode='determinate')
progress.pack()
def bar():
    import time
    progress['value']=20
    process_frame.update()
    time.sleep(1)
    progress['value']=50
    process_frame.update()
    time.sleep(1)
    progress['value']=80
    process_frame.update()
    time.sleep(1)
    progress['value']=100


Button(process_frame,text='foo',command=bar).pack()
mainloop()