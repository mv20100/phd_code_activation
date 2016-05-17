import wx.lib.activex
import threading
import comtypes.client as cc
import comtypes.automation as ca
from ctypes import byref, pointer, c_long, c_float, c_bool

cc.GetModule( ('{2A833923-9AA7-4C45-90AC-DA4F19DC24D1}', 1, 0) )
progID_motor = 'MGMOTOR.MGMotorCtrl.1'
import comtypes.gen.MG17MotorLib as APTMotorLib
break_type_switch = APTMotorLib.HWLIMSW_BREAKS
make_type_switch = APTMotorLib.HWLIMSW_MAKES
units_mm = APTMotorLib.UNITS_MM
home_rev = APTMotorLib.HOME_REV
homelimsw_rev = APTMotorLib.HOMELIMSW_REV_HW
motor_moving_bits =  -2147478512
motor_stopped_not_homed_bits = -2147479552
motor_stopped_and_homed_bits = -2147478528

class MGMotor(object):
	"""The Motor class derives from wx.lib.activex.ActiveXCtrl, which
	   is where all the heavy lifting with COM gets done."""
	
	def __init__( self, parent, HWSerialNum, id=wx.ID_ANY, pos=wx.DefaultPosition,
				 size=wx.DefaultSize, style=0, name='Stepper Motor' ):
		self.activex = wx.lib.activex.ActiveXCtrl(parent, progID_motor,id, pos, size, style, name)
		self.ctrl = self.activex.ctrl
		self.ctrl.HWSerialNum = HWSerialNum
		self.channel = APTMotorLib.CHAN1_ID # or APTMotorLib.CHAN2_ID ?
		print("Starting Motor Driver: {}".format(str(HWSerialNum)))
		self.ctrl.StartCtrl()
		returnCode = self.enableHWChannel()
		if returnCode!=0:
			self.enabled = False
			print("Connection Error")
			raise ValueError('Could not enable HW channel')
		else:
			print("Connection OK")
			self.enabled = True
			self.hwLimSwitches = (make_type_switch,make_type_switch) # lRevLimSwitch, lFwdLimSwitch
			self.stageAxisInfo = (0.0, 120.0, 1.0, units_mm, 1) # minpos, maxpos, pitch, units, direction
			self.homeParams = (home_rev, homelimsw_rev, 3, 0.1) # direction, switch,velocity, zero_offset 
			self.velParams = (0.0, 1.0, 2.0) # minvelocity, acceleration, maxvelocity
			self.jogVelParams = (0.0, 1.0, 2.0) # minvelocity, acceleration, maxvelocity
			self.jogMode = (APTMotorLib.JOG_CONTINUOUS, APTMotorLib.STOP_IMMEDIATE) # jogmode, stopmode
			self.jogStepSize = 1
			# self.bLashDist = 0.01

	# def __del__(self):
	# 	if self.enabled:
	# 		self.close()

	# def close(self):
	# 	self.disableHWChannel()
	# 	# self.ctrl.StopCtrl()
	# 	self.enabled = False

	# Read and write properties
	@property
	def absMovePos(self):
		pos = c_float()
		self.ctrl.GetAbsMovePos(self.channel,byref(pos))
		return pos.value

	@absMovePos.setter
	def absMovePos(self, pos):
		self.ctrl.SetAbsMovePos(self.channel,pos)

	@property
	def hwLimSwitches(self,):
		plRevLimSwitch = c_long()
		plFwdLimSwitch = c_long()
		self.ctrl.GetHWLimSwitches( self.channel, byref(plRevLimSwitch),byref(plFwdLimSwitch) )
		return plRevLimSwitch.value, plFwdLimSwitch.value
	
	@hwLimSwitches.setter
	def hwLimSwitches(self,  lRev_lFwd_lim_switches):
		lRevLimSwitch, lFwdLimSwitch = lRev_lFwd_lim_switches
		self.ctrl.SetHWLimSwitches(self.channel,lRevLimSwitch,lFwdLimSwitch)

	@property
	def jogStepSize(self):
		stepsize = c_float()
		self.ctrl.GetJogStepSize(self.channel, byref(stepsize))
		return stepsize.value

	@jogStepSize.setter
	def jogStepSize(self, stepsize):
		self.ctrl.SetJogStepSize(self.channel,stepsize)
	
	@property
	def bLashDist(self):
		backlash = c_float()
		self.ctrl.SetBLashDist( self.channel,byref(backlash))
		return backlash.value

	@bLashDist.setter
	def bLashDist(self, backlash):
		self.ctrl.SetBLashDist( self.channel, backlash)
	
	@property
	def stageAxisInfo(self):
		min_position = c_float()
		max_position = c_float()
		units = c_long()
		pitch = c_float()
		direction = c_long()
		self.ctrl.GetStageAxisInfo(self.channel, byref(min_position),byref(max_position), byref(units),byref(pitch), byref(direction))
		return min_position.value, max_position.value, units.value, pitch.value, direction.value

	@stageAxisInfo.setter
	def stageAxisInfo(self, infos):
		minpos, maxpos, units, pitch, direction = infos
		self.ctrl.SetStageAxisInfo( self.channel, minpos, maxpos, units, pitch, direction)

	@property
	def homeParams(self):
		direction = c_long()
		switch = c_long()
		velocity = c_float()
		zero_offset = c_float()
		self.ctrl.GetHomeParams(self.channel, byref(direction), byref(switch), byref(velocity), byref(zero_offset))
		return direction.value, switch.value, velocity.value, zero_offset.value

	@homeParams.setter
	def homeParams(self, hpars):
		direction, switch, velocity, zero_offset = hpars
		self.ctrl.SetHomeParams( self.channel, direction, switch, velocity, zero_offset)
	
	@property
	def velParams(self):
		minvelocity = c_float()
		maxvelocity = c_float()
		acceleration = c_float()
		self.ctrl.GetVelParams(self.channel, byref(minvelocity), byref(acceleration), byref(maxvelocity))
		return minvelocity.value, acceleration.value, maxvelocity.value

	@velParams.setter
	def velParams(self, vPars):
		minvelocity, acceleration, maxvelocity = vPars
		self.ctrl.SetVelParams(self.channel, minvelocity, acceleration, maxvelocity)
		
	@property
	def jogVelParams(self):
		minvelocity = c_float()
		maxvelocity = c_float()
		acceleration = c_float()
		self.ctrl.GetJogVelParams(self.channel, byref(minvelocity), byref(acceleration), byref(maxvelocity))
		return minvelocity.value, acceleration.value, maxvelocity.value

	@jogVelParams.setter
	def jogVelParams(self, jvPars):
		minvelocity, acceleration, maxvelocity = jvPars
		self.ctrl.SetJogVelParams(self.channel, minvelocity, acceleration, maxvelocity)

	@property
	def jogMode(self):
		mode, stopMode = c_long(), c_long()
		self.ctrl.GetJogMode(self.channel,byref(mode),byref(stopMode))
		return mode.value, stopMode.value

	@jogMode.setter
	def jogMode(self, mode_stopMode):
		mode, stopMode = mode_stopMode
		self.ctrl.SetJogMode(self.channel,mode,stopMode)

	# Read only properties
	@property
	def statusBits_Bits(self):
		return self.ctrl.GetStatusBits_Bits(self.channel)

	@property
	def isMoving(self):
		return (self.statusBits_Bits>>4)&0b11 # Get the 5th and 6th bit

	@property
	def isHomed(self):
		return (self.statusBits_Bits>>10)&0b1

	@property
	def position(self):
		position = c_float()
		self.ctrl.GetPosition(self.channel, byref(position))
		return position.value
	
	# Methods
	def enableHWChannel(self):
		return self.ctrl.EnableHWChannel(self.channel)

	def disableHWChannel(self):
		self.ctrl.DisableHWChannel(self.channel)

	def moveAbsolute(self,wait=True):
		self.ctrl.MoveAbsolute(self.channel,wait)

	def moveHome(self,wait=True):
		self.ctrl.MoveHome(self.channel,wait)
	
	def moveJog(self,jogDir=APTMotorLib.JOG_FWD):
		return self.ctrl.MoveJog(self.channel,jogDir)

	def stopImmediate(self):
		return self.ctrl.StopImmediate( self.channel )
		
	def stopProfiled(self):
		return self.ctrl.StopProfiled( self.channel )


class StageApp( wx.App ): 
	def __init__( self, redirect=False, filename=None ):
		wx.App.__init__( self, redirect, filename )
		self.frame = wx.Frame( None, wx.ID_ANY, title='MG17MotorControl' )
		self.panel = wx.Panel( self.frame, wx.ID_ANY )

class Stage():
	center_position = (60,60)
	JOG_FWD = APTMotorLib.JOG_FWD
	JOG_REV = APTMotorLib.JOG_REV

	def __init__( self):
		self.app=StageApp()
		self.motor1 = MGMotor( self.app.panel, HWSerialNum=90861957, style=wx.SUNKEN_BORDER )
		self.motor2 = MGMotor( self.app.panel, HWSerialNum=90861958, style=wx.SUNKEN_BORDER )
		self.motor2.stageAxisInfo = (0.0, 150.0, 1.0, units_mm, 1) #Extend the range up to 150 mm

	# def __del__(self):
	# 	self.close()

	# def close(self):
	# 	self.motor1.close()
	# 	self.motor2.close()
	# 	# self.motor1.ctrl.StopCtrl()
	
	@property
	def position(self):
		return self.motor1.position,self.motor2.position

	@property
	def isHomed(self):
		if self.motor1.isHomed and self.motor2.isHomed:
			return True
		return False

	@property
	def isMoving(self):
		if self.motor1.isMoving>0 or self.motor2.isMoving>0:
			return True
		return False
	
	def moveHome(self,wait=True):
		def thread(motor):
			motor.moveHome(wait=True)			
		t1 = threading.Thread(name="thread",target=thread,args=(self.motor1,))
		t2 = threading.Thread(name="thread",target=thread,args=(self.motor2,))
		t1.start()
		t2.start()
		if wait:
			t1.join()
			t2.join()
	
	def stopImmediate(self):
		self.motor1.stopImmediate()
		self.motor2.stopImmediate()

	def moveAbsolute(self,(x,y),wait=True):
		self.motor1.absMovePos = x
		self.motor2.absMovePos = y
		def thread(motor):
			motor.moveAbsolute(wait=True)			
		t1 = threading.Thread(name="thread",target=thread,args=(self.motor1,))
		t2 = threading.Thread(name="thread",target=thread,args=(self.motor2,))
		t1.start()
		t2.start()
		if wait:
			t1.join()
			t2.join()
	
	def homeAndCenter(self,wait=True):
		self.motor1.absMovePos, self.motor2.absMovePos = self.center_position
		def thread(motor):
			motor.moveHome(wait=True)
			motor.moveAbsolute(wait=True)			
		t1 = threading.Thread(name="thread",target=thread,args=(self.motor1,))
		t2 = threading.Thread(name="thread",target=thread,args=(self.motor2,))
		t1.start()
		t2.start()
		if wait:
			t1.join()
			t2.join()

	def jog_x(self,jogDir=JOG_FWD):
		self.motor1.moveJog(jogDir)

	def jog_y(self,jogDir=JOG_FWD):
		self.motor2.moveJog(jogDir)

	def stop_x(self):
		self.motor1.stopImmediate()

	def stop_y(self):
		self.motor2.stopImmediate()

if __name__ == "__main__":
	stage = Stage()