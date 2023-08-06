# Created by george zhao, who is working for NOKIA, 2010-2012, 2014-2018.												#
# This lib is based on python 3.6.5																						#

from abc import ABCMeta
from abc import abstractmethod
from pyDiameter.pyDiaAVPDict import DiaAVPDict

from pyDiameter.pyDiaAVPConst import AVP_VENDOR_UNKNOWN
from pyDiameter.pyDiaAVPConst import AVP_CODE_UNKNOWN
from pyDiameter.pyDiaAVPConst import AVP_NAME_NONE
from pyDiameter.pyDiaAVPConst import AVP_TYPE_UNKNOWN
from pyDiameter.pyDiaAVPConst import AVP_FLAG_CLEAR
from pyDiameter.pyDiaAVPConst import AVP_VALUE_UNSET
from pyDiameter.pyDiaAVPConst import AVP_CODE_BUFF_LEN
from pyDiameter.pyDiaAVPConst import AVP_FLAGS_BUFF_LEN
from pyDiameter.pyDiaAVPConst import AVP_LENGTH_BUFF_LEN
from pyDiameter.pyDiaAVPConst import AVP_VENDOR_BUFF_LEN
from pyDiameter.pyDiaConst import NULL_BYTE
from pyDiameter.pyDiaConst import DEFAULT_BYTES_ORDER
from pyDiameter.pyDiaAVPFactory import DiaAVPFactory


# DiaAVP class is defined for carry Diameter AVP, and its sub-AVPs.														#
class DiaAVP(metaclass=ABCMeta):
	# DiaAVP is an abstract Base Class.

	# init function of DiaAVP.																							#
	def __init__(self):
		self.__avpVendor = AVP_VENDOR_UNKNOWN
		self.__avpCode = AVP_CODE_UNKNOWN
		self.__avpName = AVP_NAME_NONE
		self.__avpType = AVP_TYPE_UNKNOWN
		self.__avpFlags = AVP_FLAG_CLEAR
		self._initAVPValue()

		
	# For property avpName.
	def getAVPName(self):
		vendor = 0
		if self.getAVPFlags():
			vendor = self.getAVPVendor()
		code = self.getAVPCode()
		dict =  DiaAVPDict()
		if dict.hasAVPDef(vendor, code):
			return dict.getAVPDefName(self.getAVPVendor(), self.getAVPCode())
		return AVP_NAME_NONE
		
	# For property avpType, read only.
	def getAVPType(self):
		vendor = 0
		if self.getAVPFlags():
			vendor = self.getAVPVendor()
		code = self.getAVPCode()
		dict =  DiaAVPDict()
		if dict.hasAVPDef(vendor, code):
			return dict.getAVPDefType(self.getAVPVendor(), self.getAVPCode())
		return AVP_TYPE_UNKNOWN
		
	# For property avpCode
	def getAVPCode(self):
		return self.__avpCode
	def setAVPCode(self, avpCode):
		self.__avpCode = avpCode
		return True

	# For property avpFlag
	def getAVPFlags(self):
		return self.__avpFlags
	def setAVPFlags(self, avpFlags):
		self.__avpFlags = avpFlags
		return True
	def setAVPVSFlag(self):
		self.__avpFlags = self.__avpFlags | 0x80
		return True
	def clearAVPVSFlag(self):
		self.__avpFlags = self.__avpFlags & 0x7F
		return True
	def getAVPVSFlag(self):
		if ((self.__avpFlags & 0x80) >> 7) == 1:
			return True
		return False
	def setAVPMandatoryFlag(self):
		self.__avpFlags = self.__avpFlags | 0x40
		return True
	def clearAVPMandatoryFlag(self):
		self.__avpFlags = self.__avpFlags & 0xBF
		return True
	def getAVPMandatoryFlag(self):
		if ((self.__avpFlags & 0x40) >> 6) == 1:
			return True
		return False
	def setAVPProtectedFlag(self):
		self.__avpFlags = self.__avpFlags | 0x20
		return True
	def clearAVPProtectedFlag(self):
		self.__avpFlags = self.__avpFlags & 0xDF
		return True
	def getAVPProtectedFlag(self):
		if ((self.__avpFlags & 0x20) >> 5) == 1:
			return True
		return False
		
	# For property avpVendor.
	def getAVPVendor(self):
		return self.__avpVendor
	def setAVPVendor(self, avpVendor):
		self.__avpVendor = avpVendor
		return True
		
	# For property avpValue
	def getAVPValue(self):
		return self.__avpValue
	def setAVPValue(self, value):
		assert self._validAVPValue(value)
		self.__avpValue = value
		
	# For get AVP header length, read only.
	def getAVPHeaderLength(self):
		l = AVP_CODE_BUFF_LEN + AVP_FLAGS_BUFF_LEN + AVP_LENGTH_BUFF_LEN 
		if self.getAVPVSFlag(): l += AVP_VENDOR_BUFF_LEN
		return l
	
	@classmethod
	def getAlignmentLength(self, len):
		return (len % 4 == 0) and len or (int(len/4) + 1) * 4		
		
	# decode tools functions																							#
	# decode tools functions need bytes buff as their parameters, not string.											#		
	# decode an integer value.		
	@classmethod																		#
	def decodeUIntValue(self, intValueBytes):
		assert type(intValueBytes) is bytes
		return int.from_bytes(intValueBytes, DEFAULT_BYTES_ORDER)
	
	# decode AVP code function																							#	
	def decodeAVPCode(self, codeBytes):
		assert (AVP_CODE_BUFF_LEN == len(codeBytes))
		return self.decodeUIntValue(codeBytes)
		
	# decode AVP Flags function.																						#
	def decodeAVPFlags(self, flagsBytes):
		assert (AVP_FLAGS_BUFF_LEN == len(flagsBytes))
		return self.decodeUIntValue(flagsBytes)
	
	# decode AVP length function.																						#
	def decodeAVPLength(self, lengthBytes):	
		assert (AVP_LENGTH_BUFF_LEN == len(lengthBytes))	
		return self.decodeUIntValue(lengthBytes)	
			
	# decode AVP vendor function.																						#
	def decodeAVPVendor(self, vendorBytes):
		assert (AVP_VENDOR_BUFF_LEN == len(vendorBytes))
		return self.decodeUIntValue(vendorBytes)
	
	# encode tools functions																							#
	# encode tools will output bytes, not string.																		#
	# encode an integer value.																							#
	def encodeUIntValue(self, intValue, intValueLength):
		return intValue.to_bytes(intValueLength, DEFAULT_BYTES_ORDER)
		
	# encode AVP code function																							#	
	def encodeAVPCode(self, avpCode):
		assert type(avpCode) is int
		return self.encodeUIntValue(avpCode, AVP_CODE_BUFF_LEN)
		
	# encode AVP vendor function																						#	
	def encodeAVPFlags(self, avpFlags):
		assert type(avpFlags) is int
		return self.encodeUIntValue(avpFlags, AVP_FLAGS_BUFF_LEN)
		
	# encode AVP length function																						#	
	def encodeAVPLength(self, avpLength):
		assert type(avpLength) is int
		return self.encodeUIntValue(avpLength, AVP_LENGTH_BUFF_LEN)		
		
	# encode AVP vendor function																						#	
	def encodeAVPVendor(self, avpVendor):
		assert type(avpVendor) is int
		return self.encodeUIntValue(avpVendor, AVP_VENDOR_BUFF_LEN)		
	
	# decode is for decoding a binary bytes to DiaAVP object.															#
	def decode(self, avpBuffBytes):
		p = 0
		self.setAVPCode(self.decodeAVPCode(avpBuffBytes[p:p+AVP_CODE_BUFF_LEN]))
		p += AVP_CODE_BUFF_LEN
		self.setAVPFlags(self.decodeAVPFlags(avpBuffBytes[p:p+AVP_FLAGS_BUFF_LEN]))
		p += AVP_FLAGS_BUFF_LEN
		tmpLen = (self.decodeAVPLength(avpBuffBytes[p:p+AVP_LENGTH_BUFF_LEN]))
		p += AVP_LENGTH_BUFF_LEN
		if self.getAVPVSFlag():
			self.setAVPVendor(self.decodeAVPVendor(avpBuffBytes[p:p+AVP_VENDOR_BUFF_LEN]))
			p += AVP_VENDOR_BUFF_LEN
		valueLen = tmpLen - p
		assert tmpLen <= len(avpBuffBytes), "Buffer length is smaller than length indicated in AVP."
		self.setAVPValue(self._decodeAVPValue(avpBuffBytes[p:p+valueLen]))
		return True
		
	# encode is for encoding a DiaAVP object to a binary bytes.															#
	def encode(self):
		retValue = self.encodeAVPCode(self.getAVPCode())
		retValue += self.encodeAVPFlags(self.getAVPFlags())
		retValue += self.encodeAVPLength(len(self))
		if self.getAVPVSFlag(): retValue += self.encodeAVPVendor(self.getAVPVendor())
		encodedValue = self._encodeAVPValue(self.getAVPValue())
		l = len(encodedValue)
		retValue += encodedValue + NULL_BYTE * (self.getAlignmentLength(l) - l)
		return retValue
		
	# Children class will override following function.
	@abstractmethod
	def _decodeAVPValue(self, valueBytes):
		raise NotImplementedError	
	@abstractmethod
	def _encodeAVPValue(self, valueBytes):
		raise NotImplementedError
	@abstractmethod
	def _validAVPValue(self, value):
		raise NotImplementedError
	@abstractmethod
	def _initAVPValue(self):
		raise NotImplementedError
	# For get AVP length
	@abstractmethod
	def __len__(self):
		raise NotImplementedError
	# For get sub-AVP in this AVP object.
	@abstractmethod
	def __getitem__(self, index):
		raise NotImplementedError
		
# end of DiaAVP class.

