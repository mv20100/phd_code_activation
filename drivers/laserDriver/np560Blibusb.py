import usb.core
import usb.util
from time import time, sleep
import numpy as np

class NP560B():
	def __init__(self):		
		# find our device
		print "Starting Laser Driver"
		self.dev = usb.core.find(idVendor=0x104d, idProduct=0x1001)
		if self.dev is None:
			self.enabled = False
			print "Could not connect to laser diode driver"
		else:
			print "Connection OK"
			self.enabled = True
			self.cfg = self.dev[0]
			self.intf = self.cfg[(0,0)]
			self.ep = self.intf[1]
			self.epout = self.intf[3]
	
	def SendCommand(self,msg):
		print msg
		return self.ep.write(msg)

	def query(self,msg):
		print msg
		return self.ep.write(msg)
	
	# Basic methods

	def SetOutput(self,outputStatus):
		msg = "LASer:OUTput"+" "+str(int(outputStatus))
		self.SendCommand(msg)
		
	def SetCurrentSetPoint(self,currentSetPoint):	
		return self.SendCommand("LASer:LDI"+" "+str(currentSetPoint))

	# Advanced methods

	def RampCurrent(self,Iin,Iout,duration):
		dt = 0.2
		n = int(duration/dt)
		currentPoints = np.linspace(Iin,Iout,n)
		for current in currentPoints:
			self.SetCurrentSetPoint(current)
			sleep(dt)
		
	def StepCurrent(self,I,t1,t2):
		self.SetCurrentSetPoint(0)
		sleep(1)
		self.SetOutput(1)
		sleep(4)
		self.SetCurrentSetPoint(I)
		sleep(t1)
		self.SetCurrentSetPoint(0)
		sleep(1)
		self.SetOutput(0)
		sleep(t2)
		
	def Sequence(self,Imax,t1,t2,t3):
		self.SetOutput(1)
		sleep(4)
		self.RampCurrent(0,Imax,t1)
		sleep(t2)
		self.RampCurrent(Imax,0,t3)
		sleep(1)
		self.SetOutput(0)
	
	def StartAim(self):
		print "Turning on laser for aiming (remove filter)"
		self.SetCurrentSetPoint(0)
		sleep(1)
		self.SetOutput(1)
		sleep(1)
		self.SetCurrentSetPoint(500)

	def Stop(self):
		print "Laser stopped"
		self.SetCurrentSetPoint(0)
		sleep(1)
		self.SetOutput(0)

if __name__=='__main__':
	ldd = NP560B()