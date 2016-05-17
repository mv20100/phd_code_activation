from Tkinter import *
from lightCtrl import LightCtrl



lightCtrl = LightCtrl(comPort='com4')
master = Tk()
def setValue(value):
	lightCtrl.white(int(value))
	return
w = Scale(master, from_=0, to=255,command=setValue)



w.pack()
mainloop()
