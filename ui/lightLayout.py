from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
import pyqtgraph as pg

class LightLayoutWidget(pg.LayoutWidget):

	def __init__(self):
		pg.LayoutWidget.__init__(self)
		
		self.w_slider = QtGui.QSlider(Qt.Horizontal)
		self.r_slider = QtGui.QSlider(Qt.Horizontal)
		self.g_slider = QtGui.QSlider(Qt.Horizontal)
		self.b_slider = QtGui.QSlider(Qt.Horizontal)
		for slider in [self.w_slider,self.r_slider,self.g_slider,self.b_slider]:
			slider.setMinimum( 0)
			slider.setMaximum(255)
		self.addWidget(QtGui.QLabel('W'), row=0, col=0)
		self.addWidget(self.w_slider, 	 row=0, col=1)
		self.addWidget(QtGui.QLabel('R'), row=1, col=0)
		self.addWidget(self.r_slider, 	 row=1, col=1)
		self.addWidget(QtGui.QLabel('G'), row=2, col=0)
		self.addWidget(self.g_slider,	 row=2, col=1)
		self.addWidget(QtGui.QLabel('B'), row=3, col=0)
		self.addWidget(self.b_slider,	 row=3, col=1)