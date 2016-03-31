#tips Reader: Utilities for reading tips.
#copyright Derek Riemer 2016.
#This code is GPL. See NVDA's license.
#All of NVDA's license and copying conditions apply here, including the waranty disclosure.
import sys, os
#This snippet is used from the NVDA Remote Addon.
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import json
sys.path.remove(sys.path[-1])
#end-snippet.

class Tips:

	def __init__(self, fn):
		self.tipsDict = j=None
		self.tips = []
		with open(fn,"r") as tipsFile:
			self.tipsDict = j = json.load(tipsFile)
		if j and j['tips']:
			self.tips.extend(j['tips'].keys()) # load dict into self.
		self.app=None
		if j and j.get('type') == 'app':
			#app specific tips.
			self.app = self.tipsDict['appname']
	
	def getTip(self, tipName):
		""" Gets a tip from the json.
		@tip: The tip to get. Must be a string.
		@type tip: String
		"""
		return (self.tipsDict['tips'][tipName] if tipName in self.tips else None) #if it contains a tip, return it otherwise return none.
	
	def __iter__(self):
		return iter(self.tips) # and iterator of tips.

	def yieldTip(self):
		""" Yields a tip to present.
		"""
		for tip in self:
			yield (tip, self.getTip(tip))
