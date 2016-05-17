import picoscope, time
import matplotlib.pyplot as plt
import numpy as np
from picoscope.ps3000a import PS3000a
from collections import deque
from PyQt4 import QtGui, QtCore
import pickle
import os.path

class Picoscope(object):
	
	mean = 32

	def __init__(self,serialNumber="CO138/046"):
		self.serialNumber = serialNumber
		self.ps = PS3000a(serialNumber)

	def __del__(self):
		self.saveBackground()

	def initialize(self):
		self.samples = 4096
		sampleFreq = 500E3 #S/s
		collectionTime = 10e-3 # sec
		noSamples = collectionTime*sampleFreq
		#Example of simple capture
		(self.sampleRate, self.nSamples)  = self.ps.setSamplingFrequency(sampleFreq, noSamples)
		print "Sampling @ %f MHz, %d samples"%(self.sampleRate/1E6, self.nSamples)
		self.ps.setChannel("A", "DC", 0.5,-0.4)
		self.ps.setChannel("B", "DC", 0.5,-0.4)
		self.ps.setChannel("C", "DC", 0.2,0.0)
		self.ps.setSimpleTrigger("External",0.5, 'Rising', timeout_ms=0,delay=int(noSamples*0.23))

		self.x = range(0,self.samples)
		self.meanA = np.zeros(self.samples,dtype=np.float64)
		self.dataA = np.zeros((self.mean,self.samples),dtype=np.float64)
		self.meanB = np.zeros(self.samples,dtype=np.float64)
		self.dataB = np.zeros((self.mean,self.samples),dtype=np.float64)
		self.meanC = np.zeros(self.samples,dtype=np.float64)
		self.dataC = np.zeros((self.mean,self.samples),dtype=np.float64)

		self.backgroundB = None

		self.cleanB = None

		self.ptr = 0
		self.deque = deque([],self.mean)

		self.loadBackground()

	def update(self):
		self.ptr=(self.ptr+1)%self.mean
		self.deque.append(self.ptr)
		self.ps.runBlock()
		self.ps.waitReady()
		self.dataA[self.ptr,:] = self.ps.getDataV("A", self.samples)
		self.dataB[self.ptr,:] = self.ps.getDataV("B", self.samples)
		self.dataC[self.ptr,:] = self.ps.getDataV("C", self.samples)

		if len(self.deque)>0:
			self.meanA=np.mean(self.dataA[self.deque],axis=0)
			self.meanB=np.mean(self.dataB[self.deque],axis=0)
			self.meanC=np.mean(self.dataC[self.deque],axis=0)
			if self.backgroundB is not None:
				self.cleanB = self.meanB/self.backgroundB

	def blankCapture(self):
		self.backgroundB = np.array(self.meanB)

	def saveBackground(self):
		if self.backgroundB is not None:
			print("Saving background data")
			pickle.dump(self.backgroundB, open('background.p', 'wb'))
			print("Done")

	def loadBackground(self):
		if os.path.isfile('./background.p'): 
			print("Loading background data")
			pkl_file = open('background.p', 'rb')
			data = pickle.load(pkl_file)
			self.backgroundB = np.array(data)
			pkl_file.close()

	def saveData(self,filename,bounds=None,meta=None):
		self.deque.clear()
		while len(self.deque)<self.mean:
			time.sleep(0.050)
		data = {}
		data.update(meta)
		data.update({"meanA":self.meanA})
		data.update({"meanB":self.meanB})
		data.update({"meanC":self.meanC})
		data.update({"cleanB":self.cleanB})
		data.update({"backgroundB":self.backgroundB})
		print("Saving data")
		pickle.dump(data, open(filename, 'wb'))
		print("Done")

if __name__ == "__main__":
	pico = Picoscope()
