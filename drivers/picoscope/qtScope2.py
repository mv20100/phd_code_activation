# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
from pico import Picoscope

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.scope = Picoscope()
        self.scope.initialize()

        self.plotLayout = pg.GraphicsLayoutWidget()
        self.setCentralWidget(self.plotLayout)
        self.plot = self.plotLayout.addPlot(row=0, col=0)
        self.plot.setYRange(0,0.3)
        yellow = [pg.mkPen((255, 255, 0,50)),pg.mkPen((255, 255, 0,255))]
        cyan = [pg.mkPen((0, 255, 255,50)),pg.mkPen((0, 255, 255,255))]
        red = [pg.mkPen((255, 0, 0,50)),pg.mkPen((255, 0, 0,255))]
        self.curve_dataA = self.plot.plot(pen=yellow[0])
        self.curve_dataB = self.plot.plot(pen=cyan[0])
        self.curve_dataC = self.plot.plot(pen=red[0])
        self.curve_meanA = self.plot.plot(pen=yellow[1])
        self.curve_meanB = self.plot.plot(pen=cyan[1])
        self.curve_meanC = self.plot.plot(pen=red[1])

        self.resize(600, 600)
        self.show()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def update(self):
        
        self.scope.update()
        self.curve_dataA.setData(self.scope.x, self.scope.dataA[self.scope.ptr,:])
        self.curve_dataB.setData(self.scope.x, self.scope.dataB[self.scope.ptr,:])
        self.curve_dataC.setData(self.scope.x, self.scope.dataC[self.scope.ptr,:])
        self.curve_meanA.setData(self.scope.x, self.scope.meanA)
        self.curve_meanB.setData(self.scope.x, self.scope.meanB)
        self.curve_meanC.setData(self.scope.x, self.scope.meanC)

if __name__ == '__main__':
    app = QtGui.QApplication([])
    win = MainWindow()
    app.exec_()    

