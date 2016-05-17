from PyQt4 import QtGui, QtCore
import pyqtgraph as pg

class LaserLayoutWidget(pg.LayoutWidget):

	def __init__(self):

		pg.LayoutWidget.__init__(self)

		self.current_spinBox = QtGui.QSpinBox()
		self.current_spinBox.setSingleStep(100)
		self.current_spinBox.setMaximum(6000)
		self.time_spinBox = QtGui.QSpinBox()
		self.on_btn = QtGui.QPushButton('Laser On')
		self.cal_btn = QtGui.QPushButton('Calibration')
		self.on_btn.setCheckable(True)
		self.status_lbl = QtGui.QLabel('Status')
		self.addWidget(QtGui.QLabel('Current (mA)'), row=0, col=0)
		self.addWidget(self.current_spinBox, row=0, col=1)
		self.addWidget(QtGui.QLabel('Time (s)'), row=1, col=0)
		self.addWidget(self.time_spinBox, row=1, col=1)
		self.addWidget(self.on_btn, row=2, col=0)
		self.addWidget(self.cal_btn, row=2, col=1)
		self.addWidget(self.status_lbl, row=3, col=0, colspan=2)