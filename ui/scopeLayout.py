from PyQt4 import QtGui, QtCore
import pyqtgraph as pg

class ScopeOpWidget(pg.LayoutWidget):

	def __init__(self):

		pg.LayoutWidget.__init__(self)
		self.blank_btn = QtGui.QPushButton('Blank')
		self.fit_btn = QtGui.QPushButton('Fit')
		self.save_btn = QtGui.QPushButton('Save Data')
		self.addWidget(self.blank_btn)
		self.addWidget(self.fit_btn)
		self.nextRow()
		self.addWidget(self.save_btn)