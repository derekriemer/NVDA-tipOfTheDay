#tipDialog: dialog and gui utilities for the tip of the day addon.
#copyright Derek Riemer 2016.
#This code is GPL. See NVDA's license.
#All of NVDA's license and copying conditions apply here, including the waranty disclosure.
import os
import wx
import gui
import tipConfig
import tipsReader
import queueHandler
from logHandler import log
from tipsReader import Tips

class TipDialog(wx.Frame):
	def __init__(self):
		#Translators: The title of the tip of the day dialog.
		super(TipDialog, self).__init__(gui.mainFrame, wx.ID_ANY, title=_("Tip Of The Day"))
		self.panel  = panel = wx.Panel(self, wx.ID_ANY)
		mainSizer=wx.BoxSizer(wx.VERTICAL)
		tipSizer = wx.BoxSizer(wx.VERTICAL)
		self.tip = tip = getTip() # yields a tip. 
		self.error = (not tip) # not tip will be true if None.
		self.queue = []
		self.index=0
		self.prepNextTip()
		self.title = item = wx.StaticText(panel)
		tipSizer.Add(item)
		self.edit = item = wx.TextCtrl(panel, size = (500,500), style =  wx.TE_READONLY|wx.TE_MULTILINE)
		tipSizer.Add(item)
		self.prepEdit()
		mainSizer.Add(tipSizer, border=20,flag=wx.LEFT|wx.RIGHT|wx.TOP)
		buttonSizer=wx.BoxSizer(wx.HORIZONTAL)
		self.back = item = wx.Button(panel, wx.ID_BACKWARD)
		buttonSizer.Add(item)
		self.Bind(wx.EVT_BUTTON, self.onBack, item)
		item.Hide()
		self.noBack = True
		item = wx.Button(panel, wx.ID_CLOSE)
		self.Bind(wx.EVT_BUTTON, self.onClose, item)
		buttonSizer.Add(item)
		self.forward = item = wx.Button(panel, wx.ID_FORWARD)
		self.noForward = False
		self.Bind(wx.EVT_BUTTON, self.onForward, item)
		buttonSizer.Add(item)
		mainSizer.Add(buttonSizer,border=20,flag=wx.LEFT|wx.RIGHT|wx.BOTTOM)
		mainSizer.Fit(panel)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.edit.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
		self.SetSizer(mainSizer)
		self.edit.SetFocus()

	def prepEdit(self):
		title, contents = self.queue[self.index-1]
		self.title.SetLabel(title)
		self.edit.SetValue(contents['description'])

	def prepButtons(self):
		if self.noBack:
			self.back.Hide()
		else:
			if not self.back.IsShown():
				self.back.Show()
		if self.noForward:
			self.forward.Hide()
		else:
			if self.IsShown:
				self.forward.Show()

	def prepNextTip(self):
		try:
			tip = next(self.tip)
			self.queue.append(tip)
			self.index += 1
		except StopIteration:
			self.noForward = True



	def onForward(self, evt):
		if self.noBack:
			self.noBack = False
		if self.index == len(self.queue): 
			# Prepair another tip to pop off the queue.
			self.prepNextTip()
		else: #No need to add a tip to the queue, user must have pressed back.
			self.index += 1
		self.prepEdit()
		self.prepButtons()
		self.edit.SetFocus()

	def onBack(self, evt):
		if self.noForward:
			self.noForward = False
		if self.index == 2:
			self.noBack = True
		self.index -= 1
		self.prepEdit()
		self.prepButtons()
		self.edit.SetFocus()

	#Code from the NVDA Log Viewer. See source/gui/logViewer.py for the exact code.
	def onKeyDown(self, evt):
		key = evt.GetKeyCode()
		if key == wx.WXK_ESCAPE:
			self.Hide()
			return
		evt.Skip()

	def onClose(self, evt):
		self.Hide()

def create():
	#create a tips dialog.
	d = TipDialog()
	#Adapted from NVDA logViewer functions.
	d.Raise()
	# There is a MAXIMIZE style which can be used on the frame at construction, but it doesn't seem to work the first time it is shown,
	# probably because it was in the background.
	# Therefore, explicitly maximise it here.
	# This also ensures that it will be maximized whenever it is activated, even if the user restored/minimised it.
	d.Maximize()
	d.Show()


def initialize():
	conf = tipConfig.conf
	if conf['user']['level'] == 'not sure': #The default pop up a dialog.
		def pop():
			choices = [
				#Translators: Choice for the level of expertise the user feels they have with windows.
				_("beginner"),
				#Translators: Choice for the level of expertise the user feels they have with Windows.
				_("intermediate"),
				#Translators: Choice for the level of expertise the user feels they have with windows.
				_("advanced"),
			]
			dialog = wx.SingleChoiceDialog(gui.mainFrame, 
				#translators: title of the panel that contains the choice of level of expertise.
				_("Select how familiar you are with  using your computer."), 
				#translators: title of a dialog asking the user how familiar they are with their computer.
				_("Familiarity With Windows"), choices=choices)
			dialog.SetSelection(0) #assume they are a beginner.
			gui.mainFrame.prePopup()
			ret = dialog.ShowModal()
			gui.mainFrame.postPopup()
			if ret == wx.ID_OK:
				level = choices[dialog.GetSelection()]
				conf['user']['level'] = level
				conf.save()
		wx.CallAfter(pop) #pop the dialog when ready.
	menu = gui.mainFrame.sysTrayIcon.menu
	#Translators: Message for getting a tip of the day manually.
	item = menu.Append(wx.ID_ANY, _("Tip of the day"))
	menu.Bind(wx.EVT_MENU, onCreateTip, item)

def onCreateTip(evt):
	create()

def getTip():
	# for now just load tips.json, until I implement the tips archive format.
	tips = None
	#translators: Error message for if tip reading fails.
	error = _("Error  loading tips. Your tips file is probably incorrect. Please reinstall it.")
	try:
		t=os.path.join(os.path.dirname(__file__), "tips.json")
		tips = Tips(t)
	except IOError as e:
		log.debug(e.message)
		gui.messageBox(error)
	except ValueError:
		log.debug("invalid json.")
		gui.messageBox(error)
	if not tips:
		return #Tip readingg failed for some reason.
	return   tips.yieldTip()

initialize()