from PyQt4 import QtGui, QtCore
import pyqtgraph as pg

class StageLayoutWidget(pg.LayoutWidget):
	def __init__(self):
		pg.LayoutWidget.__init__(self)

		self.keyboard_jog_cbx = QtGui.QCheckBox('Keyboard jog')
		self.xpos_lbl = QtGui.QLabel('x pos')
		self.ypos_lbl = QtGui.QLabel('y pos')
		self.status_lbl = QtGui.QLabel('Status')
		self.addWidget(self.keyboard_jog_cbx, row=0, col=0, colspan=2)
		self.addWidget(self.xpos_lbl, row=1, col=0)
		self.addWidget(self.ypos_lbl, row=1, col=1)
		self.addWidget(self.status_lbl, row=2, col=0, colspan=2)