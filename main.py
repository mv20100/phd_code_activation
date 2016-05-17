import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from PyQt4.QtCore import Qt
import pyqtgraph.console
from pyqtgraph.dockarea import *
import pyqtgraph.ptime as ptime
import numpy as np
import threading, time, traceback, sys
from drivers import *
from ui import *
from tasks.activationTask import ActivationTask
from tasks.analysisTask import AnalysisTask

default_data_dir = "G:\MOEMS group\Desktop\Data"
default_analysis_inerval = 15 # in minutes

class CellItem(object):

	def __init__(self,cellName,position):
		self.cellName = cellName
		self.position = position

class UpdateThread(pg.QtCore.QThread):

	newStageData = pg.QtCore.Signal(object,object)
	newLaserData = pg.QtCore.Signal(object)

	def __init__(self,stage,laserDrv):
		super(UpdateThread, self).__init__()
		self.stage = stage
		self.laserDrv = laserDrv
	
	def run(self):
		while True:
			if self.stage:
				self.newStageData.emit(self.stage.position,self.stage.isHomed)
			if self.laserDrv:
				self.newLaserData.emit(self.laserDrv.key_switch)  
			time.sleep(0.100)

class ScopeThread(pg.QtCore.QThread):

	newData = pg.QtCore.Signal()

	def __init__(self,scope):
		super(ScopeThread, self).__init__()
		self.scope = scope

	def run(self):
		while True:
			if self.scope:
				self.scope.update()
				self.newData.emit()
			time.sleep(0.05)

class MyWindow(QtGui.QMainWindow):

	def __init__(self,app):

		super(QtGui.QMainWindow,self).__init__()
		self.app = app

		self.data_dir = default_data_dir
		self.analysis_inerval = default_analysis_inerval

		saveAction = QtGui.QAction('Save', self)
		loadAction = QtGui.QAction('Load', self)
		cameraParamAction = QtGui.QAction('Settings', self)
		stageHomeAction = QtGui.QAction('Home', self)
		stageGoToAction = QtGui.QAction('Go To', self)
		analysisStartAction = QtGui.QAction('Start', self)
		analysisStopAction = QtGui.QAction('Stop', self)
		selectDirAction = QtGui.QAction('Select data folder', self)

		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&Cell list')
		fileMenu.addAction(saveAction)
		fileMenu.addAction(loadAction)
		fileMenu2 = menubar.addMenu('&Camera')
		fileMenu2.addAction(cameraParamAction)
		fileMenu3 = menubar.addMenu('&Stage')
		fileMenu3.addAction(stageHomeAction)
		fileMenu3.addAction(stageGoToAction)
		fileMenu4 = menubar.addMenu('&Analysis')
		fileMenu4.addAction(analysisStartAction)
		fileMenu4.addAction(analysisStopAction)
		fileMenu4.addAction(selectDirAction)

		area = DockArea()
		self.setCentralWidget(area)
		self.resize(1000,700)
		self.setWindowTitle('Activation setup')

		d_stage = Dock("XY stage", size=(1, 1))     ## give this dock the minimum possible size
		d_laser = Dock("Laser diode", size=(1,1))
		d_light = Dock("Light", size=(1,1))
		d_listedit = Dock("List edition", size=(1,1))
		d_camera = Dock("Camera", size=(1,1))
		d_scopeOp = Dock("Scope", size=(1,1))
		d_poslist = Dock("Position list", size=(320,1))
		d_console = Dock("Console", size=(1,1))
		d_camview = Dock("Camera view", size=(300,1))
		d_graph = Dock("Absorption graph", size=(300,1))

		area.addDock(d_stage, 'left')      ## place d1 at left edge of dock area (it will fill the whole space since there are no other docks yet)
		area.addDock(d_laser, 'bottom')
		area.addDock(d_light, 'bottom')
		area.addDock(d_camera, 'bottom')
		area.addDock(d_listedit, 'bottom')
		area.addDock(d_scopeOp, 'bottom')
		area.addDock(d_poslist, 'right')
		area.addDock(d_console, 'bottom')
		area.addDock(d_camview, 'right')
		area.addDock(d_graph, 'above', d_camview)

		# Stage widget
		self.w_stage = StageLayoutWidget()
		d_stage.addWidget(self.w_stage)

		# Laser diode ctrl widget
		self.w_laser = LaserLayoutWidget()
		d_laser.addWidget(self.w_laser)

		# Light ctrl widget
		self.w_light = LightLayoutWidget()
		d_light.addWidget(self.w_light)

		# List edition widget
		self.w_list_edit = ListEditLayoutWidget()
		d_listedit.addWidget(self.w_list_edit)

		self.w_scopeOp = ScopeOpWidget()
		d_scopeOp.addWidget(self.w_scopeOp)

		# Camera widget
		self.w_camera = CameraLayoutWidget()
		d_camera.addWidget(self.w_camera)

		# Position list widget
		self.w_table = MyTableWidget()
		d_poslist.addWidget(self.w_table)

		# Console widget
		text = """This is an interactive python console."""
		namespace = {'win': self}
		self.w_console = pyqtgraph.console.ConsoleWidget(text=text,namespace=namespace)
		# self.w_console.show()
		d_console.addWidget(self.w_console)

		self.w_camera_view = pg.GraphicsLayoutWidget()
		view = self.w_camera_view.addViewBox()
		view.setAspectLocked(True)
		img = pg.ImageItem()
		view.addItem(img)
		view.setRange(QtCore.QRectF(0, 0, 1024, 1280))
		d_camview.addWidget(self.w_camera_view)

		self.w_plot = MyGraphWidget()
		d_graph.addWidget(self.w_plot)

		# Load instuments #######################################

		print("Starting Light Controller")
		self.lightCtrl = LightCtrl(comPort='com4')

		try:
			print("Starting Laser Driver")
			self.laserDrv = NP560B()
		except:
			self.laserDrv = None
			print("Could not open Laser Driver")

		try:
			print("Starting Stage")
			self.stage = Stage()
		except:
			self.stage = None
			print("Could not open stage")

		try:
			print("Starting Camera")
			self.cam = UC480_Camera(id=1)
		except:
			self.cam = None
			print("Could not open camera")

		try:
			print("Starting Picoscope")
			self.scope = Picoscope()
			self.scope.initialize()
			self.w_plot.scope = self.scope
		except:
			self.scope = None
			print("Could not open picoscope")
			traceback.print_exc(file=sys.stdout)

		# Callbacks #############################################

		def home_stage():
			self.stage.moveHome(wait=False)

		def stage_goto():
			pass

		stageHomeAction.triggered.connect(home_stage)
		stageGoToAction.triggered.connect(stage_goto)

		def laser_on(pressed):
			if pressed:
				self.w_laser.on_btn.setText("Laser Off")		
			else:
				self.w_laser.on_btn.setText("Laser On")

		def laser_calibration():
			pass

		self.w_laser.on_btn.clicked.connect(laser_on)
		self.w_laser.cal_btn.clicked.connect(laser_calibration)

		def light_w_changed(value):
			self.lightCtrl.white(value)
			self.w_light.r_slider.setValue(value)
			self.w_light.g_slider.setValue(value)
			self.w_light.b_slider.setValue(value)

		def light_r_changed(value):
			self.lightCtrl.red(value)

		def light_g_changed(value):
			self.lightCtrl.green(value)

		def light_b_changed(value):
			self.lightCtrl.blue(value)

		self.w_light.w_slider.valueChanged.connect(light_w_changed)
		self.w_light.r_slider.valueChanged.connect(light_r_changed)
		self.w_light.g_slider.valueChanged.connect(light_g_changed)
		self.w_light.b_slider.valueChanged.connect(light_b_changed)

		def camera_grab(value):
			self.cam.freeze_frame()
			img.setImage(self.cam.image_array()[:,:,0:3],levels=(0,255)) # Remove the alpha channel which makes the image transparent

		def start_video():
			pass

		def stop_video():
			pass

		def camera_start_stop(pressed):
			if pressed:
				start_video()
				self.w_camera.live_btn.setText("Stop Video")
			else:
				stop_video()
				self.w_camera.live_btn.setText("Start Video")
				self.w_camera.status_lbl.setText("Stopped")

		self.w_camera.grab_btn.clicked.connect(camera_grab)
		self.w_camera.live_btn.clicked.connect(camera_start_stop)

		def list_load():
			fileName = QtGui.QFileDialog.getOpenFileName(self, 'Select file', '.', selectedFilter='*.tsv')
			if fileName:
				self.w_table.loadYaml(fileName)

		def list_save():
			fileName = QtGui.QFileDialog.getSaveFileName(self, 'Enter filename', '.', selectedFilter='*.tsv')
			if fileName:
				self.w_table.saveYaml(fileName)

		def list_add():
			default_name = "TXX_XX"
			current = self.w_laser.current_spinBox.value()
			time = self.w_laser.time_spinBox.value()
			status = "Waiting"
			self.w_table.appendRow([default_name,self.stage.position,current,time,status])

		def list_update():
			self.w_table.item(self.w_table.get_first_selected_row(),1).setValue(self.stage.position)

		def list_goto():
			position = self.w_table.item(self.w_table.get_first_selected_row(),1).value
			self.stage.moveAbsolute(position,wait=False)

		def list_edit():
			pass

		def list_del():
			self.w_table.delete_selected_rows()


		def list_activate():
			msgBox = QtGui.QMessageBox()
			msgBox.setText("Start the activation?")
			msgBox.setStandardButtons(QtGui.QMessageBox.No | QtGui.QMessageBox.Yes)
			msgBox.setDefaultButton(QtGui.QMessageBox.No)
			ret = msgBox.exec_()
			if ret == QtGui.QMessageBox.Yes:
				selection = get_selected_rows_idx()
				selection.sort()
				print("Starting activation")
				position = self.w_table.item(selection[0],1).value
				current = self.w_table.item(selection[0],2).value
				duration = self.w_table.item(selection[0],3).value
				actTask = ActivationTask(self,position=position,current=current,duration=duration)
				actTask.start()

		saveAction.triggered.connect(list_save)
		loadAction.triggered.connect(list_load)

		self.w_list_edit.add_btn.clicked.connect(list_add)
		self.w_list_edit.update_pos_btn.clicked.connect(list_update)
		self.w_list_edit.goto_btn.clicked.connect(list_goto)
		self.w_list_edit.edit_btn.clicked.connect(list_edit)
		self.w_list_edit.del_btn.clicked.connect(list_del)
		self.w_list_edit.act_btn.clicked.connect(list_activate)

		analysisStartAction.triggered.connect(self.startAnalysis)
		analysisStopAction.triggered.connect(self.stopAnalysis)
		selectDirAction.triggered.connect(self.selectDataDir)


		if self.scope:
			self.w_scopeOp.blank_btn.clicked.connect(self.scope.blankCapture)
		self.w_scopeOp.save_btn.clicked.connect(self.saveData)


		def updateStage(potision,isHomed):
			self.w_stage.xpos_lbl.setText("x: {0[0]:.3f}".format(potision))
			self.w_stage.ypos_lbl.setText("y: {0[1]:.3f}".format(potision))
			self.w_stage.status_lbl.setText("Homed: {}".format(isHomed))

		def updateLaser(key_switch):
			self.w_laser.status_lbl.setText("Key switch: {}".format(key_switch))


		self.thread = UpdateThread(self.stage,self.laserDrv)
		self.thread.newStageData.connect(updateStage)
		self.thread.newLaserData.connect(updateLaser)
		self.thread.start()


		self.thread2 = ScopeThread(self.scope)
		self.thread2.newData.connect(self.w_plot.update)
		self.thread2.start()

		self.w_table.loadYaml('positions.yaml')

		if self.stage and not self.stage.isHomed:
			msgBox = QtGui.QMessageBox()
			msgBox.setText("The staged is not homed, do you want to home it now?")
			msgBox.setStandardButtons(QtGui.QMessageBox.No | QtGui.QMessageBox.Yes)
			msgBox.setDefaultButton(QtGui.QMessageBox.No)
			ret = msgBox.exec_()
			if ret == QtGui.QMessageBox.Yes:
				self.stage.moveHome(wait=False)

	def saveData(self,cellName=None):
		if self.scope:
			meta = {}
			timeStr = time.strftime("%Y-%m-%d %H%M%S", time.gmtime())
			meta.update({"cellName":cellName})
			meta.update({"time":time.time()})
			meta.update({"bounds":self.w_plot.bounds})
			filenamePrefix = "CELL"
			if cellName: filenamePrefix = cellName
			filename = "{}\{} {}.p".format(self.data_dir,filenamePrefix,timeStr)
			self.scope.saveData(filename,meta=meta)

	def startAnalysis(self):
		cellItemList = []
		rows = self.w_table.get_rows()
		for row in rows:
			cellItem = CellItem(cellName=row[0],position=row[1])
			cellItemList.append(cellItem)
		self.analysisTask = AnalysisTask(self,cellItemList,interval_min=self.analysis_inerval)
		self.analysisTask.start()

	def stopAnalysis(self):
		if self.analysisTask:
			self.analysisTask.stop()

	def selectDataDir(self):
		dir_name = QtGui.QFileDialog.getExistingDirectory(self,"Select folder",self.data_dir,QtGui.QFileDialog.ShowDirsOnly)
		if dir_name:
			self.data_dir = dir_name


	def keyPressEvent(self, event):
		key = event.key()
		if not event.isAutoRepeat() and self.w_stage.keyboard_jog_cbx.checkState() == Qt.Checked:
			if key == QtCore.Qt.Key_Left:
				self.stage.jog_x(Stage.JOG_FWD)

			elif key == QtCore.Qt.Key_Right:
				self.stage.jog_x(Stage.JOG_REV)

			elif key == QtCore.Qt.Key_Up:
				self.stage.jog_y(Stage.JOG_FWD)

			elif key == QtCore.Qt.Key_Down:
				self.stage.jog_y(Stage.JOG_REV)

				
	def keyReleaseEvent(self,event):
		key = event.key()
		if not event.isAutoRepeat() and self.w_stage.keyboard_jog_cbx.checkState() == Qt.Checked: 
			if key == QtCore.Qt.Key_Left:
				self.stage.stop_x()

			elif key == QtCore.Qt.Key_Right:
				self.stage.stop_x()

			elif key == QtCore.Qt.Key_Up:
				self.stage.stop_y()

			elif key == QtCore.Qt.Key_Down:
				self.stage.stop_y()

	def terminate(self):
		self.thread.terminate()
		self.thread2.terminate()
		self.w_plot.saveBounds()
		if self.scope:
			self.scope.saveBackground()



app = QtGui.QApplication([])
app.setStyle("cleanlooks")
win = MyWindow(app)
win.show()

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
        win.terminate()
        time.sleep(1)