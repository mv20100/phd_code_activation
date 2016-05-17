from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import pickle, os.path


class MyGraphWidget(pg.GraphicsLayoutWidget):

	def __init__(self):

		self.scope = None
		pg.GraphicsLayoutWidget.__init__(self)

		self.plot = self.addPlot()
		# self.plot.setYRange(0,0.3)
		yellow = [pg.mkPen((255, 255, 0,50)),pg.mkPen((255, 255, 0,255))]
		cyan = [pg.mkPen((0, 255, 255,50)),pg.mkPen((0, 255, 255,255))]
		red = [pg.mkPen((255, 0, 0,50)),pg.mkPen((255, 0, 0,255))]
		self.curve_dataA = self.plot.plot(pen=yellow[0])
		self.curve_dataB = self.plot.plot(pen=cyan[0])
		self.curve_dataC = self.plot.plot(pen=red[0])
		self.curve_meanA = self.plot.plot(pen=yellow[1])
		self.curve_meanB = self.plot.plot(pen=cyan[1])
		self.curve_meanC = self.plot.plot(pen=red[1])

		self.bounds = None
		self.lr = pg.LinearRegionItem([10,4000])
		self.lr.setZValue(-10)
		self.plot.addItem(self.lr)

		self.nextRow()
		self.plot2 = self.addPlot()
		self.curve_blankB = self.plot2.plot(pen='g')

		self.lr.sigRegionChanged.connect(self.updateBounds)

		self.nextRow()
		self.label = pg.LabelItem(justify='right')
		self.addItem(self.label)
		self.label.setText("Test")

		self.loadBounds()

	def updateBounds(self):
		self.bounds = (int(self.lr.getRegion()[0]),int(self.lr.getRegion()[1]))
		self.plot2.setXRange(*self.lr.getRegion(), padding=0)

	def update(self):
		self.curve_dataA.setData(self.scope.x, self.scope.dataA[self.scope.ptr,:])
		self.curve_dataB.setData(self.scope.x, self.scope.dataB[self.scope.ptr,:])
		self.curve_dataC.setData(self.scope.x, self.scope.dataC[self.scope.ptr,:])
		self.curve_meanA.setData(self.scope.x, self.scope.meanA)
		self.curve_meanB.setData(self.scope.x, self.scope.meanB)
		self.curve_meanC.setData(self.scope.x, self.scope.meanC)
		if self.scope.cleanB is not None:
			if self.bounds:
				x1 = max(0,self.bounds[0])
				x2 = min(len(self.scope.x),self.bounds[1])
			else:
				x1 = 0
				x2 = len(self.scope.x)
			self.curve_blankB.setData(self.scope.x[x1:x2], self.scope.cleanB[x1:x2])
			maxi = max(self.scope.cleanB[x1:x2])
			mini = min(self.scope.cleanB[x1:x2])
			contrast =  (maxi-mini)/maxi
			self.label.setText("Contrast: {:.3f} %".format(contrast*100))

	def saveBounds(self):
		if self.bounds is not None:
			print("Saving bounds")
			pickle.dump(self.bounds, open('bounds.p', 'wb'))
			print("Done")

	def loadBounds(self):
		if os.path.isfile('./bounds.p'): 
			print("Loading bounds")
			pkl_file = open('bounds.p', 'rb')
			data = pickle.load(pkl_file)
			self.bounds = data
			self.lr.setRegion(self.bounds)
			pkl_file.close()