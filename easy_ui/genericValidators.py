class GenericValueMap(object):
	"""A generic user input validator. To implement your own custom behavior for validating user input before functions get called, you should subclass this as it handles some things with the ui manager. """
	def __init__(self, n):
		""" The user need not worry about the details of the constructor. If you wish to write your own constructor, the burden of correctly interfacing with the ui manager is up to you. """
		if self._validate(n):
			return
		else: #Erronious input.
			raise ValueError("Bad option")
	
	def _validate(self, n):
		""" This function receives an input n (of type str) which is unsanitized and unvalidated. The job of the validator is to set self.validated to n' where n' is the value (in python) that should be passed to the callable by the ui manager. 
		@n: String of raw user input.
		@returns: True/false. True on success of setting self.validated, and False on failure. Note that False represents user error. 
		"""
		raise NotImplementedError


class YesNo(GenericValueMap):
	def _validate(self, n):
		n=n.lower()
		if n=="y" or n=="yes":
			self.validated = True
		elif n=="n" or n=="no":
			self.validated = False
		else:
			return False #Error on the users part.
		return True #success.

class TrueBool(GenericValueMap): #A boolean like on a test. 
	def _validate(self, n):
		n = n.lower()
		if n == "true":
			self.validated = True
			return True
		elif n == "false":
			self.validated = False
			return True
		else:
			return False

