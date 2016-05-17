import threading, time


class ActivationTask(object):

	def __init__(self,parent,position=None,current=None,duration=None):
		super(ActivationTask, self).__init__()
		self.position = position
		self.current = current
		self.duration = duration
		self.stage = parent.stage
		self.laserDrv = parent.laserDrv

	def start(self):
		t = threading.Thread(target=self.activate)
		t.start()

	def activate(self):
		self.stage.moveAbsolute(self.position,wait=True)
		assert stage.position == self.position
		self.laserDrv.current_set_point = 0
		print("Laser On")
		self.laserDrv.output = 1
		print("Waiting for laser output to turn on")
		time.sleep(5)
		print("Current set")
		self.laserDrv.current_set_point = self.current
		time.sleep(self.duration)
		print("Stopping")
		self.laserDrv.current_set_point = 0
		time.sleep(1)
		print("Laser Off")
		self.laserDrv.output = 0