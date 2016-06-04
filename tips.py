import  wx
import sys
import json

class TipsDisplay(wx.Panel):

	def __init__(self, parent, tip=None):
		""" Tips page. Is shown when adding or editing a tip.
		@var parent: The parent frame that initiates this.
		@type parent: Window.
		@var tip: the tiip object which contains the tip to edit. If None we are adding a tip.
		@type tip: Tip
		"""
		super(TipsDisplay,self).__init__(parent, size=(800,600))
		self.parent = parent
		if tip is None:
			self.parent.SetTitle("Add A Tip")
			title=""
		else:
			self.parent.SetTitle("edit"+tip[0])
			title = tip[0]
		sizer = wx.BoxSizer(wx.VERTICAL)
		contents_sizer = wx.BoxSizer(wx.HORIZONTAL)
		title_sizer = wx.BoxSizer(wx.VERTICAL)
		title_label=wx.StaticText(self, label="Title")
		title_sizer.Add(title_label)
		title_text = wx.TextCtrl(self, value = title)
		title_sizer.Add(title_text)
		contents_sizer.Add(title_sizer)
		level_sizer = wx.BoxSizer(wx.VERTICAL)
		level_text = wx.StaticText(self, label = "Level of knowledge")
		level_sizer.Add(level_text)
		self.level_choices = ("Beginner", "Intermediate", "Advanced", "Beginner and Intermediate", "Intermediate and Advanced", "Beginner, Intermediate,  and Advanced")
		level_list = wx.Choice(self, choices = self.level_choices)
		if tip is not None:
			level = tip.level
			s=0
			if len(level) == 1:
				l=level[0]
				if l == "intermediate":
					s=1
				elif l == "advanced":
					s=2
			elif len(level) == 2:
				s = (3 if level[0] == "beginner" else 4) #we don't want the level to be beginner and advanced, so just ignore the second one.
			else:
				s == 5
			level_list.SetSelection(s)
		level_sizer.Add(level_list)
		contents_sizer.Add(level_sizer)
		sizer.Add(contents_sizer)
		multiLine_sizer = wx.BoxSizer(wx.VERTICAL)
		tip_sizer = wx.BoxSizer(wx.VERTICAL)
		tip_label=wx.StaticText(self, label="Tip Text")
		tip_sizer.Add(tip_label)
		tip_text = wx.TextCtrl(self, style=wx.TE_MULTILINE)
		tip_sizer.Add(tip_text, flag=wx.EXPAND)
		multiLine_sizer.Add(tip_sizer)
		sizer.Add(contents_sizer)
		choices_sizer = wx.BoxSizer(wx.HORIZONTAL)
		ok = wx.Button(self, wx.ID_OK)
		choices_sizer.Add(ok)
		cancel = wx.Button(self, wx.ID_CANCEL)
		choices_sizer.Add(cancel)
		sizer.Add(choices_sizer)
		self.SetSizer(sizer)
		self.Center()

class TipList(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, wx.ID_ANY, size=(800,600))
		self.parent = parent
		choices = []
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		tips = openTips("tips.json")
		for tip in tips["tips"]:
			choices.append(tip)
		self.choices = choices
		self.list_box = list_box = wx.Choice(self, wx.ID_ANY, choices=choices)
		main_sizer.Add(list_box)
		button_sizer = wx.BoxSizer(wx.VERTICAL)
		add_tip_button = wx.Button(self, wx.ID_ANY, label="&Add")
		add_tip_button.Bind(wx.EVT_BUTTON, self.onAdd)
		button_sizer.Add(add_tip_button)
		main_sizer.Add(button_sizer)
		self.SetSizer(main_sizer)
		main_sizer.Fit(self)
		self.list_box.SetFocus()

	def onAdd(self, evt):
		self.parent.notify(evt)



def openTips(fileName):
	""" Returns tips for the file.
	@fileName: The file name.
	@type fileName: String
	"""
	with open(fileName) as file:
		return json.load(file) #desearialize


app=wx.App()
class Frame(wx.Frame):
	def __init__(self, parent, title):
		super(Frame,self).__init__(parent, title=title,size=(800,600))
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.main = main = TipList(self)
		sizer.Add(main)
		self.display = display = TipsDisplay(self)
		sizer.Add(display)
		main.Show()
		display.Hide()
		self.SetSizer(sizer)
		self.Center()
		self.main = True

	def notify(self, evt):
		if self.main:
			self.main.Hide()
			self.display.Show()
		else:
			self.display.Hide()
			self.main.Show()
		self.Layout()
		self.main = not self.main
		self.Bind



if __name__=='__main__':
	frame=Frame(None,"Tip manager.")
	frame.Show()
		app.MainLoop()

