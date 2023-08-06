# Created by george zhao, who is working for NOKIA, 2010-2012, 2014-2018.												#
# This lib is based on python 3.6.5																						#

import importlib

from pyDiameter.pyDiaAVPBasicTypesConst import AVP_TYPE_STR
from pyDiameter.pyDiaAVPBasicTypesConst import AVP_TYPE_INT32
from pyDiameter.pyDiaAVPBasicTypesConst import AVP_TYPE_UINT32
from pyDiameter.pyDiaAVPBasicTypesConst import AVP_TYPE_INT64
from pyDiameter.pyDiaAVPBasicTypesConst import AVP_TYPE_UINT64
from pyDiameter.pyDiaAVPBasicTypesConst import AVP_TYPE_FLOAT32
from pyDiameter.pyDiaAVPBasicTypesConst import AVP_TYPE_FLOAT64
from pyDiameter.pyDiaAVPBasicTypesConst import AVP_TYPE_GROUP

# this class is used to generate DiaAVP Object. (An empty object, need call decode)										#
# after get object from this factory, call object decode method to fullfill the object.									#
class DiaAVPFactory():
	def __init__(self):
		self.__typesDict={
			AVP_TYPE_STR: "DiaAVPStr",
			AVP_TYPE_INT32: "DiaAVPInt32",
			AVP_TYPE_UINT32: "DiaAVPUInt32",
			AVP_TYPE_INT64: "DiaAVPInt64",
			AVP_TYPE_UINT64: "DiaAVPUInt64",
			AVP_TYPE_FLOAT32: "DiaAVPFloat32",
			AVP_TYPE_FLOAT64: "DiaAVPFloat64",
			AVP_TYPE_GROUP: "DiaAVPGroup",
		}
		
	def generateDiaAVPObject(self, avpBytes):
		typesModule = importlib.import_module("pyDiameter.pyDiaAVPTypes")
		utAVP = getattr(typesModule, "DiaAVPUnknowType")()
		utAVP.decode(avpBytes)
		type = utAVP.getAVPType()
		if type in self.__typesDict: r = getattr(typesModule, self.__typesDict[type])()
		else: r = None
		if not (None ==  r): r.decode(avpBytes)
		return r
			
# end of DiaAVPFactory.