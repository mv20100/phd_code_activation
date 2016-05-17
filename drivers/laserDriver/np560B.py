__author__  = "Vincent Maurice"
from time import time, sleep
import numpy as np
from ctypes import *

lib = WinDLL("M530DLL.dll") 
# Functions descriptions of this lib can be found in the NewpDll.h file (Newport C++ samples)
productID = 0x1001

class NP560B(object):
	"""
	Controls for Newport 560B laser diode driver (with Newport's default driver)
	"""

	def __init__(self):		
		status = lib.newp_usb_init_system()
		if status != 0:
			raise ValueError('Laser diode driver: could not init system')
			print("Laser diode driver init system status: {}".format(status))
			return None
		numDev = self._newp_usb_open_devices(bUseUSBAddress=False)
		if numDev == 0:
			raise ValueError('Laser diode driver: no device')
			print("Laser diode driver: no device")
			return None
		self.deviceID = 0
		print("Laser diode driver connection open")

	def __del__(self):
		lib.newp_usb_uninit_system()
		print("Laser diode driver connection closed")

	def _newp_usb_open_devices(self,bUseUSBAddress=False):
		c_nNumDevices = c_int()
		lib.newp_usb_open_devices (c_int(productID), c_bool(bUseUSBAddress), byref(c_nNumDevices))
		return c_nNumDevices.value

	def _newp_usb_send_ascii(self,command):
		return lib.newp_usb_send_ascii(c_long(self.deviceID),c_char_p(command), c_ulong(len(command)))

	def _newp_usb_get_ascii(self):
		buffLen = 60
		buff = c_char_p(" "*buffLen)
		bytesRead = c_ulong(0)
		status = lib.newp_usb_get_ascii(c_long(self.deviceID),buff,c_ulong(buffLen),byref(bytesRead))
		return buff.value[:bytesRead.value-2]  #Strip the \r\n termination characters.

	#Lantz like functions
	def query(self,command):
		self._newp_usb_send_ascii(command)
		# print(command)
		return self._newp_usb_get_ascii()

	def send(self,command):
		# print(command)
		self._newp_usb_send_ascii(command)

	#Read only properties

	@property
	def key_switch(self):
		"""
		Returns key switch ON/OFF status.
		"""
		return bool(int(self.query("KEY?")))

	@property
	def hw_temp(self):
		"""
		Returns instrument temperture in degC.
		"""
		return int(self.query("HWTemp?"))

	@property
	def current(self):
		"""
		Get measured laser current in mA.
		"""
		return float(self.query("LAS:LDI?"))

	@property
	def pd_current(self):
		"""
		Get measured photodiode current.
		"""
		return float(self.query("LAS:MDI?"))

	@property
	def fwd_voltage(self):
		"""
		Get measured forward voltage in V.
		"""
		return float(self.query("LAS:LDV?"))

	#Read and write properties

	@property
	def current_set_point(self):
		"""
		Get laser current set point in mA.
		"""
		return float(self.query("LAS:SET:LDI?"))

	@current_set_point.setter
	def current_set_point(self, current):
		"""
		Set laser current set point in mA.
		"""
		self.send("LASer:LDI {}".format(int(current)))

	@property
	def current_limit(self):
		"""
		Get the value of the laser current limit in mA.
		"""
		return float(self.query("LAS:LIM:LDI?"))

	@current_limit.setter
	def current_limit(self, currentLim):
		"""
		Set the value of the current limit in mA.
		"""
		self.send("LAS:LIM:LDI {}".format(int(current_limit)))

	@property
	def output(self):
		"""
		Get status of the laser output.
		"""
		return int(self.query("LAS:OUT?"))

	@output.setter
	def output(self, state):
		"""
		Turns the laser output on or off.
		"""
		self.send("LAS:OUT {}".format(int(state)))

	#Methods

	def local(self):
		"""
		Makes front panel buttons active.
		"""
		self.send("LOCAL")

if __name__=='__main__':
	ldd = NP560B()