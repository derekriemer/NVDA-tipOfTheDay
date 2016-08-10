#__init__: Main plugin code.
#copyright Derek Riemer 2016.
#This code is GPL. See NVDA's license.
#All of NVDA's license and copying conditions apply here, including the waranty disclosure.
import datetime
import os
import time
import addonHandler
import globalPluginHandler
import globalVars
import queueHandler
import tipConfig
#We need to initialize the tip config before we import anything that relys on it.
tipConfig.initialize()
import tipDialog
import wx
from logHandler import log
#from tipsReader import Tips
from threading import Timer

addonHandler.initTranslation()

globalVars.TOD_timers = [] # TOD=tip of the day


class TipTimeManager:
	"""
	Class for checking if it's time for the tip of the day. We do this in a class rather than in the plugin so i can create one class per config item later when I have app-specific tips and such.
	"""
	
	def __init__(self, ord):
		""" 
		Excepts a time in seconds since the UTC epoc.
		"""
		self.__datetime = datetime.datetime.fromtimestamp(ord)
	
	def toNormalizedTime(self):
		""" Converts the internal representation into a time in seconds since the epoc for normalization purposes.
		"""
		return time.mktime(self.__datetime.timetuple())

	def hasMoreThanADayPassed(self):
		""" Returns true if this represents more than one day passing.
		"""
		return datetime.datetime.now()-datetime.timedelta(days=1) >= self.__datetime
	
	def alert(self, callBack):
		""" Registers a callback to for the event that the tip of the day dialog should pop up.
		@callBack: The callback taking absolutely no arguments at all.
		@type callback: Function.
		"""
		#We use internal functions here so we have access to self still (closures).
		def _alert():
			#we close over the callback.
			if self.hasMoreThanADayPassed():
				callBack()
			else:
				a = Timer(600, _alert) # 600 is 10 minutes.
				globalVars.TOD_timers.append(a)
				a.start()
		a = Timer(600,_alert) # 10 minutes.
		globalVars.TOD_timers.append(a)
		a.start()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super(globalPluginHandler.GlobalPlugin, self).__init__()
		tipDialog.initialize()
		conf = tipConfig.conf
		try:
			confVal = conf["internal"]["lastUse"]
		except KeyError:
			conf["internal"]["lastUse"] = time.time()
			confVal = conf["internal"]["lastUse"]
			conf.save()
		lastUse = TipTimeManager(confVal)
		if lastUse.hasMoreThanADayPassed():
			conf["internal"]["lastUse"] = time.time()
			conf.save()
			lastUse = TipTimeManager(conf['internal']['lastUse'])
			if conf["user"]["level"] != "not sure":
				queueHandler.queueFunction(queueHandler.eventQueue, tipDialog.create) #This should queue this to open in the future when NVDA is ready.
		self.purger() #gracefully remove dead timers.
		lastUse.alert(self) # runs a timer over and over every few minutes, and when the specified action happens, calls -the callback specified.

	def __call__(self): # calling this object with no arguments will work. This way we can use the class as the object to call.
		queueHandler.queueFunction(queueHandler.eventQueue, tipDialog.create) #This should queue this to open in the future when NVDA is ready. Seems to prevent an issue with the dialog not appearing thince this gets called randomly.
		lastUse = TipTimeManager(time.time())
		config = tipConfig.conf
		config["internal"]["lastUse"] = lastUse.toNormalizedTime()
		config.save()
		lastUse.alert(self) #register callBack again. If we die before the next day, that's fine, but we want to make sure the tip will pop up in one day if need be.
	
	def terminate(self):
		#cancel all timers from this plugin so NVDA can quit.
		for i in globalVars.TOD_timers:
			if i.is_alive():
				i.cancel()
		tipDialog.terminate()
	
	def purger(self):
			#timers might have died. Filter the global timers list so that dead timers can be garbage collected.
			globalVars.TOD_timers.append(Timer(600, self.purger))
			globalVars.TOD_timers[-1].start()
			def run():
				globalVars.TOD_timers = filter(lambda timer: timer.is_alive(), globalVars.TOD_timers) #check if alive for each timer and filter off of that.
			Timer(1, run).start() #bug: It gets activated before the other timer stops. wait a bit so the dead ones for sure have died thus far.


