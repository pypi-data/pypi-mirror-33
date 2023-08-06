# Created by george zhao, who is working for NOKIA, 2010-2012, 2014-2018.												#
# This lib is based on python 3.6.5																						#

from pyDiameter.pyDiaAVPConst import AVP_ARRAY_DEFAULT
from pyDiameter.pyDiaAVPConst import NAME_KEY, TYPE_KEY
from pyDiameter.pyDiaAVPConst import AVP_TYPE_UNKNOWN
from pyDiameter.pyDiaAVPConst import AVP_NAME_NONE

# DiaAVPDict is used to clarify the class DiaAVPDict, which is contained a default dictionary,							#
# in this default dictionary, almost diameter AVPs were stored, including their name, code, verdor and type.			#		
# But anyway, this default dictionary could not contains all AVP registered in all specifications all over the world.	#
# it only contains a popular AVPs' definition, e.g. base diameter, and 3gpp (10415).									#
# The DiaAVPDict class provide methods to add your own AVP definitions, when you run your app based on it.				#

class DiaAVPDict():
	__instance=None

	def __new__(cls, *args, **kwargs):
		if cls.__instance is None:
			cls.__instance = super().__new__(cls)
		return cls.__instance
		
	def __init__(self):
		self.__avpDict = AVP_ARRAY_DEFAULT
		
	# Create a new vendor in default dictionary.																		#
	def __createAVPVendor(self, avpVendor):
		self.__avpDict[avpVendor]={}
		
	# Create a new AVP code in a vendor scope in default dictionary.													#
	def __createAVPCode(self ,avpVendor, avpCode):
		self.__avpDict[avpVendor][avpCode]={}
		
	# Judge whether Vendor is defined in default dictionary.															#
	def hasVendorDef(self, avpVendor):
		if avpVendor in self.__avpDict:
			return True
		return False
		
	# Judge whether AVP is exist in default dictionary. If yes, True will be returned, and False for not.				#
	def hasAVPDef(self, avpVendor, avpCode):
		if avpVendor in self.__avpDict:
			if avpCode in self.__avpDict[avpVendor]:
				return True
		return False
		
	# Add AVP definition if relavant definition is not exist in default dictionary.										#
	# If AVP is already exist in default dictionary, this function will raise an KeyError, 								#
	# with comment "Key is already exist, please use function updateAVPDef() to update the AVP definition"				#
	# avpType should be one of CONSTs, TYPE_STR, TYPE_INT32, TYPE_INT64, TYPE_GROUP										#
	def addAVPDef(self, avpVendor, avpCode, avpName, avpType):
		if self.hasAVPDef(avpVendor, avpCode):
			raise KeyError("AVP vendor and code is already exist, please use function updateAVPDef() to update the AVP definition.")
			return False
		if not self.hasVendorDef(avpVendor):
			self.__createAVPVendor(avpVendor)
		self.__createAVPCode(avpVendor, avpCode)
		self.__avpDict[avpVendor][avpCode][NAME_KEY] = avpName
		self.__avpDict[avpVendor][avpCode][TYPE_KEY] = avpType
		return True
		
	# Update AVP definition according to parameters.																	#
	# If AVP is not exist in default dictionary, this function will raise an KeyError,									#
	# with comment "Key is not exist, please use function addAVPDef() to add new AVP definition."						#
	# avpType should be one of CONSTs, TYPE_STR, TYPE_INT32, TYPE_INT64, TYPE_GROUP										#
	def updateAVPDef(self, avpVendor, avpCode, avpName, avpType):
		if not self.hasVendorDef(avpVendor):
			raise KeyError("AVP vendor is not exist, please use function addAVPDef() to add new AVP definition.")
			return False			
		if not self.hasAVPDef(avpVendor, avpCode):
			raise KeyError("AVP code is not exist, please use function addAVPDef() to add new AVP definition.")
			return False
		self.__avpDict[avpVendor][avpCode][NAME_KEY] = avpName
		self.__avpDict[avpVendor][avpCode][TYPE_KEY] = avpType
		return True		
	
	# In this version, delete the AVP definition is not supported currently.											#
	def deleteAVPDef(self, avpVendor, avpCode):
		raise NotImplementedError("The function deleteAVPDef() is not implementated currently.")

	# get AVP name by using vendor and code.
	def getAVPDefName(self, avpVendor, avpCode):
		if self.hasAVPDef(avpVendor, avpCode):
			return self.__avpDict[avpVendor][avpCode][NAME_KEY]
		return AVP_NAME_NONE
	
	# get AVP type by using vendor and code.
	def getAVPDefType(self, avpVendor, avpCode):
		if self.hasAVPDef(avpVendor, avpCode):
			return self.__avpDict[avpVendor][avpCode][TYPE_KEY]
		return AVP_TYPE_UNKNOWN

# end of class DiaAVPDict
