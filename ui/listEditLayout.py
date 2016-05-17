from PyQt4 import QtGui, QtCore
import pyqtgraph as pg

class ListEditLayoutWidget(pg.LayoutWidget):

	def __init__(self):

		pg.LayoutWidget.__init__(self)
		self.add_btn = QtGui.QPushButton('Add')
		self.update_pos_btn = QtGui.QPushButton('Update pos.')
		self.goto_btn = QtGui.QPushButton('Go To')
		self.edit_btn = QtGui.QPushButton('Edit')
		self.del_btn = QtGui.QPushButton('Delete')
		self.act_btn = QtGui.QPushButton('Activate')
		self.act_btn.setStyleSheet("background-color: red;");
		self.addWidget(self.add_btn)
		self.addWidget(self.update_pos_btn)
		self.nextRow()
		self.addWidget(self.goto_btn)
		self.addWidget(self.edit_btn)
		self.nextRow()
		self.addWidget(self.del_btn)
		self.addWidget(self.act_btn)