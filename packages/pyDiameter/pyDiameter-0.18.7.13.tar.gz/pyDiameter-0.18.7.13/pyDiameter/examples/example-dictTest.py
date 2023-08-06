from pyDiameter.pyDiaAVPDict import DiaAVPDict
from pyDiameter.pyDiaAVPConst import AVP_TYPE_GROUP,AVP_TYPE_STR

a = DiaAVPDict()
b = DiaAVPDict()
# verify that DiaAVPDict is a singleton class.
print(a==b)

# verify whether DiaAVPDict has vendor 0 defination.
print(a.hasVendorDef(0))
# verify whether DiaAVPDict has vendor 44556 defination. (44556 is not defined in DiaAVPDict default dictionary.)
print(b.hasVendorDef(44556))

# try to get AVP type defination with code 13331, vendor code 0. No definatiion actually.
print(a.getAVPDefType(0,13331))

# add the definatiion.
a.addAVPDef(0,13331,'test',AVP_TYPE_GROUP)

# verify again by using another DiaAVPDict object.
print(b.hasAVPDef(0,13331),b.getAVPDefName(0,13331),b.getAVPDefType(0,13331))

# update the definatiion.
a.updateAVPDef(0,13331,'test2',AVP_TYPE_STR)
# verify again by using another DiaAVPDict object.
print(b.hasAVPDef(0,13331),b.getAVPDefName(0,13331),b.getAVPDefType(0,13331))
