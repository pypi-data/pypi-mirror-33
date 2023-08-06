# Created by george zhao, who is working for NOKIA, 2010-2012, 2014-2018.												#
# This lib is based on python 3.6.5																						#

from random import randint

from pyDiameter.pyDiaAVPTypes import DiaAVPGroup
from pyDiameter.pyDiaAVPFactory import DiaAVPFactory

from pyDiameter.pyDiaMessageConst import MSG_VERSION_BUFF_LEN
from pyDiameter.pyDiaMessageConst import MSG_LENGTH_BUFF_LEN
from pyDiameter.pyDiaMessageConst import MSG_FLAGS_BUFF_LEN
from pyDiameter.pyDiaMessageConst import MSG_COMMAND_CODE_BUFF_LEN
from pyDiameter.pyDiaMessageConst import MSG_APPLICATION_ID_BUFF_LEN
from pyDiameter.pyDiaMessageConst import MSG_HBH_BUFF_LEN
from pyDiameter.pyDiaMessageConst import MSG_E2E_BUFF_LEN
from pyDiameter.pyDiaMessageConst import MSG_HEADER_BUFF_LEN
from pyDiameter.pyDiaMessageConst import MSG_FLAGS_UNSET
from pyDiameter.pyDiaMessageConst import MSG_COMMAND_CODE_UNSET
from pyDiameter.pyDiaMessageConst import MSG_APP_ID_UNSET
from pyDiameter.pyDiaMessageConst import MSG_HBH_ID_UNSET
from pyDiameter.pyDiaMessageConst import MSG_E2E_ID_UNSET


from pyDiameter.pyDiaConst import ZERO_LEN_BYTES
from pyDiameter.pyDiaConst import DEFAULT_BYTES_ORDER

class DiaMessage:
	def __init__(self):
		self.__version = 0x01			# Only Diameter Version 1 is supported by this lib.								#
		self.__flags = MSG_FLAGS_UNSET
		self.__commandCode = MSG_COMMAND_CODE_UNSET
		self.__applicationID = MSG_APP_ID_UNSET
		self.__hbhID = MSG_HBH_ID_UNSET
		self.__e2eID = MSG_E2E_ID_UNSET
		self.__avps = []
		
	# For properties operations																							#
	def getE2EID(self):
		return self.__e2eID
	def setE2EID(self, e2eID):
		self.__e2eID = e2eID
		
	def getHBHID(self):
		return self.__hbhID
	def setHBHID(self, hbhID):
		self.__hbhID = hbhID
		
	def setFlags(self, flags):
		self.__flags = flags
	def getFlags(self):
		return self.__flags
	def setRequestFlag(self):
		self.__flags = self.__flags | 0x80
	def clearRequestFlag(self):
		self.__flags = self.__flags & 0x7F
	def getRequestFlag(self):
		if 1 == (self.__flags & 0x80) >> 7: return True
		return False
	def setProxyableFlag(self):
		self.__flags = self.__flags | 0x40
	def clearProxyableFlag(self):
		self.__flags = self.__flags & 0xBF
	def getProxyableFlag(self):
		if 1 == (self.__flags & 0x40) >> 6: return True
		return False
	def setEBitFlag(self):
		self.__flags = self.__flags | 0x20
	def clearEBitFlag(self):
		self.__flags = self.__flags & 0xDF
	def getEBitFlag(self):
		return (self.__flags & 0x20) >> 5
	def setTBitFlag(self):
		self.__flags = self.__flags | 0x10
	def clearTBitFlag(self):
		self.__flags = self.__flags & 0xEF
	def getTBitFlag(self):
		return (self.__flags & 0x10) >> 4
		
	def setCommandCode(self, cmdCode):
		self.__commandCode = cmdCode
	def getCommandCode(self):
		return self.__commandCode
		
	def setApplicationID(self, appID):
		self.__applicationID = appID
	def getApplicationID(self):
		return self.__applicationID
		
	def generateHBHID(self):
		self.setHBHID(randint(0, 0xffffffff))
	def generateE2EID(self):
		self.setE2EID(randint(0, 0xffffffff))
		
	# getAVPs() is just a function use to debug, will be removed after release#
	def getAVPs(self):
		return self.__avps		
		
		
	# By using DiaAVPPath object, this function can help user to visit AVP directly.									#
	# avpPath parameter should be initialed first by using AVP path language, like 10145/1400[0]->0/493[0]				#
	def getAVPByPath(self, avpPath):
		fakeRoot = DiaAVPGroup()
		fakeRoot.setAVPValue(self.__avps)
		avp = fakeRoot.getAVPByPath(avpPath)
		del fakeRoot
		return avp
		
	# By using DiaAVPPath object, this function can help user to add AVP directly.										#
	# groupAVPPath parameter should be initialed first by using AVP path language, like 10145/1400[0]->0/493[0]			#
	# Note that, groupAVPPath is the father avp which contains the avp you want to add.									#
	# groupAVPPath must be a group type AVP, or you can leave groupAVPPath a blank, avp will be added at root.			#
	def addAVPByPath(self, groupAVPPath, avp, index = -1):
		fakeRoot = DiaAVPGroup()
		fakeRoot.setAVPValue(self.__avps)
		r = fakeRoot.addAVPByPath(groupAVPPath, avp, index)
		del fakeRoot
		return r
		
	# By using DiaAVPPath object, this function can help user to remove AVP directly.									#
	# avpPath parameter should be initialed first by using AVP path language, like 10145/1400[0]->0/493[0]				#
	def removeAVPByPath(self, avpPath):
		fakeRoot = DiaAVPGroup()
		fakeRoot.setAVPValue(self.__avps)
		r = fakeRoot.removeAVPByPath(avpPath)
		del fakeRoot
		return r
			
	# decode tools functions																							#
	# decode tools functions need bytes buff as their parameters, not string.											#		
	# decode an integer value.		
	@classmethod																		#
	def decodeUIntValue(self, intValueBytes):
		assert type(intValueBytes) is bytes
		return int.from_bytes(intValueBytes, DEFAULT_BYTES_ORDER)
		
	# decode only diameter message part.																				#
	def __decodeMessageHeader(self, headerBytesBuff):
		p = 0
		version = self.decodeUIntValue(headerBytesBuff[p:p+MSG_VERSION_BUFF_LEN])
		p += MSG_VERSION_BUFF_LEN
		if self.__version != version:
			raise RuntimeError("Diameter version is not 1 but", version)
		# Length value is ignored.
		p += MSG_LENGTH_BUFF_LEN
		flags = self.decodeUIntValue(headerBytesBuff[p:p+MSG_FLAGS_BUFF_LEN])
		self.setFlags(flags)
		p += MSG_FLAGS_BUFF_LEN
		cmdCode = self.decodeUIntValue(headerBytesBuff[p:p+MSG_COMMAND_CODE_BUFF_LEN])
		self.setCommandCode(cmdCode)
		p += MSG_COMMAND_CODE_BUFF_LEN
		appID = self.decodeUIntValue(headerBytesBuff[p:p+MSG_APPLICATION_ID_BUFF_LEN])
		self.setApplicationID(appID)
		p += MSG_APPLICATION_ID_BUFF_LEN
		hbhID = self.decodeUIntValue(headerBytesBuff[p:p+MSG_HBH_BUFF_LEN])
		self.setHBHID(hbhID)
		p += MSG_HBH_BUFF_LEN
		e2eID = self.decodeUIntValue(headerBytesBuff[p:p+MSG_E2E_BUFF_LEN])
		self.setE2EID(e2eID)
		
	# decode diameter message from a bytes-like buffer to the object.													#
	def decode(self, bytesBuff):
		assert type(bytesBuff) is bytes
		self.__decodeMessageHeader(bytesBuff[0:MSG_HEADER_BUFF_LEN])
		avpsBytesBuff = DiaAVPGroup.cutAVPBytes(bytesBuff[MSG_HEADER_BUFF_LEN:])
		avpFactory =  DiaAVPFactory ()
		for avpBuffsBuff in avpsBytesBuff:
			avp = avpFactory.generateDiaAVPObject(avpBuffsBuff)
			if not None == avp:
				self.__avps.append(avp)
			else:
				raise RuntimeError("Got a Null Pointor when decoding Diameter AVP.")
		
	# encode tools functions																							#
	# encode tools will output bytes, not string.																		#
	# encode an integer value.																							#
	def encodeUIntValue(self, intValue, intValueLength):
		return intValue.to_bytes(intValueLength, DEFAULT_BYTES_ORDER)
		
	# decode only diameter message part.																				#
	def __encodeMessageHeader(self):
		r = ZERO_LEN_BYTES
		r += self.encodeUIntValue(self.__version, MSG_VERSION_BUFF_LEN)
		r += self.encodeUIntValue(len(self), MSG_LENGTH_BUFF_LEN)
		r += self.encodeUIntValue(self.getFlags(), MSG_FLAGS_BUFF_LEN)
		r += self.encodeUIntValue(self.getCommandCode(), MSG_COMMAND_CODE_BUFF_LEN)
		r += self.encodeUIntValue(self.getApplicationID(), MSG_APPLICATION_ID_BUFF_LEN)
		r += self.encodeUIntValue(self.getHBHID(), MSG_HBH_BUFF_LEN)
		r += self.encodeUIntValue(self.getE2EID(), MSG_E2E_BUFF_LEN)
		return r
		
	# encode this object to a bytes-like buffer.																		#
	def encode(self):
		r = ZERO_LEN_BYTES
		r += self.__encodeMessageHeader()
		for avp in self.__avps:
			r += avp.encode()
		return r
	
	# Override the len operator.
	def __len__(self):
		r = MSG_HEADER_BUFF_LEN
		for avp in self.__avps:
			r += len(avp)
		return r