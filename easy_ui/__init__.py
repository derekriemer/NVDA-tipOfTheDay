from __future__ import print_function
from genericValidators import *
from sys import version

#monkeypatch python 2's stupid builtin input function to replace it with something safe.
if version[0] == "2":
	input = raw_input



class Ui:
	def initialize_menu(self):
		print("{options:^40}\n\n".format(options="options:"))
		print("{index:<10}{item:>10}".format(item="exit", index=0))

		for index, item in enumerate(self.funcDict.keys()):
			print("{index:<10}{item:>10}".format(item=item, index=index+1))
		self.max=len(list(self.funcDict.keys()))

	def getraw_input(self):
		while True:
			try:
				self.choice=int(input("enter your choice"))
				if self.choice>self.max or self.choice < 0:
					raise ValueError("Value too large")
				break
			except KeyboardInterrupt as e:
				exit()
			except ValueError as e:
				if str(e)=="Value too large":
					print("item not in the menu.")
				else:
					print("That was a bad option you gave me.\nEnter one of the numbers above.")
				self.initialize_menu()
				continue
		if 0 == self.choice:
			print("Good Bye, Exiting program.")
			exit()


	def callIt(self):
		option=list(self.funcDict.values())[self.choice-1] # get the 3-toople.
		#an option is a toople of the function, and then a toople of 2-tooples with items in the form of (type, prompt)  
		args=[]
		for theType, toPrint in option[1:]:
			while True:
				print("{:^20}".format(toPrint))
				#types provided by the class to make life easier.
				#This is a map of genaric types, or miscellaneous types, and their respective built-in helper. If the python type is the same as the builtin type to map on then just put the same thing on both sides of the mapping.
				#To get at the actual type that we should have, a self.validated variable should be provided with what we want to actually give the function. See the YesNo typeclass for an example.
				inMap = False # if it is in the map we set this to True.
				self.validators.update({
					bool : YesNo,
					TrueBool : TrueBool
				} )
				if theType in self.validators:
					inMap = True
					theOldType = theType
					theType = self.validators[theOldType]
				try:
					that = theType(str(input()))
					if inMap:
						args.append(that.validated)
					else:
						args.append(that)
					break
				except ValueError:
					print("{:^20}".format("bad option? Try entering that again."))
		option[0](*args) #call it with our just built list of arguements.


	def __init__(self, funcDict, validators = {}, once = True):
		self.funcDict=funcDict
		self.validators = validators
		loop=True
		while loop:
			self.initialize_menu()
			loop=once
			self.getraw_input()
			self.callIt() #choice is passed in on self.choice so we don't need to send it in here.










