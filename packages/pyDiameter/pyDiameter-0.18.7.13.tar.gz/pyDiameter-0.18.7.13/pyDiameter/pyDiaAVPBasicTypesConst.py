# Created by george zhao, who is working for NOKIA, 2010-2012, 2014-2018.												#
# This lib is based on python 3.6.5																						#

# Types of AVP, only basic diameter types are supported.																#
from pyDiameter.pyDiaAVPConst import AVP_TYPE_STR
from pyDiameter.pyDiaAVPConst import AVP_TYPE_INT32 
from pyDiameter.pyDiaAVPConst import AVP_TYPE_UINT32 
from pyDiameter.pyDiaAVPConst import AVP_TYPE_INT64
from pyDiameter.pyDiaAVPConst import AVP_TYPE_UINT64 
from pyDiameter.pyDiaAVPConst import AVP_TYPE_FLOAT32
from pyDiameter.pyDiaAVPConst import AVP_TYPE_FLOAT64
from pyDiameter.pyDiaAVPConst import AVP_TYPE_GROUP

# AVP value length in buffer.																							#
AVP_VALUE_INT32_BUFF_LEN = 4
AVP_VALUE_UINT32_BUFF_LEN = 4
AVP_VALUE_INT64_BUFF_LEN = 8
AVP_VALUE_UINT64_BUFF_LEN = 8
AVP_VALUE_FLOAT32_BUFF_LEN = 4
AVP_VALUE_FLOAT64_BUFF_LEN = 8