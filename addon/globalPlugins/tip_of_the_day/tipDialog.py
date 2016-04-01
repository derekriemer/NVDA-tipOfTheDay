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

def confDialog(evt = None):
	conf = tipConfig.conf
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
	try:
		selection = choices.index(conf["user"]["level"])
	except (ValueError, KeyError):
		selection=0 #assume beginner if they don't have anything set yet.
	dialog.SetSelection(selection) 
	gui.mainFrame.prePopup()
	ret = dialog.ShowModal()
	gui.mainFrame.postPopup()
	if ret == wx.ID_OK:
		level = choices[dialog.GetSelection()]
		conf['user']['level'] = level
		conf.save()

class TipDialog(wx.Frame):
	def __init__(self):
		#Translators: The title of the tip of the day dialog.
		super(TipDialog, self).__init__(gui.mainFrame, wx.ID_ANY, title=_("Tip Of The Day"))
		self.new = True # no tips exist yet and we are needing more.
		self.panel  = panel = wx.Panel(self, wx.ID_ANY)
		mainSizer=wx.BoxSizer(wx.VERTICAL)
		tipSizer = wx.BoxSizer(wx.VERTICAL)
		self.tips  = getTips()
		if not self.tips:
			return #Critical error.
		self.index=tipConfig.conf["internal"]["index"]
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
		item = wx.Button(panel, wx.ID_CLOSE)
		self.Bind(wx.EVT_BUTTON, self.onClose, item)
		buttonSizer.Add(item)
		self.forward = item = wx.Button(panel, wx.ID_FORWARD)
		self.Bind(wx.EVT_BUTTON, self.onForward, item)
		buttonSizer.Add(item)
		self.prepButtons()
		mainSizer.Add(buttonSizer,border=20,flag=wx.LEFT|wx.RIGHT|wx.BOTTOM)
		mainSizer.Fit(panel)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.edit.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
		self.SetSizer(mainSizer)
		self.edit.SetFocus()

	def prepEdit(self):
		title, contents = self.tips[self.index]
		self.title.SetLabel(title)
		self.edit.SetValue(contents['description'])

	def prepButtons(self):
		#back button
		if self.index == 0:
			self.back.Enable(False)
			self.back.Hide()
		else:
			self.back.Enable(True)
			self.back.Show()
		#Forward button:
		if self.index == len(self.tips)-1:
			self.forward.Enable(False)
			self.forward.Hide()
		else:
			self.forward.Enable(True)
			self.forward.Show()

	def onForward(self, evt):
		self.index += 1
		self.prepEdit()
		self.prepButtons()
		self.edit.SetFocus()

	def onBack(self, evt):
		self.index -= 1
		self.prepEdit()
		self.prepButtons()
		self.edit.SetFocus()

	#Code from the NVDA Log Viewer. See source/gui/logViewer.py for the exact code.
	def onKeyDown(self, evt):
		key = evt.GetKeyCode()
		if key == wx.WXK_ESCAPE:
			self.Hide()
			self.save()
			return
		evt.Skip()

	def onClose(self, evt):
		self.Hide()
		self.save()

	def save(self):
		""" Saves the config. """
		tipConfig.conf["internal"]["index"] = self.index
		tipConfig.conf.save()

def create():
	#create a tips dialog.
	d = TipDialog()
	#Adapted from NVDA logViewer functions.
	gui.mainFrame.prePopup()
	d.Raise()
	# There is a MAXIMIZE style which can be used on the frame at construction, but it doesn't seem to work the first time it is shown,
	# probably because it was in the background.
	# Therefore, explicitly maximise it here.
	# This also ensures that it will be maximized whenever it is activated, even if the user restored/minimised it.
	d.Maximize()
	d.Show()
	gui.mainFrame.postPopup()


def initialize():
	conf = tipConfig.conf
	if conf['user']['level'] == 'not sure': #The default pop up a dialog.
		wx.CallAfter(confDialog) #pop the dialog when ready.
	menu = gui.mainFrame.sysTrayIcon.menu
	prefsMenu = gui.mainFrame.sysTrayIcon.preferencesMenu
	#Translators: Message for getting a tip of the day manually.
	item = menu.Append(wx.ID_ANY, _("Tip of the day"))
	menu.Bind(wx.EVT_MENU, onCreateTip, item)
	#Translators: Message for setting the tip of the day preferences.
	item = prefsMenu.Append(wx.ID_ANY, _("Tip of the day settings ..."))
	menu.Bind(wx.EVT_MENU, confDialog, item)

def onCreateTip(evt):
	create()

def getTips():
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
	return   tips.tips #tupal of tips.

initialize()