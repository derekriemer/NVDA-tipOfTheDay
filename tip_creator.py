import collections
import json
import easy_ui

def save():
	with open("tips.json", "w") as f:
		json.dump(tips, f, separators = (",", " : "), indent=4)

def list():
	for i in tips["tips"].keys():
		print i


def add(title, level, description):
	if title in tips["tips"]:
		print "you already added this tip."
		return
	tip = {}
	if level not in xrange(1,7):
		print "bad level."
		return
	tip["level"] = [
		["beginner"], 
		["intermediate"],
		["advanced"],
		["beginner", "intermediate"],
		["intermediate", "advanced"],
		["beginner", "intermediate", "advanced"]
	][level-1]
	tip["description"] = description
	tips["tips"][title] = tip

ui = {
	"List Tips" : (
		list, 
	),
	"Add a Tip" : (
		add,
		(str, "Type your Title",),
		(int, "1 for beginner, 2 for intermediate, 3 for advanced, 4 for beginner and intermediate, 5 for intermediate and advanced, or 6 for all three.",),
		(str, "the tip, \n makes a new line.",),
	),
	"Save" : (
		save,
	)
}

with open("tips.json") as tipsFile:
	tips = json.load(tipsFile, object_pairs_hook=collections.OrderedDict)
easy_ui.Ui(ui) #runs the ui asking the user what they want.

