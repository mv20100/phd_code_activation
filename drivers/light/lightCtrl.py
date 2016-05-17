import time
import serial

class LightCtrl(object):
	def __init__(self,comPort='com4'):
		try:
			self.ser = ser = serial.Serial(port=comPort,timeout=5)
		except serial.serialutil.SerialException:
			#no serial connection
			self.ser = None
		else:
			pass
		print("Light controller connection open")
		self.white(255)
	
	def write(self,command):
		self.ser.write(command+"\n")
		return
		
	def __del__(self):
		if self.ser:
			self.white(0)
			self.ser.close()
			print("Light controller connection closed")

	def white(self,level):
		self.write("w:%d"%level)
		return

	def red(self,level):
		self.write("r:%d"%level)
		return

	def green(self,level):
		self.write("g:%d"%level)
		return

	def blue(self,level):
		self.write("b:%d"%level)
		return
	
if __name__=='__main__':
	lightCtrl = LightCtrl()