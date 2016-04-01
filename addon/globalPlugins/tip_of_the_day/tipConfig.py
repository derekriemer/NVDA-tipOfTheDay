#tipConfig: Config handling for the tip of the day addon.
#copyright Derek Riemer 2016.
#This code is GPL. See NVDA's license.
#All of NVDA's license and copying conditions apply here, including the waranty disclosure.
import os
from cStringIO import StringIO
import config
import configobj
import validate
#adapted from the config in OCR, to be a module.
#Uses some of NVDA's internal conventions as well.

configspec = StringIO("""
	[internal]
		lastUse=float(min=0 default=0)
		index = integer(min=0, default=0)
	[user]
		level = option('not sure', 'beginner', 'intermediate', 'advanced', default='not sure')
""")

class TipConf(object):
	def __init__(self):
		""" Initializes config for the tip of the day addon.  """
		path = os.path.join(config.getUserDefaultConfigPath(), "tip_of_day.ini")
		self._config  = configobj.ConfigObj(path, configspec=configspec, indent_type = '\t')
		val = validate.Validator()
		self._config.validate(val)

	def __getitem__(self, key):
		return self._config[key]

	def __setitem__(self, key, val):
		self._config[key] = val

	def save(self):
		self._config.write()

conf = None

def initialize():
	global conf
	conf = TipConf()
