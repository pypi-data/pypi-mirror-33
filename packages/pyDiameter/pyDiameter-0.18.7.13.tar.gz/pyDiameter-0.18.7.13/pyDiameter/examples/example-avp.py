avpBuff1 = b'\x00\x00\x05\x85\xc0\x00\x00\xa8\x00\x00\x28\xaf\x00\x00\x05\x86\xc0\x00\x00\x9c\x00\x00\x28\xaf\x00\x00\x05\x8b\xc0\x00\x00\x10\x00\x00\x28\xaf\x00\x00\x00\x01\x00\x00\x05\xa7\xc0\x00\x00\x1c\x00\x00\x28\xaf\x0b\xd5\x14\xf6\xe1\xeb\xf1\x0b\x59\xdc\xbb\x9e\x72\x90\x20\x98\x00\x00\x05\xa8\xc0\x00\x00\x1c\x00\x00\x28\xaf\x1a\xf7\x27\xb2\xb4\x8d\x86\x83\x48\xfe\x88\xda\x27\xf6\x57\x99\x00\x00\x05\xa9\xc0\x00\x00\x1c\x00\x00\x28\xaf\x01\x00\x10\x44\x41\x62\x71\x08\x11\x00\x33\x04\x50\x00\x20\x00\x00\x00\x05\xaa\xc0\x00\x00\x2c\x00\x00\x28\xaf\x12\x34\x56\x78\x90\x12\x34\x56\x78\x90\x12\x34\x56\x78\x90\x12\x34\x56\x78\x90\x12\x34\x56\x78\x90\x12\x34\x56\x78\x90\x12\x34\x00'

avpBuff2 = b'\x00\x00\x01\x25\x40\x00\x00\x11\x48\x53\x53\x2e\x74\x74\x63\x6e\x33\x00\x00\x00'

# This is a wrong avp, whose code is not defined in DiaAVPDict
avpBuff3 = b'\x00\x00\x34\x13\x40\x00\x00\x11\x48\x53\x53\x2e\x74\x74\x63\x6e\x33\x00\x00\x00'

def visitAVP(avp, tab=''):
	print(tab,end='')
	print('name:  ',avp.getAVPName())
	print(tab,end='')
	print('type:  ',avp.getAVPType())	
	print(tab,end='')
	print('code:  ',avp.getAVPCode())
	print(tab,end='')
	print('flags: ',avp.getAVPFlags())
	print(tab,end='')
	print('len:   ',len(avp))
	value=avp.getAVPValue()
	if avp.getAVPVSFlag():
		print(tab,end='')
		print('vendor:', avp.getAVPVendor())
	if type(value) is list:
		print(tab, end='')
		print('====>')
		for sub in value:
			visitAVP(sub, tab+'    ')
		print(tab, end='')
		print('<====')		
	else:
		print(tab,end='')
		print('value: ', value)
	print(tab,end='')
	print('-------')
	
from pyDiameter.pyDiaAVPFactory import DiaAVPFactory
from pyDiameter.pyDiaAVPDict import DiaAVPDict
from pyDiameter.pyDiaAVPConst import AVP_TYPE_STR

print("=========== AVP1 decoding ===========")
factory = DiaAVPFactory()
avp1 = factory.generateDiaAVPObject(avpBuff1)
visitAVP(avp1)

print("=========== AVP2 decoding ===========")
avp2 = factory.generateDiaAVPObject(avpBuff2)
visitAVP(avp2)

print("=========== AVP3 decoding ===========")
# Unknown avp decode
avp3 = factory.generateDiaAVPObject(avpBuff3)
print(avp3 == None)
# decode result is a None object.
# modify DiaAVPDict
print("=========== AVP3 Update Dictionary ===========")
dict = DiaAVPDict()
dict.addAVPDef(0,13331,'test-avp-defined',AVP_TYPE_STR)
avp3 = factory.generateDiaAVPObject(avpBuff3)
visitAVP(avp3)
print("=========== Add an int32 AVP to AVP1 ===========")
# as we known, avp1 is a group avp, only group avp could add sub-avp.
from pyDiameter.pyDiaAVPBasicTypes import DiaAVPInt32
from pyDiameter.pyDiaAVPPath import DiaAVPPath

newAVP = DiaAVPInt32()
newAVP.setAVPCode(6)
newAVP.setAVPMandatoryFlag()
newAVP.setAVPValue(-10)
avpPath = DiaAVPPath()
avpPath.setPath('')	# root position
avp1.addAVPByPath(avpPath, newAVP)
visitAVP(avp1)

print("=========== Add an unsigned int32 AVP to AVP1's sub-avp ===========")
# as we known, avp1 is a group avp, only group avp could add sub-avp.
from pyDiameter.pyDiaAVPBasicTypes import DiaAVPUInt32
from pyDiameter.pyDiaAVPPath import DiaAVPPath
newAVP = DiaAVPUInt32()
newAVP.setAVPCode(5)
newAVP.setAVPMandatoryFlag()
newAVP.setAVPValue(32)
avpPath = DiaAVPPath()
avpPath.setPath('10415/1414[0]')	# root's sub-avp (code 1414, vendor 10415)
avp1.addAVPByPath(avpPath, newAVP)
visitAVP(avp1)

print("=========== Add an int64 AVP to AVP1 ===========")
# as we known, avp1 is a group avp, only group avp could add sub-avp.
from pyDiameter.pyDiaAVPBasicTypes import DiaAVPInt64
from pyDiameter.pyDiaAVPPath import DiaAVPPath
newAVP = DiaAVPInt64()
newAVP.setAVPCode(447)
newAVP.setAVPMandatoryFlag()
newAVP.setAVPValue(-47)
avpPath = DiaAVPPath()
avpPath.setPath('')	# root position
avp1.addAVPByPath(avpPath, newAVP)
visitAVP(avp1)

print("=========== Add an unsigned int64 AVP to AVP1 ===========")
# as we known, avp1 is a group avp, only group avp could add sub-avp.
from pyDiameter.pyDiaAVPBasicTypes import DiaAVPUInt64
from pyDiameter.pyDiaAVPPath import DiaAVPPath
newAVP = DiaAVPUInt64()
newAVP.setAVPCode(465)
newAVP.setAVPMandatoryFlag()
newAVP.setAVPValue(40)
avpPath = DiaAVPPath()
avpPath.setPath('')	# root position
avp1.addAVPByPath(avpPath, newAVP)
visitAVP(avp1)

print("=========== Add a float32 AVP to AVP1 ===========")
# as we known, avp1 is a group avp, only group avp could add sub-avp.
from pyDiameter.pyDiaAVPBasicTypes import DiaAVPFloat32
from pyDiameter.pyDiaAVPPath import DiaAVPPath
newAVP = DiaAVPFloat32()
newAVP.setAVPCode(496)
newAVP.setAVPMandatoryFlag()
newAVP.setAVPValue(1.7)
avpPath = DiaAVPPath()
avpPath.setPath('')	# root position
avp1.addAVPByPath(avpPath, newAVP)
visitAVP(avp1)

print("=========== Add a float64 AVP to AVP1 ===========")
# as we known, avp1 is a group avp, only group avp could add sub-avp.
from pyDiameter.pyDiaAVPBasicTypes import DiaAVPFloat64
from pyDiameter.pyDiaAVPPath import DiaAVPPath
newAVP = DiaAVPFloat64()
newAVP.setAVPCode(603)
newAVP.setAVPMandatoryFlag()
# need set Vendor flag after setting vendor code for this AVP.
newAVP.setAVPVendor(193)
newAVP.setAVPVSFlag()
newAVP.setAVPValue(-1.18973149535723176E+308)
avpPath = DiaAVPPath()
avpPath.setPath('')	# root position
avp1.addAVPByPath(avpPath, newAVP)
visitAVP(avp1)

print("=========== Add a time AVP to AVP1 ===========")
# as we known, avp1 is a group avp, only group avp could add sub-avp.
from pyDiameter.pyDiaAVPBasicTypes import DiaAVPStr
from pyDiameter.pyDiaAVPPath import DiaAVPPath
from pyDiameter.pyDiaAVPTools import address_to_bytes, bytes_to_address, time_to_bytes, bytes_to_time
import datetime
newAVP = DiaAVPStr()
newAVP.setAVPCode(55)
newAVP.setAVPMandatoryFlag()
d=datetime.datetime.now()
newAVP.setAVPValue(time_to_bytes(d.year,d.month,d.day,d.hour,d.minute,d.second))
avpPath = DiaAVPPath()
avpPath.setPath('')	# root position
avp1.addAVPByPath(avpPath, newAVP)
visitAVP(avp1)

print("=========== Add an address AVP to AVP1 ===========")
# as we known, avp1 is a group avp, only group avp could add sub-avp.
from pyDiameter.pyDiaAVPBasicTypes import DiaAVPStr
from pyDiameter.pyDiaAVPPath import DiaAVPPath
from pyDiameter.pyDiaAVPTools import address_to_bytes, bytes_to_address, time_to_bytes, bytes_to_time
newAVP = DiaAVPStr()
newAVP.setAVPCode(257)
newAVP.setAVPMandatoryFlag()
newAVP.setAVPValue(address_to_bytes(('ipv6', '2000:1234:ac12:abcd:abcd:abcd:abcd:abc1')))
avpPath = DiaAVPPath()
avpPath.setPath('')	# root position
avp1.addAVPByPath(avpPath, newAVP)
visitAVP(avp1)

print("=========== Convert avp1 object to bytes ===========")
print(avp1.encode())

# Try following functions and find the result by yourself.
avp1.setAVPMandatoryFlag()
avp1.clearAVPMandatoryFlag()
avp1.setAVPVSFlag()
avp1.clearAVPVSFlag()
avp1.setAVPProtectedFlag()
avp1.clearAVPProtectedFlag()
