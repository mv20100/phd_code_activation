import visa

class PM100USB(object):
	def __init__(self,powerMeterID="P2005322"):
		devID = "USB0::0x1313::0x8072::"+powerMeterID+"::INSTR"
		rm = visa.ResourceManager()
		self.inst = rm.open_resource(devID,read_termination='\n')

	def getPower(self):
		self.inst.write("READ?")
		data = float(self.inst.read())*1e6
		return data
		
	def getPowerUnit(self):
		self.inst.write("POWer:UNIT?")
		data = self.inst.read()
		return data
	
if __name__=='__main__':
	pwm = PM100USB()