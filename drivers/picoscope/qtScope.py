# -*- coding: utf-8 -*-
#
# Based on code from Luke Campagnola, author of amazing pyqtgraph library

from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
from picoscope import ps3000a

def setupScope():
    ps = ps3000a.PS3000a("CO138/046")


    sampleFreq = 500E3 #S/s
    collectionTime = 10e-3 # sec
    noSamples = collectionTime*sampleFreq
    #Example of simple capture
    (sampleRate, nSamples)  = ps.setSamplingFrequency(sampleFreq, noSamples)
    print "Sampling @ %f MHz, %d samples"%(sampleRate/1E6, nSamples)
    ps.setChannel("A", "DC", 0.2,-0.2)
    ps.setChannel("B", "DC", 0.2,-0.2)
    ps.setChannel("C", "DC", 0.2,0.0)
    ps.setSimpleTrigger("External",0.5, 'Rising', timeout_ms=0,delay=int(noSamples*0.23))
        # SIGGEN_TRIGGER_TYPES = {"Rising": 0, "Falling": 1,
        #                     "GateHigh": 2, "GateLow": 3}
    return [ps, sampleRate]

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.plotLayout = pg.GraphicsLayoutWidget()
        self.setCentralWidget(self.plotLayout)
        self.specPlot = self.plotLayout.addPlot(row=0, col=0)
        self.specPlot.setYRange(0,0.3)
        self.curveA = self.specPlot.plot(pen='y')
        self.curveB = self.specPlot.plot(pen='c')
        self.curveC = self.specPlot.plot(pen='r')

        self.resize(600, 600)
        self.show()

        [self.scope, self.rate] = setupScope()
        self.scopeRunning = False

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

        self.trigAvg = np.zeros(5000)
        self.lastValue = None
        self.lastData = None
        self.persistent = []
        self.lastUpdate = None
        
    
    def update(self):
        now = pg.ptime.time()
        if self.lastUpdate is None:
            self.lastUpdate = now
            dt = 0.0
        else:
            dt = now - self.lastUpdate
            self.lastUpdate = now
        
        ## read data from sound device
        if self.scopeRunning == False:
            self.scope.runBlock()
            self.scopeRunning = True

        if self.scope.isReady():
            data = self.scope.getDataV("A", 4096)
            data2 = self.scope.getDataV("B", 4096)
            data3 = self.scope.getDataV("C", 4096)
            self.scopeRunning = False
        else:
            data = []

        if self.scopeRunning == False:
            self.scope.runBlock()

        if len(data) > 0:
            self.curveA.setData(range(0,len(data)), data)
            self.curveB.setData(range(0,len(data2)), data2)
            self.curveC.setData(range(0,len(data3)), data3)
            self.lastData = data


    def keyPressEvent(self, ev):
        if ev.text() == ' ':
            if self.timer.isActive():
                self.timer.stop()
            else:
                self.timer.start()
        else:
            print ev.key()

if __name__ == '__main__':
    app = QtGui.QApplication([])
    win = MainWindow()
    app.exec_()    

