# Example code for multiple video display
# -*- coding: utf-8 -*-
# based on pyqtgraph\examples\ImageItem.py
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
import pyqtgraph.ptime as ptime
from drivers.camera.uc480 import UC480_Camera

app = QtGui.QApplication([])
win = pg.GraphicsLayoutWidget()
win.show() 
win.setWindowTitle('multi-video display')
win.setGeometry(200,200,1000,700)

cam = UC480_Camera(id=1)
cam.start_live_video(None)
cam.stop_live_video()
cam.start_live_video(None)

class VideoView:
    def __init__(self, r,c):
        self.view = win.addViewBox(row=r, col=c)
        self.view.setAspectLocked(True)
        self.img = pg.ImageItem(border='k')
        self.view.addItem(self.img)
        self.view.setRange(QtCore.QRectF(0, 0, 600, 600))
        self.data = np.random.normal(size=(15, 600, 600), loc=1024, scale=64).astype(np.uint16)
        self.i = 0
        self.updateTime = ptime.time()
        self.fps = 0

    def updateData(self):

        # self.img.setImage(self.data[self.i])
        self.img.setImage(cam.image_array()[:,:,0:3],levels=(0,255),autoDownsample=True)
        self.i = (self.i+1) % self.data.shape[0]

        QtCore.QTimer.singleShot(1, self.updateData)
        now = ptime.time()
        fps1 = 1.0 / (now-self.updateTime)
        self.updateTime = now
        self.fps = self.fps * 0.9 + fps1 * 0.1
        if self.i == 0:
            print "%0.1f fps" % self.fps

coords = [[x,y] for x in range(0,1) for y in range(0,1)]
views = []
for (x,y) in coords:
    views.append(VideoView(x,y))
for v in views:
    v.updateData()

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()