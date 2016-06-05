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

def confDialog(evt = None, createAfter = False):
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
		if createAfter:
			wx.CallAfter(create)

class TipDialog(wx.Frame):
	def __init__(self):
		#Translators: The title of the tip of the day dialog.
		super(TipDialog, self).__init__(gui.mainFrame, wx.ID_ANY, title=_("Tip Of The Day"))
		self.panel  = panel = wx.Panel(self, wx.ID_ANY)
		mainSizer=wx.BoxSizer(wx.VERTICAL)
		tipSizer = wx.BoxSizer(wx.VERTICAL)
		self.tips  = getTips()
		if not self.tips:
			return #Critical error.
		self.index=tipConfig.conf["internal"]["index"]
		self.level = tipConfig.conf["user"]["level"]
		self.title = item = wx.StaticText(panel)
		tipSizer.Add(item)
		self.edit = item = wx.TextCtrl(panel, size = (500,500), style =  wx.TE_READONLY|wx.TE_MULTILINE)
		tipSizer.Add(item)
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
		mainSizer.Add(buttonSizer,border=20,flag=wx.LEFT|wx.RIGHT|wx.BOTTOM)
		mainSizer.Fit(panel)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.edit.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
		self.SetSizer(mainSizer)
		self.edit.SetFocus()
		self.cache = []
		self.superIndex = 0
		noShow = True
		for i in range(len(self.tips)):
			if  self.level in self.tips[i][1]["level"]:
				self.cache.append(i)
				if i == self.index:
					self.superIndex = len(self.cache)-1
					noShow = False
		# when the tips wrap, it'll reset to 0. We should notify the user the tips wrapped however.
		if noShow:
			gui.messageBox(
				#Translators: Message for when the user has seen all possible tips.
				_("You have seen all possible tips. The add-on will now show you the first tip again."),
				#Translators: The title of the dialog that shows up when the user has seen all tips.
				_("Out of Tips")				)
				
		self.prepEdit()
		self.prepButtons()

	def prepEdit(self):
		title, contents = self.tips[self.cache[self.superIndex]]
		self.title.SetLabel(title)
		self.edit.SetValue(contents['description'])

	def prepButtons(self):
		#back button
		if self.superIndex == 0:
			self.back.Enable(False)
			self.back.Hide()
		else:
			self.back.Enable(True)
			self.back.Show()
		#Forward button:
		if self.superIndex == len(self.cache)-1:
			self.forward.Enable(False)
			self.forward.Hide()
		else:
			self.forward.Enable(True)
			self.forward.Show()

	def onForward(self, evt):
		self.superIndex += 1
		self.prepEdit()
		self.prepButtons()
		self.edit.SetFocus()
		self.edit.SelectAll()

	def onBack(self, evt):
		self.superIndex -= 1
		self.prepEdit()
		self.prepButtons()
		self.edit.SetFocus()
		self.edit.SelectAll()

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
		try:
			tipConfig.conf["internal"]["index"] = self.cache[self.superIndex+1]
		except IndexError:
			tipConfig.conf["internal"]["index"] = -1 #force the dialog at boot next time.
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
		wx.CallAfter(confDialog, createAfter = True) #pop the dialog when ready.
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
		dir = os.path.dirname(__file__)
		dir = os.path.split(dir)[0]
		t=os.path.join(dir, "tips.json")
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