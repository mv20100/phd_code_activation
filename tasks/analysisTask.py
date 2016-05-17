import threading, time
from apscheduler.schedulers.blocking import BlockingScheduler


class AnalysisTask(object):

	def __init__(self,parent,cellList,interval_min=1):
		# cellList is a list of CellItem
		super(AnalysisTask, self).__init__()
		self.parent = parent
		self.cellList = cellList
		self.stage = parent.stage
		self.interval_min = interval_min
		self.taskOn = True
		self.scheduler = BlockingScheduler()

	def start(self):
		self.t = threading.Thread(target=self.analyseJob,args=(None,))
		self.t.start()

	def stop(self):
		self.taskOn = False
		if self.scheduler.running:
			self.scheduler.shutdown()
			print("Scheduler stopped")

		# self.t.join()

	def analyseJob(self,s):
		self.scheduler.add_job(self.analyseList, 'interval', minutes=self.interval_min)
		self.analyseList()
		self.scheduler.start()

	def analyseList(self):
		analysis_start_time = time.time()
		print("Starting cell analysis")
		for cellItem in self.cellList:
			self.analyseCell(cellItem)
			if not self.taskOn:
				print("AnalysisTask stopped")
				return 
		now = time.time()
		next_analysis_time = analysis_start_time + 60*self.interval_min
		waiting_time = next_analysis_time - now
		next_analysis_time_str = time.strftime("%d %b %Y %H:%M:%S",time.localtime(next_analysis_time))
		print("Next analysis in {} min (on {})".format(waiting_time/60,next_analysis_time_str))

	def analyseCell(self,cellItem):
		print("Going to cell {}".format(cellItem.cellName))
		self.stage.moveAbsolute(cellItem.position,wait=True)
		assert self.stage.position == cellItem.position
		self.parent.saveData(cellItem.cellName)