# Created by george zhao, who is working for NOKIA, 2010-2012, 2014-2018.												#
# This lib is based on python 3.6.5																						#

from struct import unpack, pack
from pyDiameter.pyDiaAVPBase import DiaAVP

from pyDiameter.pyDiaAVPBasicTypesConst import AVP_VALUE_INT32_BUFF_LEN
from pyDiameter.pyDiaAVPBasicTypesConst import AVP_VALUE_UINT32_BUFF_LEN
from pyDiameter.pyDiaAVPBasicTypesConst import AVP_VALUE_INT64_BUFF_LEN
from pyDiameter.pyDiaAVPBasicTypesConst import AVP_VALUE_UINT64_BUFF_LEN
from pyDiameter.pyDiaAVPBasicTypesConst import AVP_VALUE_FLOAT32_BUFF_LEN
from pyDiameter.pyDiaAVPBasicTypesConst import AVP_VALUE_FLOAT64_BUFF_LEN
from pyDiameter.pyDiaAVPConst import AVP_LENGTH_BUFF_LEN
from pyDiameter.pyDiaConst import ZERO_LEN_BYTES
from pyDiameter.pyDiaConst import DEFAULT_BYTES_ORDER_2
from pyDiameter.pyDiaAVPFactory import DiaAVPFactory
from pyDiameter.pyDiaAVPPath import DiaAVPPath

# An unknown type of Diameter AVP.																						#
class DiaAVPUnknowType(DiaAVP):	
	def _decodeAVPValue(self, valueBytes):
		return None
		
	def _encodeAVPValue(self, avpValue):
		return ZERO_LEN_BYTES
		
	def _validAVPValue(self, value):
		return True
		
	def __len__(self):
		return 0
	
	def _initAVPValue(self):
		pass
		
	def __getitem__(self, index):
		pass
		
# end of DiaAVPUnknowType.
		
class DiaAVPStr(DiaAVP):	
	# this function will decode bytes value to value.																	#
	def _decodeAVPValue(self, valueBytes):
		assert type(valueBytes) is bytes
		# in string type AVP, valueBytes will be return directly.
		return valueBytes
		
	# Override the encode function.																						#
	def _encodeAVPValue(self, avpValue):
		assert type(avpValue) is bytes, "Make sure avpValue is Python Bytes Type. Now it is " + str(type(avpValue)) 
		return avpValue
		
	# Override the _validAVPValue function.																				#
	def _validAVPValue(self, value):
		if not type(value) is bytes: raise ValueError("String AVP should have a bytes-like value. e.g. b'hello, world.'")
		return True
		
	# Override _initAVPValue function.
	def _initAVPValue(self):
		self.setAVPValue(ZERO_LEN_BYTES)
		
	# Override __len__ operator
	def __len__(self):
		return self.getAVPHeaderLength() + len(self.getAVPValue())
		
	#Override __getitem__ function.
	def __getitem__(self, index):
		raise NotImplementedError('__getitem__ is not implemented in DiaAVPStr')
		
# end of DiaAVPStr.
		
class DiaAVPUInt32(DiaAVP):		
	# this function implement _decodeAVPValue of DiaAVP.																	#
	def _decodeAVPValue(self, valueBytes):
		assert type(valueBytes) is bytes
		assert len(valueBytes) is AVP_VALUE_UINT32_BUFF_LEN, "For UINT32 AVP, buffer should have 4 bytes, now it is " + str(len(valueBytes))
		return self.decodeUIntValue(valueBytes)
		
	# this function implement _encodeAVPValue of DiaAVP.																	#
	def _encodeAVPValue(self, avpValue):
		try:
			return self.encodeUIntValue(avpValue, AVP_VALUE_UINT32_BUFF_LEN)
		except OverflowError as ofle:
			raise OverflowError("UINT32 AVP should be b/w 0 - 4294967295, avpValue now is "+str(avpValue))
			
	# Override the _validAVPValue function.																				#
	def _validAVPValue(self, value):
		if (not type(value) is int) or (value < 0) : raise ValueError("UINT32 AVP should have a positive integer value. e.g. 10")
		return True
		
	# Override _initAVPValue function.
	def _initAVPValue(self):
		self.setAVPValue(0)

	# Override __len__ operator
	def __len__(self):
		return self.getAVPHeaderLength() + AVP_VALUE_UINT32_BUFF_LEN
		
	#Override __getitem__ function.
	def __getitem__(self, index):
		raise NotImplementedError('__getitem__ is not implemented in DiaAVPUInt32.')
			
# end of DiaAVPUInt32.

class DiaAVPInt32(DiaAVP):		
	def __decodeInt32Value(self, valueBytes):
		return unpack(DEFAULT_BYTES_ORDER_2+'i', valueBytes)[0]
	
	def __encodeInt32Value(self, value):
		try:
			return pack(DEFAULT_BYTES_ORDER_2+'i', value)
		except:
			raise OverflowError
		
	# this function implement _decodeAVPValue of DiaAVP.																	#
	def _decodeAVPValue(self, valueBytes):
		assert type(valueBytes) is bytes
		assert len(valueBytes) is AVP_VALUE_INT32_BUFF_LEN, "For INT32 AVP, buffer should have 4 bytes, now it is " + str(len(valueBytes))
		return self.__decodeInt32Value(valueBytes)
		
	# this function implement _encodeAVPValue of DiaAVP.																	#
	def _encodeAVPValue(self, avpValue):
		try:
			return self.__encodeInt32Value(avpValue)
		except OverflowError as ofle:
			raise OverflowError("INT32 AVP should be b/w -2147483648 - 2147483647, avpValue now is "+str(avpValue))
			
	# Override the _validAVPValue function.																				#
	def _validAVPValue(self, value):
		if (not type(value) is int): raise ValueError("INT32 AVP should have a integer value. e.g. 10, -10")
		return True
		
	# Override _initAVPValue function.
	def _initAVPValue(self):
		self.setAVPValue(0)
		
	# Override __len__ operator
	def __len__(self):
		return self.getAVPHeaderLength() + AVP_VALUE_INT32_BUFF_LEN
		
	#Override __getitem__ function.
	def __getitem__(self, index):
		raise NotImplementedError('__getitem__ is not implemented in DiaAVPInt32.')

# end of DiaAVPInt32

class DiaAVPUInt64(DiaAVP):
	# this function implement _decodeAVPValue of DiaAVP.																	#
	def _decodeAVPValue(self, valueBytes):
		assert type(valueBytes) is bytes
		assert len(valueBytes) is AVP_VALUE_UINT64_BUFF_LEN, "For UINT64 AVP, buffer should have 8 bytes, now it is " + str(len(valueBytes))
		return self.decodeUIntValue(valueBytes)
		
	# this function implement _encodeAVPValue of DiaAVP.																	#
	def _encodeAVPValue(self, avpValue):
		try:
			return self.encodeUIntValue(avpValue, AVP_VALUE_UINT64_BUFF_LEN)
		except OverflowError as ofle:
			raise OverflowError("UINT64 AVP should be b/w 0 - 18446744073709551615, avpValue now is "+str(avpValue))
			
	# Override the _validAVPValue function.																				#
	def _validAVPValue(self, value):
		if (not type(value) is int) or (value < 0) : raise ValueError("UINT64 AVP should have a positive integer value. e.g. 10")
		return True
			
	# Override _initAVPValue function.
	def _initAVPValue(self):
		self.setAVPValue(0)

	# Override __len__ operator
	def __len__(self):
		return self.getAVPHeaderLength() + AVP_VALUE_UINT64_BUFF_LEN
		
	#Override __getitem__ function.
	def __getitem__(self, index):
		raise NotImplementedError('__getitem__ is not implemented in DiaAVPUInt64.')
		
# end of DiaAVPUInt64.

class DiaAVPInt64(DiaAVP):
	def __decodeInt64Value(self, valueBytes):
		return unpack(DEFAULT_BYTES_ORDER_2+'q', valueBytes)[0]
	
	def __encodeInt64Value(self, value):
		try:
			return pack(DEFAULT_BYTES_ORDER_2+'q', value)
		except:
			raise OverflowError
		
	# this function implement _decodeAVPValue of DiaAVP.																	#
	def _decodeAVPValue(self, valueBytes):
		assert type(valueBytes) is bytes
		assert len(valueBytes) is AVP_VALUE_INT64_BUFF_LEN, "For INT64 AVP, buffer should have 8 bytes, now it is " + str(len(valueBytes))
		return self.__decodeInt64Value(valueBytes)
		
	# this function implement _encodeAVPValue of DiaAVP.																	#
	def _encodeAVPValue(self, avpValue):
		try:
			return self.__encodeInt64Value(avpValue)
		except OverflowError as ofle:
			raise OverflowError("INT64 AVP should be b/w -9223372036854775808 - 9223372036854775807, avpValue now is "+str(avpValue))
			
	# Override the _validAVPValue function.																				#
	def _validAVPValue(self, value):
		if (not type(value) is int): raise ValueError("INT32 AVP should have a integer value. e.g. 10, -10")
		return True
			
	# Override _initAVPValue function.
	def _initAVPValue(self):
		self.setAVPValue(0)
		
	# Override __len__ operator
	def __len__(self):
		return self.getAVPHeaderLength() + AVP_VALUE_INT64_BUFF_LEN
		
	#Override __getitem__ function.
	def __getitem__(self, index):
		raise NotImplementedError('__getitem__ is not implemented in DiaAVPInt64.')
		
# end of DiaAVPInt64
	
class DiaAVPFloat32(DiaAVP):
	def __decodeFloat32Value(self, valueBytes):
		return unpack(DEFAULT_BYTES_ORDER_2+'f', valueBytes)[0]
	
	def __encodeFloat32Value(self, value):
		try:
			return pack(DEFAULT_BYTES_ORDER_2+'f', value)
		except:
			raise OverflowError
		
	# this function implement _decodeAVPValue of DiaAVP.																	#
	def _decodeAVPValue(self, valueBytes):
		assert type(valueBytes) is bytes
		assert len(valueBytes) is AVP_VALUE_FLOAT32_BUFF_LEN, "For Float32 AVP, buffer should have 4 bytes, now it is " + str(len(valueBytes))
		return self.__decodeFloat32Value(valueBytes)
		
	# this function implement _encodeAVPValue of DiaAVP.																	#
	def _encodeAVPValue(self, avpValue):
		try:
			if float('-inf') == avpValue or float('inf') == avpValue: raise OverflowError
			return self.__encodeFloat32Value(avpValue)
		except OverflowError as ofle:
			raise OverflowError("Float32 AVP should be b/w -3.4028234663852886E+38 - 3.4028234663852886E+38, avpValue now is "+str(avpValue))
			
	# Override the _validAVPValue function.																				#
	def _validAVPValue(self, value):
		if (not type(value) is float): raise ValueError("FLOAT32 AVP should have a float value. e.g. 1.7")
		return True
		
	# Override _initAVPValue function.
	def _initAVPValue(self):
		self.setAVPValue(0.0)
		
	# Override __len__ operator
	def __len__(self):
		return self.getAVPHeaderLength() + AVP_VALUE_FLOAT32_BUFF_LEN
		
	#Override __getitem__ function.
	def __getitem__(self, index):
		raise NotImplementedError('__getitem__ is not implemented in DiaAVPFloat32.')
		
# end of DiaAVPFloat32

class DiaAVPFloat64(DiaAVP):
	def __decodeFloat64Value(self, valueBytes):
		return unpack(DEFAULT_BYTES_ORDER_2+'d', valueBytes)[0]
	
	def __encodeFloat64Value(self, value):
		try:
			return pack(DEFAULT_BYTES_ORDER_2+'d', value)
		except:
			raise OverflowError
		
	# this function implement _decodeAVPValue of DiaAVP.																	#
	def _decodeAVPValue(self, valueBytes):
		assert type(valueBytes) is bytes
		assert len(valueBytes) is AVP_VALUE_FLOAT64_BUFF_LEN, "For Float64 AVP, buffer should have 8 bytes, now it is " + str(len(valueBytes))
		return self.__decodeFloat64Value(valueBytes)
		
	# this function implement _encodeAVPValue of DiaAVP.																	#
	def _encodeAVPValue(self, avpValue):
		try:
			if float('-inf') == avpValue or float('inf') == avpValue: raise OverflowError
			return self.__encodeFloat64Value(avpValue)
		except OverflowError as ofle:
			raise OverflowError("Float64 AVP should be b/w -1.7976931348623157E+308 - 1.7976931348623157E+308, avpValue now is "+str(avpValue))
			
	# Override the _validAVPValue function.																				#
	def _validAVPValue(self, value):
		if (not type(value) is float): raise ValueError("FLOAT64 AVP should have a float value. e.g. 1.7")
		return True

	# Override _initAVPValue function.
	def _initAVPValue(self):
		self.setAVPValue(0.0)
		
	# Override __len__ operator
	def __len__(self):
		return self.getAVPHeaderLength() + AVP_VALUE_FLOAT64_BUFF_LEN
		
	#Override __getitem__ function.
	def __getitem__(self, index):
		raise NotImplementedError('__getitem__ is not implemented in DiaAVPFloat64.')
		
# end of DiaAVPFloat64
	
class DiaAVPGroup(DiaAVP):			
	# This function is used to divide a Bytes buffer which contains several AVP bytes into a list.						#
	# Each item in the list contains only 1 AVP (group AVP will contains all its sub-AVPs)								#
	@classmethod
	def cutAVPBytes(cls, avpBytes):
		LENGTH_POS = 5
		p = 0
		r = []
		while p <= len(avpBytes):
			try:
				lengthBytes = avpBytes [p + LENGTH_POS:p + LENGTH_POS + AVP_LENGTH_BUFF_LEN]
				if ZERO_LEN_BYTES == lengthBytes: break
				length = cls.decodeUIntValue(lengthBytes)
				alignedLength = cls.getAlignmentLength(length)
				r.append(avpBytes[p:p+alignedLength])
				p += alignedLength
			except Exception as e:
				break
		return r
		
	# For adding sub-AVP in this AVP object.
	def addAVP(self, avp, index = -1):
		avps = self.getAVPValue()
		assert type(avps) is list, "GROUP AVP value should be a list which contains DiaAVP sub-class objects. e.g. [avp1, avp2, avp3]"
		if -1 == index: avps.append(avp)
		elif index < len(avps): avps.insert(index, avp)
		else: raise ValueError('Index to insert is too big to this DiaAVPGroup. DiaAVPGroup only have '+ str(len(avps)) + ' items.')
		self.setAVPValue(avps)
		
	# For removing sub-AVP in this AVP object.
	def removeAVP(self, index):
		avps = self.getAVPValue()
		assert type(avps) is list
		assert index < len(avps), "Index try to remove must less than length of avps in this Group AVP object."
		del avps[index]
		self.setAVPValue(avps)

	# For getting count of sub-AVPs.
	def getAVPCount(self):
		avps=self.getAVPValue()
		assert type(avps) is list
		return len(avps)
		
	def __getAVPByCode(self, vendor, code, sameAVPIndex):
		avps = self.getAVPValue()
		i = 0
		r = None
		for avp in avps:
			if vendor == avp.getAVPVendor() and code == avp.getAVPCode(): i += 1
			if i > sameAVPIndex:
				r = avp
				break
		return r
		
	# By using DiaAVPPath object, this function can help user to visit AVP directly.									#
	# avpPath parameter should be initialed first by using AVP path language, like 10145/1400[0]->0/493[0]				#
	def getAVPByPath(self, avpPath):
		assert ((type(avpPath) is DiaAVPPath),'getAVPByPath in DiaAVPGroup need a DiaAVPPath object as a parameter.')
		if 0 >= avpPath.getLayersCount(): return self
		avp = None
		vendor =  avpPath.getAVPVendor(0)
		code = avpPath.getAVPCode(0)
		sameAVPIndex = avpPath.getAVPSameAVPIndex(0)
		avp = self.__getAVPByCode(vendor, code, sameAVPIndex)
		if None == avp: return None
		if 1 < avpPath.getLayersCount():
			tmpPath = DiaAVPPath()
			tmpPath.setPath(avpPath.getPath())
			tmpPath.removeTop()
			avp = avp.getAVPByPath(tmpPath)
		return avp
		
	# By using DiaAVPPath object, this function can help user to add AVP directly.										#
	# rootAVPPath parameter should be initialed first by using AVP path language, like 10145/1400[0]->0/493[0]			#
	# Note that, rootAVPPath is the father avp which contains the avp you want to add.									#
	# rootAVPPath must be a group type AVP, or you can leave rootAVPPath a blank, avp will be added at root.			#		
	def addAVPByPath(self, rootAVPPath, avp, index = -1):
		assert ((type(rootAVPPath) is DiaAVPPath),'addAVPByPath in DiaAVPGroup need a DiaAVPPath object as a parameter.')
		rootAVP = self.getAVPByPath(rootAVPPath)
		if not (type(rootAVP) is DiaAVPGroup): return -1
		rootAVP.addAVP(avp, index)
		return 0

	# By using DiaAVPPath object, this function can help user to remove AVP directly.									#
	# avpPath parameter should be initialed first by using AVP path language, like 10145/1400[0]->0/493[0]				#		
	def removeAVPByPath(self, avpPath):
		assert ((type(avpPath) is DiaAVPPath),'addAVPByPath in DiaAVPGroup need a DiaAVPPath object as a parameter.')
		if 0 >= avpPath.getLayersCount(): return -1
		last = avpPath.getLayersCount() - 1
		vendor =  avpPath.getAVPVendor(last)
		code = avpPath.getAVPCode(last)
		sameAVPIndex = avpPath.getAVPSameAVPIndex(last)
		rootAVPPath = DiaAVPPath()
		rootAVPPath.setPath(avpPath.getPath())
		rootAVPPath.removeTail()
		rootAVP = self.getAVPByPath(rootAVPPath)
		if None == rootAVP: return -1
		avp = rootAVP.__getAVPByCode(vendor, code, sameAVPIndex)
		avps = rootAVP.getAVPValue()
		avps.remove(avp)
	
	# For decoding Group AVP.
	def _decodeAVPValue(self, valueBytes):
		retValue = []
		factory = DiaAVPFactory()
		avpsBytes = self.cutAVPBytes(valueBytes)
		for avpBytes in avpsBytes:
			avpObj = factory.generateDiaAVPObject(avpBytes)
			retValue.append(avpObj)
		return retValue
			
	# For encoding Group AVP.
	def _encodeAVPValue(self, avpValue):
		assert type(avpValue) is list
		retValue = ZERO_LEN_BYTES
		for subAvp in avpValue:
			retValue += subAvp.encode()
		return retValue
		
	# Override the _validAVPValue function.																				#
	def _validAVPValue(self, value):
		if (not type(value) is list): raise ValueError("GROUP AVP value should be a list which contains DiaAVP sub-class objects. e.g. [avp1, avp2, avp3]")
		for obj in value:
			if not isinstance(obj, DiaAVP): raise ValueError("GROUP AVP avlue should be a list which contains DiaAVP sub-class objects. e.g. [avp1, avp2, avp3]")
		return True
		
	# Override _initAVPValue function.
	def _initAVPValue(self):
		self.setAVPValue([])
		
	# Override __len__ operator
	def __len__(self):
		l = 0
		for subAvp in self.getAVPValue():
			l += self.getAlignmentLength(len(subAvp))
		return self.getAVPHeaderLength() + l

	#Override __getitem__ function.
	def __getitem__(self, index):
		avps = self.getAVPValue()
		assert index < len(avps), "Index try to visit must less than length of avps in this Group AVP object."
		return avps[index]

# end of DiaAVPGroup.
