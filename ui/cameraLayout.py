from PyQt4 import QtGui, QtCore
import pyqtgraph as pg

class CameraLayoutWidget(pg.LayoutWidget):
	def __init__(self):
		pg.LayoutWidget.__init__(self)

		self.grab_btn = QtGui.QPushButton('Grab Image')
		self.live_btn = QtGui.QPushButton('Start Video')
		self.live_btn.setCheckable(True)
		self.status_lbl = QtGui.QLabel('FPS')
		self.addWidget(self.live_btn, row=0, col=0)
		self.addWidget(self.grab_btn, row=0, col=1)
		self.addWidget(self.status_lbl, row=1, col=0,colspan=2)