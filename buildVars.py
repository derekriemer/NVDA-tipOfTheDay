# -*- coding: UTF-8 -*-
import os
# Build customizations
# Change this file instead of sconstruct or manifest files, whenever possible.

# Full getext (please don't change)
_ = lambda x : x

# Add-on information variables
addon_info = {
	# for previously unpublished addons, please follow the community guidelines at:
	# https://bitbucket.org/nvdaaddonteam/todo/raw/master/guideLines.txt
	# add-on Name, internal for nvda
	"addon_name" : "tipOfTheDay",
	# Add-on summary, usually the user visible name of the addon.
	# Translators: Summary for this add-on to be shown on installation and add-on information.
	"addon_summary" : _("Tip Of The Day"),
	# Add-on description
	# Translators: Long description to be shown for this add-on on add-on information from add-ons manager
	"addon_description" : _("""The Tip of the day Addon allows beginner users to receive a tip of the day once a day. See it's documentation for more info."""),
	# version
	"addon_version" : "1.0.1",
	# Author(s)
	"addon_author" : u"derek Riemer <driemer.riemer@gmail.com>",
	# URL for the add-on documentation support
	"addon_url" : None,
	# Documentation file name
	"addon_docFileName" : "readme.html",
}


import os.path

# Define the python files that are the sources of your add-on.
# You can use glob expressions here, they will be expanded.
baseDir = os.path.join("addon", "globalPlugins")
pythonSources = [os.path.join(baseDir, "tip_of_the_day", "*.py"), os.path.join(baseDir, "tips.json")]

# Files that contain strings for translation. Usually your python sources
i18nSources = pythonSources + ["buildVars.py"]

# Files that will be ignored when building the nvda-addon file
# Paths are relative to the addon directory, not to the root directory of your addon sources.
def walkOver(dir):
	x=[]
	os.chdir("addon")
	for dir, dirnames, filenames in os.walk(dir):
		x+=map(lambda y:os.path.join(dir, y), filenames)
	os.chdir("..")
	return x

excludedFiles = walkOver("tests")
