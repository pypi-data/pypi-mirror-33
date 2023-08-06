#Created by george zhao, who is working for NOKIA, 2010-2012, 2014-2018.												#
#This lib is based on python 3.6.5																						#

#Definition of name and type keys in AVP_ARRAY_DEFAULT.																	#
NAME_KEY='name'
TYPE_KEY='type'

# Const for AVP code.																									#
AVP_CODE_UNKNOWN = 0
# Const for AVP name.																									#
AVP_NAME_NONE = ''
# Const for AVP vendor.																									#
AVP_VENDOR_UNKNOWN = 0
# Const for AVP flag.
AVP_FLAG_CLEAR = 0
AVP_FLAG_FULLSET = 0xFF
# Const for AVP value.																									#
AVP_VALUE_UNSET = None

# Const, Length of AVP attributes in bytes buffer.																		#
AVP_CODE_BUFF_LEN = 4
AVP_FLAGS_BUFF_LEN = 1
AVP_LENGTH_BUFF_LEN = 3
AVP_VENDOR_BUFF_LEN = 4

# Types of AVP, only basic diameter types are supported.																#
AVP_TYPE_UNKNOWN = 'unknown'
AVP_TYPE_STR = 'str'
AVP_TYPE_INT32 = 'int32'
AVP_TYPE_UINT32 = 'uint32'
AVP_TYPE_INT64 = 'int64'
AVP_TYPE_UINT64 = 'uint64'
AVP_TYPE_FLOAT32 = 'float32'
AVP_TYPE_FLOAT64 = 'float64'
AVP_TYPE_GROUP = 'grp'

# ===================================================================================================================== #
#Default dictionary of AVP definition.
AVP_ARRAY_DEFAULT={
# Vendor 0 Base Diameter
0:{
	1:{'name':'User-Name', 'type':AVP_TYPE_STR},	# Vendor 0
	2:{'name':'User-Password', 'type':AVP_TYPE_STR},	# Vendor 0
	3:{'name':'CHAP-Password', 'type':AVP_TYPE_STR},	# Vendor 0
	4:{'name':'NAS-IP-Address', 'type':AVP_TYPE_STR},	# Vendor 0
	5:{'name':'NAS-Port', 'type':AVP_TYPE_UINT32},	# Vendor 0
	6:{'name':'Service-Type', 'type':AVP_TYPE_INT32},	# Vendor 0
	7:{'name':'Framed-Protocol', 'type':AVP_TYPE_INT32},	# Vendor 0
	8:{'name':'Framed-IP-Address', 'type':AVP_TYPE_STR},	# Vendor 0
	9:{'name':'Framed-IP-Netmask', 'type':AVP_TYPE_STR},	# Vendor 0
	10:{'name':'Framed-Routing', 'type':AVP_TYPE_INT32},	# Vendor 0
	11:{'name':'Filter-Id', 'type':AVP_TYPE_STR},	# Vendor 0
	12:{'name':'Framed-MTU', 'type':AVP_TYPE_UINT32},	# Vendor 0
	13:{'name':'Framed-Compression', 'type':AVP_TYPE_INT32},	# Vendor 0
	14:{'name':'Login-IP-Host', 'type':AVP_TYPE_STR},	# Vendor 0
	15:{'name':'Login-Service', 'type':AVP_TYPE_INT32},	# Vendor 0
	16:{'name':'Login-TCP-Port', 'type':AVP_TYPE_UINT32},	# Vendor 0
	17:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	18:{'name':'Reply-Message', 'type':AVP_TYPE_STR},	# Vendor 0
	19:{'name':'Callback-Number', 'type':AVP_TYPE_STR},	# Vendor 0
	20:{'name':'Callback-Id', 'type':AVP_TYPE_STR},	# Vendor 0
	21:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	22:{'name':'Framed-Route', 'type':AVP_TYPE_STR},	# Vendor 0
	23:{'name':'Framed-IPX-Network', 'type':AVP_TYPE_STR},	# Vendor 0
	24:{'name':'State', 'type':AVP_TYPE_STR},	# Vendor 0
	25:{'name':'Class', 'type':AVP_TYPE_STR},	# Vendor 0
	26:{'name':'Vendor-Specific', 'type':AVP_TYPE_UINT32},	# Vendor 0
	27:{'name':'Session-Timeout', 'type':AVP_TYPE_UINT32},	# Vendor 0
	28:{'name':'Idle-Timeout', 'type':AVP_TYPE_UINT32},	# Vendor 0
	29:{'name':'Termination-Action', 'type':AVP_TYPE_UINT32},	# Vendor 0
	30:{'name':'Called-Station-Id', 'type':AVP_TYPE_STR},	# Vendor 0
	31:{'name':'Calling-Station-Id', 'type':AVP_TYPE_STR},	# Vendor 0
	32:{'name':'NAS-Identifier', 'type':AVP_TYPE_STR},	# Vendor 0
	33:{'name':'Proxy-State', 'type':AVP_TYPE_STR},	# Vendor 0
	34:{'name':'Login-LAT-Service', 'type':AVP_TYPE_STR},	# Vendor 0
	35:{'name':'Login-LAT-Node', 'type':AVP_TYPE_STR},	# Vendor 0
	36:{'name':'Login-LAT-Group', 'type':AVP_TYPE_STR},	# Vendor 0
	37:{'name':'Framed-AppleTalk-Link', 'type':AVP_TYPE_UINT32},	# Vendor 0
	38:{'name':'Framed-AppleTalk-Network', 'type':AVP_TYPE_UINT32},	# Vendor 0
	39:{'name':'Framed-AppleTalk-Zone', 'type':AVP_TYPE_STR},	# Vendor 0
	40:{'name':'Acct-Status-Type', 'type':AVP_TYPE_UINT32},	# Vendor 0
	41:{'name':'Acct-Delay-Time', 'type':AVP_TYPE_UINT32},	# Vendor 0
	42:{'name':'Acct-Input-Octets', 'type':AVP_TYPE_UINT32},	# Vendor 0
	43:{'name':'Acct-Output-Octets', 'type':AVP_TYPE_UINT32},	# Vendor 0
	44:{'name':'Acct-Session-Id', 'type':AVP_TYPE_STR},	# Vendor 0
	45:{'name':'Acct-Authentic', 'type':AVP_TYPE_INT32},	# Vendor 0
	46:{'name':'Acct-Session-Time', 'type':AVP_TYPE_UINT32},	# Vendor 0
	47:{'name':'Acct-Input-Packets', 'type':AVP_TYPE_INT32},	# Vendor 0
	48:{'name':'Acct-Output-Packets', 'type':AVP_TYPE_INT32},	# Vendor 0
	49:{'name':'Acct-Terminate-Cause', 'type':AVP_TYPE_UINT32},	# Vendor 0
	50:{'name':'Accounting-Multi-Session-Id', 'type':AVP_TYPE_STR},	# Vendor 0
	51:{'name':'Acct-Link-Count', 'type':AVP_TYPE_UINT32},	# Vendor 0
	52:{'name':'Acct-Input-Gigawords', 'type':AVP_TYPE_INT32},	# Vendor 0
	53:{'name':'Acct-Output-Gigawords', 'type':AVP_TYPE_INT32},	# Vendor 0
	54:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	55:{'name':'Event-Timestamp', 'type':AVP_TYPE_STR},	# Vendor 0
	56:{'name':'Egress-VLANID', 'type':AVP_TYPE_STR},	# Vendor 0
	57:{'name':'Ingress-Filters', 'type':AVP_TYPE_INT32},	# Vendor 0
	58:{'name':'Egress-VLAN-Name', 'type':AVP_TYPE_STR},	# Vendor 0
	59:{'name':'User-Priority-Table', 'type':AVP_TYPE_STR},	# Vendor 0
	60:{'name':'CHAP-Challenge', 'type':AVP_TYPE_STR},	# Vendor 0
	61:{'name':'NAS-Port-Type', 'type':AVP_TYPE_INT32},	# Vendor 0
	62:{'name':'Port-Limit', 'type':AVP_TYPE_UINT32},	# Vendor 0
	63:{'name':'Login-LAT-Port', 'type':AVP_TYPE_STR},	# Vendor 0
	64:{'name':'Tunnel-Type', 'type':AVP_TYPE_INT32},	# Vendor 0
	65:{'name':'Tunnel-Medium-Type', 'type':AVP_TYPE_INT32},	# Vendor 0
	66:{'name':'Acct-Tunnel-Client-Endpoint', 'type':AVP_TYPE_STR},	# Vendor 0
	67:{'name':'Tunnel-Server-Endpoint', 'type':AVP_TYPE_STR},	# Vendor 0
	68:{'name':'Acct-Tunnel-Connection-ID', 'type':AVP_TYPE_STR},	# Vendor 0
	69:{'name':'Tunnel-Password', 'type':AVP_TYPE_STR},	# Vendor 0
	70:{'name':'ARAP-Password', 'type':AVP_TYPE_STR},	# Vendor 0
	71:{'name':'ARAP-Features', 'type':AVP_TYPE_STR},	# Vendor 0
	72:{'name':'ARAP-Zone-Access', 'type':AVP_TYPE_INT32},	# Vendor 0
	73:{'name':'ARAP-Security', 'type':AVP_TYPE_UINT32},	# Vendor 0
	74:{'name':'ARAP-Security-Data', 'type':AVP_TYPE_STR},	# Vendor 0
	75:{'name':'Password-Retry', 'type':AVP_TYPE_UINT32},	# Vendor 0
	76:{'name':'Prompt', 'type':AVP_TYPE_INT32},	# Vendor 0
	77:{'name':'Connect-Info', 'type':AVP_TYPE_STR},	# Vendor 0
	78:{'name':'Configuration-Token', 'type':AVP_TYPE_STR},	# Vendor 0
	79:{'name':'EAP-Message', 'type':AVP_TYPE_STR},	# Vendor 0
	80:{'name':'Signature', 'type':AVP_TYPE_STR},	# Vendor 0
	81:{'name':'Tunnel-Private-Group-Id', 'type':AVP_TYPE_STR},	# Vendor 0
	82:{'name':'Tunnel-Assignment-Id', 'type':AVP_TYPE_STR},	# Vendor 0
	83:{'name':'Tunnel-Preference', 'type':AVP_TYPE_UINT32},	# Vendor 0
	84:{'name':'ARAP-Challenge-Response', 'type':AVP_TYPE_STR},	# Vendor 0
	85:{'name':'Acct-Interim-Interval', 'type':AVP_TYPE_UINT32},	# Vendor 0
	86:{'name':'Acct-Tunnel-Packets-Lost', 'type':AVP_TYPE_UINT32},	# Vendor 0
	87:{'name':'NAS-Port-Id', 'type':AVP_TYPE_STR},	# Vendor 0
	88:{'name':'Framed-Pool', 'type':AVP_TYPE_STR},	# Vendor 0
	89:{'name':'CUI', 'type':AVP_TYPE_STR},	# Vendor 0
	90:{'name':'Tunnel-Client-Auth-Id', 'type':AVP_TYPE_STR},	# Vendor 0
	91:{'name':'Tunnel-Server-Auth-Id', 'type':AVP_TYPE_STR},	# Vendor 0
	92:{'name':'NAS-Filter-Rule', 'type':AVP_TYPE_STR},	# Vendor 0
	93:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	94:{'name':'Originating-Line-Info', 'type':AVP_TYPE_STR},	# Vendor 0
	95:{'name':'NAS-IPv6-Address', 'type':AVP_TYPE_STR},	# Vendor 0
	96:{'name':'Framed-Interface-Id', 'type':AVP_TYPE_UINT64},	# Vendor 0
	97:{'name':'Framed-IPv6-Prefix', 'type':AVP_TYPE_STR},	# Vendor 0
	98:{'name':'Login-IPv6-Host', 'type':AVP_TYPE_STR},	# Vendor 0
	99:{'name':'Framed-IPv6-Route', 'type':AVP_TYPE_STR},	# Vendor 0
	100:{'name':'Framed-IPv6-Pool', 'type':AVP_TYPE_STR},	# Vendor 0
	101:{'name':'Error-Cause', 'type':AVP_TYPE_INT32},	# Vendor 0
	102:{'name':'EAP-Key-Name', 'type':AVP_TYPE_STR},	# Vendor 0
	103:{'name':'Digest-Response', 'type':AVP_TYPE_STR},	# Vendor 0
	104:{'name':'Digest-Realm', 'type':AVP_TYPE_STR},	# Vendor 0
	105:{'name':'Digest-Nonce', 'type':AVP_TYPE_STR},	# Vendor 0
	106:{'name':'Digest-Response-Auth', 'type':AVP_TYPE_STR},	# Vendor 0
	107:{'name':'Digest-Nextnonce', 'type':AVP_TYPE_STR},	# Vendor 0
	108:{'name':'Digest-Method', 'type':AVP_TYPE_STR},	# Vendor 0
	109:{'name':'Digest-URI', 'type':AVP_TYPE_STR},	# Vendor 0
	110:{'name':'Digest-Qop', 'type':AVP_TYPE_STR},	# Vendor 0
	111:{'name':'Digest-Algorithm', 'type':AVP_TYPE_STR},	# Vendor 0
	112:{'name':'Digest-Entity-Body-Hash', 'type':AVP_TYPE_STR},	# Vendor 0
	113:{'name':'Digest-Digest-CNonce', 'type':AVP_TYPE_STR},	# Vendor 0
	114:{'name':'Digest-Nonce-Count', 'type':AVP_TYPE_STR},	# Vendor 0
	115:{'name':'Digest-Username', 'type':AVP_TYPE_STR},	# Vendor 0
	116:{'name':'Digest-Opaque', 'type':AVP_TYPE_STR},	# Vendor 0
	117:{'name':'Digest-Auth-Param', 'type':AVP_TYPE_STR},	# Vendor 0
	118:{'name':'Digest-AKA-Auts', 'type':AVP_TYPE_STR},	# Vendor 0
	119:{'name':'Digest-Domain', 'type':AVP_TYPE_STR},	# Vendor 0
	120:{'name':'Digest-Stale', 'type':AVP_TYPE_STR},	# Vendor 0
	121:{'name':'Digest-HA1', 'type':AVP_TYPE_STR},	# Vendor 0
	122:{'name':'SIP-AOR', 'type':AVP_TYPE_STR},	# Vendor 0
	123:{'name':'Delegated-IPv6-Prefix', 'type':AVP_TYPE_STR},	# Vendor 0
	124:{'name':'MIP6-Feature-Vector', 'type':AVP_TYPE_UINT64},	# Vendor 0
	125:{'name':'MIP6-Home-Link-Prefix', 'type':AVP_TYPE_STR},	# Vendor 0
	126:{'name':'Operator-Name', 'type':AVP_TYPE_STR},	# Vendor 0
	127:{'name':'Location-Information', 'type':AVP_TYPE_STR},	# Vendor 0
	128:{'name':'Location-Data', 'type':AVP_TYPE_STR},	# Vendor 0
	129:{'name':'Basic-Location-Policy-Rules', 'type':AVP_TYPE_STR},	# Vendor 0
	130:{'name':'Extended-Location-Policy-Rules', 'type':AVP_TYPE_STR},	# Vendor 0
	131:{'name':'Location-Capable', 'type':AVP_TYPE_STR},	# Vendor 0
	132:{'name':'Requested-Location-Info', 'type':AVP_TYPE_STR},	# Vendor 0
	133:{'name':'Framed-Management-Protocol', 'type':AVP_TYPE_INT32},	# Vendor 0
	134:{'name':'Management-Transport-Protection', 'type':AVP_TYPE_INT32},	# Vendor 0
	135:{'name':'Management-Policy-Id', 'type':AVP_TYPE_STR},	# Vendor 0
	136:{'name':'Management-Privilege-Level', 'type':AVP_TYPE_INT32},	# Vendor 0
	137:{'name':'PKM-SS-Cert', 'type':AVP_TYPE_STR},	# Vendor 0
	138:{'name':'PKM-CA-Cert', 'type':AVP_TYPE_STR},	# Vendor 0
	139:{'name':'PKM-Config-Settings', 'type':AVP_TYPE_STR},	# Vendor 0
	140:{'name':'PKM-Cryptosuite-List', 'type':AVP_TYPE_STR},	# Vendor 0
	141:{'name':'PPKM-SAID', 'type':AVP_TYPE_STR},	# Vendor 0
	142:{'name':'PKM-SA-Descriptor', 'type':AVP_TYPE_STR},	# Vendor 0
	143:{'name':'PKM-Auth-Key', 'type':AVP_TYPE_STR},	# Vendor 0
	144:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	145:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	146:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	147:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	148:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	149:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	150:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	151:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	152:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	153:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	154:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	155:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	156:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	157:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	158:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	159:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	160:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	161:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	162:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	163:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	164:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	165:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	166:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	167:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	168:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	169:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	170:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	171:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	172:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	173:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	174:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	175:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	176:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	177:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	178:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	179:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	180:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	181:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	182:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	183:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	184:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	185:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	186:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	187:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	188:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	189:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	190:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	191:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	192:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	193:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	194:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	195:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	196:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	197:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	198:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	199:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	200:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	201:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	202:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	203:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	204:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	205:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	206:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	207:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	208:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	209:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	210:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	211:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	212:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	213:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	214:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	215:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	216:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	217:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	218:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	219:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	220:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	221:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	222:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	223:{'name':'Experimental-Use', 'type':AVP_TYPE_STR},	# Vendor 0
	224:{'name':'Implementation-Specific', 'type':AVP_TYPE_STR},	# Vendor 0
	225:{'name':'Implementation-Specific', 'type':AVP_TYPE_STR},	# Vendor 0
	226:{'name':'Implementation-Specific', 'type':AVP_TYPE_STR},	# Vendor 0
	227:{'name':'Implementation-Specific', 'type':AVP_TYPE_STR},	# Vendor 0
	228:{'name':'Implementation-Specific', 'type':AVP_TYPE_STR},	# Vendor 0
	229:{'name':'Implementation-Specific', 'type':AVP_TYPE_STR},	# Vendor 0
	230:{'name':'Implementation-Specific', 'type':AVP_TYPE_STR},	# Vendor 0
	231:{'name':'Implementation-Specific', 'type':AVP_TYPE_STR},	# Vendor 0
	232:{'name':'Implementation-Specific', 'type':AVP_TYPE_STR},	# Vendor 0
	233:{'name':'Implementation-Specific', 'type':AVP_TYPE_STR},	# Vendor 0
	234:{'name':'Implementation-Specific', 'type':AVP_TYPE_STR},	# Vendor 0
	235:{'name':'Implementation-Specific', 'type':AVP_TYPE_STR},	# Vendor 0
	236:{'name':'Implementation-Specific', 'type':AVP_TYPE_STR},	# Vendor 0
	237:{'name':'Implementation-Specific', 'type':AVP_TYPE_STR},	# Vendor 0
	238:{'name':'Implementation-Specific', 'type':AVP_TYPE_STR},	# Vendor 0
	239:{'name':'Implementation-Specific', 'type':AVP_TYPE_STR},	# Vendor 0
	240:{'name':'Implementation-Specific', 'type':AVP_TYPE_STR},	# Vendor 0
	241:{'name':'Reserved', 'type':AVP_TYPE_STR},	# Vendor 0
	242:{'name':'Reserved', 'type':AVP_TYPE_STR},	# Vendor 0
	243:{'name':'Reserved', 'type':AVP_TYPE_STR},	# Vendor 0
	244:{'name':'Reserved', 'type':AVP_TYPE_STR},	# Vendor 0
	245:{'name':'Reserved', 'type':AVP_TYPE_STR},	# Vendor 0
	246:{'name':'Reserved', 'type':AVP_TYPE_STR},	# Vendor 0
	247:{'name':'Reserved', 'type':AVP_TYPE_STR},	# Vendor 0
	248:{'name':'Reserved', 'type':AVP_TYPE_STR},	# Vendor 0
	249:{'name':'Reserved', 'type':AVP_TYPE_STR},	# Vendor 0
	250:{'name':'Reserved', 'type':AVP_TYPE_STR},	# Vendor 0
	251:{'name':'Reserved', 'type':AVP_TYPE_STR},	# Vendor 0
	252:{'name':'Reserved', 'type':AVP_TYPE_STR},	# Vendor 0
	253:{'name':'Reserved', 'type':AVP_TYPE_STR},	# Vendor 0
	254:{'name':'Reserved', 'type':AVP_TYPE_STR},	# Vendor 0
	255:{'name':'Reserved', 'type':AVP_TYPE_STR},	# Vendor 0
	256:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	257:{'name':'Host-IP-Address', 'type':AVP_TYPE_STR},	# Vendor 0
	258:{'name':'Auth-Application-Id', 'type':AVP_TYPE_INT32},	# Vendor 0
	259:{'name':'Acct-Application-Id', 'type':AVP_TYPE_INT32},	# Vendor 0
	260:{'name':'Vendor-Specific-Application-Id', 'type':AVP_TYPE_GROUP},	# Vendor 0
	261:{'name':'Redirect-Host-Usage', 'type':AVP_TYPE_INT32},	# Vendor 0
	262:{'name':'Redirect-Max-Cache-Time', 'type':AVP_TYPE_UINT32},	# Vendor 0
	263:{'name':'Session-Id', 'type':AVP_TYPE_STR},	# Vendor 0
	264:{'name':'Origin-Host', 'type':AVP_TYPE_STR},	# Vendor 0
	265:{'name':'Supported-Vendor-Id', 'type':AVP_TYPE_INT32},	# Vendor 0
	266:{'name':'Vendor-Id', 'type':AVP_TYPE_INT32},	# Vendor 0
	267:{'name':'Firmware-Revision', 'type':AVP_TYPE_UINT32},	# Vendor 0
	268:{'name':'Result-Code', 'type':AVP_TYPE_UINT32},	# Vendor 0
	269:{'name':'Product-Name', 'type':AVP_TYPE_STR},	# Vendor 0
	270:{'name':'Session-Binding', 'type':AVP_TYPE_UINT32},	# Vendor 0
	271:{'name':'Session-Server-Failover', 'type':AVP_TYPE_UINT32},	# Vendor 0
	272:{'name':'Multi-Round-Time-Out', 'type':AVP_TYPE_UINT32},	# Vendor 0
	273:{'name':'Disconnect-Cause', 'type':AVP_TYPE_INT32},	# Vendor 0
	274:{'name':'Auth-Request-Type', 'type':AVP_TYPE_UINT32},	# Vendor 0
	275:{'name':'Alternate-Peer', 'type':AVP_TYPE_STR},	# Vendor 0
	276:{'name':'Auth-Grace-Period', 'type':AVP_TYPE_UINT32},	# Vendor 0
	277:{'name':'Auth-Session-State', 'type':AVP_TYPE_UINT32},	# Vendor 0
	278:{'name':'Origin-State-Id', 'type':AVP_TYPE_UINT32},	# Vendor 0
	279:{'name':'Failed-AVP', 'type':AVP_TYPE_GROUP},	# Vendor 0
	280:{'name':'Proxy-Host', 'type':AVP_TYPE_STR},	# Vendor 0
	281:{'name':'Error-Message', 'type':AVP_TYPE_STR},	# Vendor 0
	282:{'name':'Route-Record', 'type':AVP_TYPE_STR},	# Vendor 0
	283:{'name':'Destination-Realm', 'type':AVP_TYPE_STR},	# Vendor 0
	284:{'name':'Proxy-Info', 'type':AVP_TYPE_GROUP},	# Vendor 0
	285:{'name':'Re-Auth-Request-Type', 'type':AVP_TYPE_UINT32},	# Vendor 0
	286:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	287:{'name':'Accounting-Sub-Session-Id', 'type':AVP_TYPE_UINT64},	# Vendor 0
	288:{'name':'Unallocated', 'type':AVP_TYPE_STR},	# Vendor 0
	289:{'name':'Unallocated', 'type':AVP_TYPE_STR},	# Vendor 0
	290:{'name':'Unallocated', 'type':AVP_TYPE_STR},	# Vendor 0
	291:{'name':'Authorization-Lifetime', 'type':AVP_TYPE_INT32},	# Vendor 0
	292:{'name':'Redirect-Host', 'type':AVP_TYPE_STR},	# Vendor 0
	293:{'name':'Destination-Host', 'type':AVP_TYPE_STR},	# Vendor 0
	294:{'name':'Error-Reporting-Host', 'type':AVP_TYPE_STR},	# Vendor 0
	295:{'name':'Termination-Cause', 'type':AVP_TYPE_INT32},	# Vendor 0
	296:{'name':'Origin-Realm', 'type':AVP_TYPE_STR},	# Vendor 0
	297:{'name':'Experimental-Result', 'type':AVP_TYPE_GROUP},	# Vendor 0
	298:{'name':'Experimental-Result-Code', 'type':AVP_TYPE_UINT32},	# Vendor 0
	299:{'name':'Inband-Security-Id', 'type':AVP_TYPE_UINT32},	# Vendor 0
	300:{'name':'E2E-Sequence', 'type':AVP_TYPE_GROUP},	# Vendor 0
	301:{'name':'Unallocated', 'type':AVP_TYPE_STR},	# Vendor 0
	302:{'name':'Unallocated', 'type':AVP_TYPE_STR},	# Vendor 0
	303:{'name':'Unallocated', 'type':AVP_TYPE_STR},	# Vendor 0
	304:{'name':'Unallocated', 'type':AVP_TYPE_STR},	# Vendor 0
	305:{'name':'Unallocated', 'type':AVP_TYPE_STR},	# Vendor 0
	306:{'name':'Unallocated', 'type':AVP_TYPE_STR},	# Vendor 0
	307:{'name':'Unallocated', 'type':AVP_TYPE_STR},	# Vendor 0
	308:{'name':'Unallocated', 'type':AVP_TYPE_STR},	# Vendor 0
	309:{'name':'Unallocated', 'type':AVP_TYPE_STR},	# Vendor 0
	310:{'name':'Unallocated', 'type':AVP_TYPE_STR},	# Vendor 0
	311:{'name':'Unallocated', 'type':AVP_TYPE_STR},	# Vendor 0
	312:{'name':'Unallocated', 'type':AVP_TYPE_STR},	# Vendor 0
	313:{'name':'Unallocated', 'type':AVP_TYPE_STR},	# Vendor 0
	314:{'name':'Unallocated', 'type':AVP_TYPE_STR},	# Vendor 0
	315:{'name':'Unallocated', 'type':AVP_TYPE_STR},	# Vendor 0
	316:{'name':'Unallocated', 'type':AVP_TYPE_STR},	# Vendor 0
	317:{'name':'Unallocated', 'type':AVP_TYPE_STR},	# Vendor 0
	318:{'name':'MIP-FA-to-HA-SPI', 'type':AVP_TYPE_UINT32},	# Vendor 0
	319:{'name':'MIP-FA-to-MN-SPI', 'type':AVP_TYPE_UINT32},	# Vendor 0
	320:{'name':'MIP-Reg-Request', 'type':AVP_TYPE_STR},	# Vendor 0
	321:{'name':'MIP-Reg-Reply', 'type':AVP_TYPE_STR},	# Vendor 0
	322:{'name':'MIP-MN-AAA-Auth', 'type':AVP_TYPE_GROUP},	# Vendor 0
	323:{'name':'MIP-HA-to-FA-SPI', 'type':AVP_TYPE_UINT32},	# Vendor 0
	324:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	325:{'name':'MIP-MN-to-FA-MSA', 'type':AVP_TYPE_GROUP},	# Vendor 0
	326:{'name':'MIP-FA-to-MN-MSA', 'type':AVP_TYPE_GROUP},	# Vendor 0
	327:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	328:{'name':'MIP-FA-to-HA-MSA', 'type':AVP_TYPE_GROUP},	# Vendor 0
	329:{'name':'MIP-HA-to-FA-MSA', 'type':AVP_TYPE_GROUP},	# Vendor 0
	330:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	331:{'name':'MIP-MN-to-HA-MSA', 'type':AVP_TYPE_GROUP},	# Vendor 0
	332:{'name':'MIP-HA-to-MN-MSA', 'type':AVP_TYPE_GROUP},	# Vendor 0
	333:{'name':'MIP-Mobile-Node-Address', 'type':AVP_TYPE_STR},	# Vendor 0
	334:{'name':'MIP-Home-Agent-Address', 'type':AVP_TYPE_STR},	# Vendor 0
	335:{'name':'MIP-Nonce', 'type':AVP_TYPE_STR},	# Vendor 0
	336:{'name':'MIP-Candidate-Home-Agent-Host', 'type':AVP_TYPE_STR},	# Vendor 0
	337:{'name':'MIP-Feature-Vector', 'type':AVP_TYPE_UINT32},	# Vendor 0
	338:{'name':'MIP-Auth-Input-Data-Length', 'type':AVP_TYPE_UINT32},	# Vendor 0
	339:{'name':'MIP-Authenticator-Length', 'type':AVP_TYPE_UINT32},	# Vendor 0
	340:{'name':'MIP-Authenticator-Offset', 'type':AVP_TYPE_UINT32},	# Vendor 0
	341:{'name':'MIP-MN-AAA-SPI', 'type':AVP_TYPE_UINT32},	# Vendor 0
	342:{'name':'MIP-Filter-Rule', 'type':AVP_TYPE_STR},	# Vendor 0
	343:{'name':'MIP-Session-Key', 'type':AVP_TYPE_STR},	# Vendor 0
	344:{'name':'MIP-FA-Challenge', 'type':AVP_TYPE_STR},	# Vendor 0
	345:{'name':'MIP-Algorithm-Type', 'type':AVP_TYPE_UINT32},	# Vendor 0
	346:{'name':'MIP-Replay-Mode', 'type':AVP_TYPE_UINT32},	# Vendor 0
	347:{'name':'MIP-Originating-Foreign-AAA', 'type':AVP_TYPE_GROUP},	# Vendor 0
	348:{'name':'MIP-Home-Agent-Host', 'type':AVP_TYPE_GROUP},	# Vendor 0
	349:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	350:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	351:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	352:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	353:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	354:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	355:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	356:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	357:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	358:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	359:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	360:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	361:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	362:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	363:{'name':'Accounting-Input-Octets', 'type':AVP_TYPE_UINT64},	# Vendor 0
	364:{'name':'Accounting-Output-Octets', 'type':AVP_TYPE_UINT64},	# Vendor 0
	365:{'name':'Accounting-Input-Packets', 'type':AVP_TYPE_UINT64},	# Vendor 0
	366:{'name':'Accounting-Output-Packets', 'type':AVP_TYPE_UINT64},	# Vendor 0
	367:{'name':'MIP-MSA-Lifetime', 'type':AVP_TYPE_UINT32},	# Vendor 0
	368:{'name':'SIP-Accounting-Information', 'type':AVP_TYPE_GROUP},	# Vendor 0
	369:{'name':'SIP-Accounting-Server-URI', 'type':AVP_TYPE_STR},	# Vendor 0
	370:{'name':'SIP-Credit-Control-Server-URI', 'type':AVP_TYPE_STR},	# Vendor 0
	371:{'name':'SIP-Server-URI', 'type':AVP_TYPE_STR},	# Vendor 0
	372:{'name':'SIP-Server-Capabilities', 'type':AVP_TYPE_GROUP},	# Vendor 0
	373:{'name':'SIP-Mandatory-Capability', 'type':AVP_TYPE_UINT32},	# Vendor 0
	374:{'name':'SIP-Optional-Capability', 'type':AVP_TYPE_UINT32},	# Vendor 0
	375:{'name':'SIP-Server-Assignment-Type', 'type':AVP_TYPE_INT32},	# Vendor 0
	376:{'name':'SIP-Auth-Data-Item', 'type':AVP_TYPE_GROUP},	# Vendor 0
	377:{'name':'SIP-Authentication-Scheme', 'type':AVP_TYPE_INT32},	# Vendor 0
	378:{'name':'SIP-Item-Number', 'type':AVP_TYPE_UINT32},	# Vendor 0
	379:{'name':'SIP-Authenticate', 'type':AVP_TYPE_GROUP},	# Vendor 0
	380:{'name':'SIP-Authorization', 'type':AVP_TYPE_GROUP},	# Vendor 0
	381:{'name':'SIP-Authentication-Info', 'type':AVP_TYPE_GROUP},	# Vendor 0
	382:{'name':'SIP-Number-Auth-Items', 'type':AVP_TYPE_UINT32},	# Vendor 0
	383:{'name':'SIP-Deregistration-Reason', 'type':AVP_TYPE_GROUP},	# Vendor 0
	384:{'name':'SIP-Reason-Code', 'type':AVP_TYPE_INT32},	# Vendor 0
	385:{'name':'SIP-Reason-Info', 'type':AVP_TYPE_STR},	# Vendor 0
	386:{'name':'SIP-Visited-Network-Id', 'type':AVP_TYPE_STR},	# Vendor 0
	387:{'name':'SIP-User-Authorization-Type', 'type':AVP_TYPE_INT32},	# Vendor 0
	388:{'name':'SIP-Supported-User-Data-Type', 'type':AVP_TYPE_STR},	# Vendor 0
	389:{'name':'SIP-User-Data', 'type':AVP_TYPE_GROUP},	# Vendor 0
	390:{'name':'SIP-User-Data-Type', 'type':AVP_TYPE_STR},	# Vendor 0
	391:{'name':'SIP-User-Data-Contents', 'type':AVP_TYPE_STR},	# Vendor 0
	392:{'name':'SIP-User-Data-Already-Available', 'type':AVP_TYPE_INT32},	# Vendor 0
	393:{'name':'SIP-Method', 'type':AVP_TYPE_STR},	# Vendor 0
	394:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	395:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	396:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	397:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	398:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	399:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	400:{'name':'NAS-Filter-Rule', 'type':AVP_TYPE_STR},	# Vendor 0
	401:{'name':'Tunneling', 'type':AVP_TYPE_GROUP},	# Vendor 0
	402:{'name':'CHAP-Auth', 'type':AVP_TYPE_GROUP},	# Vendor 0
	403:{'name':'CHAP-Algorithm', 'type':AVP_TYPE_INT32},	# Vendor 0
	404:{'name':'CHAP-Ident', 'type':AVP_TYPE_STR},	# Vendor 0
	405:{'name':'CHAP-Response', 'type':AVP_TYPE_STR},	# Vendor 0
	406:{'name':'Accounting-Auth-Method', 'type':AVP_TYPE_INT32},	# Vendor 0
	407:{'name':'QoS-Filter-Rule', 'type':AVP_TYPE_STR},	# Vendor 0
	408:{'name':'Origin-AAA-Protocol', 'type':AVP_TYPE_INT32},	# Vendor 0
	409:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	410:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	411:{'name':'CC-Correlation-Id', 'type':AVP_TYPE_STR},	# Vendor 0
	412:{'name':'CC-Input-Octets', 'type':AVP_TYPE_UINT64},	# Vendor 0
	413:{'name':'CC-Money', 'type':AVP_TYPE_GROUP},	# Vendor 0
	414:{'name':'CC-Output-Octets', 'type':AVP_TYPE_UINT64},	# Vendor 0
	415:{'name':'CC-Request-Number', 'type':AVP_TYPE_UINT32},	# Vendor 0
	416:{'name':'CC-Request-Type', 'type':AVP_TYPE_UINT32},	# Vendor 0
	417:{'name':'CC-Service-Specific-Units', 'type':AVP_TYPE_UINT64},	# Vendor 0
	418:{'name':'CC-Session-Failover', 'type':AVP_TYPE_INT32},	# Vendor 0
	419:{'name':'CC-Sub-Session-Id', 'type':AVP_TYPE_UINT64},	# Vendor 0
	420:{'name':'CC-Time', 'type':AVP_TYPE_UINT32},	# Vendor 0
	421:{'name':'CC-Total-Octets', 'type':AVP_TYPE_UINT64},	# Vendor 0
	422:{'name':'Check-Balance-Result', 'type':AVP_TYPE_INT32},	# Vendor 0
	423:{'name':'Cost-Information', 'type':AVP_TYPE_GROUP},	# Vendor 0
	424:{'name':'Cost-Unit', 'type':AVP_TYPE_STR},	# Vendor 0
	425:{'name':'Currency-Code', 'type':AVP_TYPE_UINT32},	# Vendor 0
	426:{'name':'Credit-Control', 'type':AVP_TYPE_INT32},	# Vendor 0
	427:{'name':'Credit-Control-Failure-Handling', 'type':AVP_TYPE_INT32},	# Vendor 0
	428:{'name':'Direct-Debiting-Failure-Handling', 'type':AVP_TYPE_INT32},	# Vendor 0
	429:{'name':'Exponent', 'type':AVP_TYPE_INT32},	# Vendor 0
	430:{'name':'Final-Unit-Indication', 'type':AVP_TYPE_GROUP},	# Vendor 0
	431:{'name':'Granted-Service-Unit', 'type':AVP_TYPE_GROUP},	# Vendor 0
	432:{'name':'Rating-Group', 'type':AVP_TYPE_UINT32},	# Vendor 0
	433:{'name':'Redirect-Address-Type', 'type':AVP_TYPE_INT32},	# Vendor 0
	434:{'name':'Redirect-Server', 'type':AVP_TYPE_GROUP},	# Vendor 0
	435:{'name':'Redirect-Server-Address', 'type':AVP_TYPE_STR},	# Vendor 0
	436:{'name':'Requested-Action', 'type':AVP_TYPE_INT32},	# Vendor 0
	437:{'name':'Requested-Service-Unit', 'type':AVP_TYPE_GROUP},	# Vendor 0
	438:{'name':'Restricted-Filter-Rule', 'type':AVP_TYPE_STR},	# Vendor 0
	439:{'name':'Service-Identifier', 'type':AVP_TYPE_UINT32},	# Vendor 0
	440:{'name':'Service-Parameter-Info', 'type':AVP_TYPE_GROUP},	# Vendor 0
	441:{'name':'Service-Parameter-Type', 'type':AVP_TYPE_UINT32},	# Vendor 0
	442:{'name':'Service-Parameter-Value', 'type':AVP_TYPE_STR},	# Vendor 0
	443:{'name':'Subscription-Id', 'type':AVP_TYPE_GROUP},	# Vendor 0
	444:{'name':'Subscription-Id-Data', 'type':AVP_TYPE_STR},	# Vendor 0
	445:{'name':'Unit-Value', 'type':AVP_TYPE_GROUP},	# Vendor 0
	446:{'name':'Used-Service-Unit', 'type':AVP_TYPE_GROUP},	# Vendor 0
	447:{'name':'Value-Digits', 'type':AVP_TYPE_INT64},	# Vendor 0
	448:{'name':'Validity-Time', 'type':AVP_TYPE_UINT32},	# Vendor 0
	449:{'name':'Final-Unit-Action', 'type':AVP_TYPE_INT32},	# Vendor 0
	450:{'name':'Subscription-Id-Type', 'type':AVP_TYPE_UINT32},	# Vendor 0
	451:{'name':'Tariff-Time-Change', 'type':AVP_TYPE_STR},	# Vendor 0
	452:{'name':'Tariff-Change-Usage', 'type':AVP_TYPE_INT32},	# Vendor 0
	453:{'name':'G-S-U-Pool-Identifier', 'type':AVP_TYPE_UINT32},	# Vendor 0
	454:{'name':'CC-Unit-Type', 'type':AVP_TYPE_INT32},	# Vendor 0
	455:{'name':'Multiple-Services-Indicator', 'type':AVP_TYPE_INT32},	# Vendor 0
	456:{'name':'Multiple-Services-Credit-Control', 'type':AVP_TYPE_GROUP},	# Vendor 0
	457:{'name':'G-S-U-Pool-Reference', 'type':AVP_TYPE_GROUP},	# Vendor 0
	458:{'name':'User-Equipment-Info', 'type':AVP_TYPE_GROUP},	# Vendor 0
	459:{'name':'User-Equipment-Info-Type', 'type':AVP_TYPE_INT32},	# Vendor 0
	460:{'name':'User-Equipment-Info-Value', 'type':AVP_TYPE_STR},	# Vendor 0
	461:{'name':'Service-Context-Id', 'type':AVP_TYPE_STR},	# Vendor 0
	462:{'name':'EAP-Payload', 'type':AVP_TYPE_STR},	# Vendor 0
	463:{'name':'EAP-Reissued-Payload', 'type':AVP_TYPE_STR},	# Vendor 0
	464:{'name':'EAP-Master-Session-Key', 'type':AVP_TYPE_STR},	# Vendor 0
	465:{'name':'Accounting-EAP-Auth-Method', 'type':AVP_TYPE_UINT64},	# Vendor 0
	466:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	467:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	468:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	469:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	470:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	471:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	472:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	473:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	474:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	475:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	476:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	477:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	478:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	479:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	480:{'name':'Accounting-Record-Type', 'type':AVP_TYPE_INT32},	# Vendor 0
	481:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	482:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	483:{'name':'Accounting-Realtime-Required', 'type':AVP_TYPE_UINT32},	# Vendor 0
	484:{'name':'Unassigned', 'type':AVP_TYPE_STR},	# Vendor 0
	485:{'name':'Accounting-Record-Number', 'type':AVP_TYPE_UINT32},	# Vendor 0
	486:{'name':'MIP6-Agent-Info', 'type':AVP_TYPE_GROUP},	# Vendor 0
	487:{'name':'MIP-Careof-Address', 'type':AVP_TYPE_STR},	# Vendor 0
	488:{'name':'MIP-Authenticator', 'type':AVP_TYPE_STR},	# Vendor 0
	489:{'name':'MIP-MAC-Mobility-Data', 'type':AVP_TYPE_STR},	# Vendor 0
	490:{'name':'MIP-Timestamp', 'type':AVP_TYPE_STR},	# Vendor 0
	491:{'name':'MIP-MN-HA-SPI', 'type':AVP_TYPE_UINT32},	# Vendor 0
	492:{'name':'MIP-MN-HA-MSA', 'type':AVP_TYPE_GROUP},	# Vendor 0
	493:{'name':'Service-Selection', 'type':AVP_TYPE_STR},	# Vendor 0
	494:{'name':'MIP6-Auth-Mode', 'type':AVP_TYPE_INT32},	# Vendor 0
	495:{'name':'TMOD-1', 'type':AVP_TYPE_GROUP},	# Vendor 0
	496:{'name':'Token-Rate', 'type':AVP_TYPE_FLOAT32},	# Vendor 0
	497:{'name':'Bucket-Depth', 'type':AVP_TYPE_FLOAT32},	# Vendor 0
	498:{'name':'Peak-Traffic-Rate', 'type':AVP_TYPE_FLOAT32},	# Vendor 0
	499:{'name':'Minimum-Policed-Unit', 'type':AVP_TYPE_UINT32},	# Vendor 0
	500:{'name':'Maximum-Packet-Size', 'type':AVP_TYPE_UINT32},	# Vendor 0
	501:{'name':'TMOD-2', 'type':AVP_TYPE_GROUP},	# Vendor 0
	502:{'name':'Bandwidth', 'type':AVP_TYPE_FLOAT32},	# Vendor 0
	503:{'name':'PHB-Class', 'type':AVP_TYPE_UINT32},	# Vendor 0
	504:{'name':'PMIP6-DHCP-Server-Address', 'type':AVP_TYPE_STR},	# Vendor 0
	505:{'name':'PMIP6-IPv4-Home-Address', 'type':AVP_TYPE_STR},	# Vendor 0
	506:{'name':'Mobile-Node-Identifier', 'type':AVP_TYPE_STR},	# Vendor 0
	507:{'name':'Service-Configuration', 'type':AVP_TYPE_GROUP},	# Vendor 0
	530:{'name':'Port', 'type':AVP_TYPE_INT32},	# Vendor 0
	531:{'name':'Port-Range', 'type':AVP_TYPE_GROUP},	# Vendor 0
	532:{'name':'Port-Start', 'type':AVP_TYPE_INT32},	# Vendor 0
	533:{'name':'Port-End', 'type':AVP_TYPE_INT32}	# Vendor 0
} ,
# Vendor 193 Ericsson
193:{
	261:{'name':'Acc-Service-Type', 'type':AVP_TYPE_INT32},	# Vendor 193
	1055:{'name':'Charging-Rule-Authorization', 'type':AVP_TYPE_GROUP},	# Vendor 193
	544:{'name':'Currency-Code', 'type':AVP_TYPE_UINT32},	# Vendor 193
	1057:{'name':'Authorization-State-Change-Time', 'type':AVP_TYPE_STR},	# Vendor 193
	290:{'name':'Rule-Space-Suggestion', 'type':AVP_TYPE_STR},	# Vendor 193
	291:{'name':'Rule-Space-Decision', 'type':AVP_TYPE_STR},	# Vendor 193
	292:{'name':'Bearer-Control-Options', 'type':AVP_TYPE_UINT32},	# Vendor 193
	553:{'name':'Subscription-Id', 'type':AVP_TYPE_GROUP},	# Vendor 193
	554:{'name':'Subscription-Id-Data', 'type':AVP_TYPE_STR},	# Vendor 193
	555:{'name':'Subscription-Id-Type', 'type':AVP_TYPE_UINT32},	# Vendor 193
	559:{'name':'Original-Subscription-Id', 'type':AVP_TYPE_GROUP},	# Vendor 193
	1056:{'name':'Authorization-State', 'type':AVP_TYPE_INT32},	# Vendor 193
	1060:{'name':'Gx-Capability-List', 'type':AVP_TYPE_UINT32},	# Vendor 193
	1059:{'name':'Next-Authorization-State', 'type':AVP_TYPE_INT32},	# Vendor 193
	600:{'name':'Abnormal-Termination-Reason', 'type':AVP_TYPE_UINT32},	# Vendor 193
	601:{'name':'Final-Unit-Indication', 'type':AVP_TYPE_UINT32},	# Vendor 193
	602:{'name':'Granted-Service-Unit', 'type':AVP_TYPE_GROUP},	# Vendor 193
	603:{'name':'Cost', 'type':AVP_TYPE_FLOAT64},	# Vendor 193
	604:{'name':'Cost-Information', 'type':AVP_TYPE_GROUP},	# Vendor 193
	605:{'name':'Accounting-Correlation-Id', 'type':AVP_TYPE_STR},	# Vendor 193
	606:{'name':'Requested-Service-Unit', 'type':AVP_TYPE_GROUP},	# Vendor 193
	607:{'name':'Service-Parameter-Info', 'type':AVP_TYPE_GROUP},	# Vendor 193
	608:{'name':'Service-Parameter-Type', 'type':AVP_TYPE_UINT32},	# Vendor 193
	609:{'name':'Service-Parameter-Value', 'type':AVP_TYPE_STR},	# Vendor 193
	610:{'name':'Event-Timestamp', 'type':AVP_TYPE_STR},	# Vendor 193
	611:{'name':'Unit-Type', 'type':AVP_TYPE_UINT32},	# Vendor 193
	612:{'name':'Unit-Value', 'type':AVP_TYPE_GROUP},	# Vendor 193
	613:{'name':'Used-Service-Unit', 'type':AVP_TYPE_GROUP},	# Vendor 193
	614:{'name':'Check-Balance-Result', 'type':AVP_TYPE_UINT32},	# Vendor 193
	615:{'name':'Requested-Action', 'type':AVP_TYPE_UINT32},	# Vendor 193
	616:{'name':'Exponent', 'type':AVP_TYPE_INT32},	# Vendor 193
	617:{'name':'Value-Digits', 'type':AVP_TYPE_UINT64},	# Vendor 193
	1146:{'name':'Customer-Id', 'type':AVP_TYPE_STR}	# Vendor 193
} ,
# Vendor 8164 Starent
8164:{
	512:{'name':'SN-Bandwidth-Control', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	513:{'name':'SN-Transparent-Data', 'type':AVP_TYPE_STR},	# Vendor 8164
	514:{'name':'SN-Traffic-Policy', 'type':AVP_TYPE_STR},	# Vendor 8164
	515:{'name':'SN-Firewall-Policy', 'type':AVP_TYPE_STR},	# Vendor 8164
	4:{'name':'SN-PPP-Progress-Code', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	517:{'name':'SN-Usage-Monitoring-Control', 'type':AVP_TYPE_GROUP},	# Vendor 8164
	518:{'name':'SN-Monitoring-Key', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	519:{'name':'SN-Usage-Volume', 'type':AVP_TYPE_UINT64},	# Vendor 8164
	520:{'name':'SN-Service-Flow-Detection', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	521:{'name':'SN-Usage-Monitoring', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	522:{'name':'Session-Start-Indicator', 'type':AVP_TYPE_STR},	# Vendor 8164
	523:{'name':'SN-Phase0-PSAPName', 'type':AVP_TYPE_STR},	# Vendor 8164
	525:{'name':'SN-Charging-Id', 'type':AVP_TYPE_STR},	# Vendor 8164
	526:{'name':'SN-Remaining-Service-Unit', 'type':AVP_TYPE_GROUP},	# Vendor 8164
	527:{'name':'SN-Service-Start-Timestamp', 'type':AVP_TYPE_STR},	# Vendor 8164
	528:{'name':'SN-Rulebase-Id', 'type':AVP_TYPE_STR},	# Vendor 8164
	529:{'name':'SN-CF-Policy-ID', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	530:{'name':'SN-Charging-Collection-Function-Name', 'type':AVP_TYPE_STR},	# Vendor 8164
	3:{'name':'SN-Disconnect-Reason', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	20:{'name':'SN-Subscriber-Permission', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	21:{'name':'SN-Admin-Permission', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	22:{'name':'SN-Simultaneous-SIP-MIP', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	23:{'name':'SN-Min-Compress-Size', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	24:{'name':'SN-Service-Type', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	25:{'name':'SN-DNS-Proxy-Use-Subscr-Addr', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	26:{'name':'SN-Tunnel-Password', 'type':AVP_TYPE_STR},	# Vendor 8164
	27:{'name':'SN-Tunnel-Load-Balancing', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	30:{'name':'SN-MN-HA-Timestamp-Tolerance', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	31:{'name':'SN-Prepaid-Compressed-Count', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	32:{'name':'SN-Prepaid-Inbound-Octets', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	33:{'name':'SN-Prepaid-Outbound-Octets', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	18:{'name':'SN-IP-Out-ACL', 'type':AVP_TYPE_STR},	# Vendor 8164
	35:{'name':'SN-Prepaid-Timeout', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	36:{'name':'SN-Prepaid-Watermark', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	37:{'name':'SN-NAI-Construction-Domain', 'type':AVP_TYPE_STR},	# Vendor 8164
	38:{'name':'SN-Tunnel-ISAKMP-Crypto-Map', 'type':AVP_TYPE_STR},	# Vendor 8164
	39:{'name':'SN-Tunnel-ISAKMP-Secret', 'type':AVP_TYPE_STR},	# Vendor 8164
	41:{'name':'SN-Ext-Inline-Srvr-Context', 'type':AVP_TYPE_STR},	# Vendor 8164
	43:{'name':'SN-L3-to-L2-Tun-Addr-Policy', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	44:{'name':'SN-Long-Duration-Timeout', 'type':AVP_TYPE_INT32},	# Vendor 8164
	45:{'name':'SN-Long-Duration-Action', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	46:{'name':'SN-PDSN-Handoff-Req-IP-Addr', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	47:{'name':'SN-HA-Send-DNS-ADDRESS', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	48:{'name':'SN-MIP-Send-Term-Verification', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	49:{'name':'SN-Data-Tunnel-Ignore-DF-Bit', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	50:{'name':'SN-MIP-AAA-Assign-Addr', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	51:{'name':'SN-MIP-Match-AAA-Assign-Addr', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	52:{'name':'SN-Proxy-MIP', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	53:{'name':'SN-IP-Alloc-Method', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	54:{'name':'SN-Gratuitous-ARP-Aggressive', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	55:{'name':'SN-Ext-Inline-Srvr-Up-Addr', 'type':AVP_TYPE_STR},	# Vendor 8164
	56:{'name':'SN-Ext-Inline-Srvr-Down-Addr', 'type':AVP_TYPE_STR},	# Vendor 8164
	57:{'name':'SN-Ext-Inline-Srvr-Preference', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	58:{'name':'SN-Ext-Inline-Srvr-Up-VLAN', 'type':AVP_TYPE_STR},	# Vendor 8164
	59:{'name':'SN-Ext-Inline-Srvr-Down-VLAN', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	60:{'name':'SN-IP-Hide-Service-Address', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	10:{'name':'SN-IP-Filter-In', 'type':AVP_TYPE_STR},	# Vendor 8164
	62:{'name':'SN-GTP-Version', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	63:{'name':'SN-Access-link-IP-Frag', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	64:{'name':'SN-Subscriber-Accounting', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	65:{'name':'SN-Nw-Reachability-Server-Name', 'type':AVP_TYPE_STR},	# Vendor 8164
	2:{'name':'SN-VPN-Name', 'type':AVP_TYPE_STR},	# Vendor 8164
	11:{'name':'SN-IP-Filter-Out', 'type':AVP_TYPE_STR},	# Vendor 8164
	68:{'name':'SN-GGSN-MIP-Required', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	69:{'name':'SN-Subscriber-Acct-Start', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	70:{'name':'SN-Subscriber-Acct-Interim', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	71:{'name':'SN-Subscriber-Acct-Stop', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	73:{'name':'SN-QoS-Tp-Dnlk', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	258:{'name':'SN-SIP-Request-Time-Stamp', 'type':AVP_TYPE_STR},	# Vendor 8164
	75:{'name':'SN-Tp-Dnlk-Peak-Data-Rate', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	76:{'name':'SN-Tp-Dnlk-Burst-Size', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	77:{'name':'SN-Tp-Dnlk-Exceed-Action', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	78:{'name':'SN-Tp-Dnlk-Violate-Action', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	13:{'name':'SN-Local-IP-Address', 'type':AVP_TYPE_STR},	# Vendor 8164
	80:{'name':'SN-Tp-Uplk-Committed-Data-Rate', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	81:{'name':'SN-Tp-Uplk-Peak-Data-Rate', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	82:{'name':'SN-Tp-Uplk-Burst-Size', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	83:{'name':'SN-Tp-Uplk-Exceed-Action', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	84:{'name':'SN-Tp-Uplk-Violate-Action', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	14:{'name':'SN-IP-Source-Validation', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	86:{'name':'SN-QoS-Conversation-Class', 'type':AVP_TYPE_STR},	# Vendor 8164
	87:{'name':'SN-QoS-Streaming-Class', 'type':AVP_TYPE_STR},	# Vendor 8164
	88:{'name':'SN-QoS-Interactive1-Class', 'type':AVP_TYPE_STR},	# Vendor 8164
	89:{'name':'SN-QoS-Interactive2-Class', 'type':AVP_TYPE_STR},	# Vendor 8164
	90:{'name':'SN-QoS-Interactive3-Class', 'type':AVP_TYPE_STR},	# Vendor 8164
	15:{'name':'SN-PPP-Outbound-Password', 'type':AVP_TYPE_STR},	# Vendor 8164
	92:{'name':'SN-PPP-NW-Layer-IPv4', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	93:{'name':'SN-PPP-NW-Layer-IPv6', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	94:{'name':'SN-Virtual-APN-Name', 'type':AVP_TYPE_STR},	# Vendor 8164
	95:{'name':'SN-PPP-Accept-Peer-v6Ifid', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	96:{'name':'SN-IPv6-rtr-advt-interval', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	97:{'name':'SN-IPv6-num-rtr-advt', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	98:{'name':'SN-NPU-Qos-Priority', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	99:{'name':'SN-MN-HA-Hash-Algorithm', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	100:{'name':'SN-Subscriber-Acct-Rsp-Action', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	101:{'name':'SN-IPv6-Primary-DNS', 'type':AVP_TYPE_STR},	# Vendor 8164
	102:{'name':'SN-IPv6-Secondary-DNS', 'type':AVP_TYPE_STR},	# Vendor 8164
	17:{'name':'SN-IP-In-ACL', 'type':AVP_TYPE_STR},	# Vendor 8164
	104:{'name':'SN-Mediation-VPN-Name', 'type':AVP_TYPE_STR},	# Vendor 8164
	105:{'name':'SN-Mediation-Acct-Rsp-Action', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	106:{'name':'SN-Home-Sub-Use-GGSN', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	103:{'name':'SN-IPv6-Egress-Filtering', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	108:{'name':'SN-Roaming-Sub-Use-GGSN', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	109:{'name':'SN-Home-Profile', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	110:{'name':'SN-IP-Src-Validation-Drop-Limit', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	111:{'name':'SN-QoS-Class-Conversational-PHB', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	112:{'name':'SN-QoS-Class-Streaming-PHB', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	113:{'name':'SN-QoS-Class-Background-PHB', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	114:{'name':'SN-QoS-Class-Interactive-1-PHB', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	19:{'name':'SN-PPP-Data-Compression-Mode', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	116:{'name':'SN-QoS-Class-Interactive-3-PHB', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	117:{'name':'SN-Visiting-Profile', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	118:{'name':'SN-Roaming-Profile', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	119:{'name':'SN-Home-Behavior', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	120:{'name':'SN-Visiting-Behavior', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	121:{'name':'SN-Roaming-Behavior', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	1146:{'name':'Customer-Id', 'type':AVP_TYPE_STR},	# Vendor 8164
	123:{'name':'SN-Mediation-Enabled', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	124:{'name':'SN-IPv6-Sec-Pool', 'type':AVP_TYPE_STR},	# Vendor 8164
	125:{'name':'SN-IPv6-Sec-Prefix', 'type':AVP_TYPE_STR},	# Vendor 8164
	126:{'name':'SN-IPv6-DNS-Proxy', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	127:{'name':'SN-Subscriber-Nexthop-Address', 'type':AVP_TYPE_STR},	# Vendor 8164
	128:{'name':'SN-Prepaid', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	129:{'name':'SN-Prepaid-Preference', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	130:{'name':'SN-PPP-Always-On-Vse', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	107:{'name':'SN-Visiting-Sub-Use-GGSN', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	259:{'name':'SN-SIP-Response-Time-Stamp', 'type':AVP_TYPE_STR},	# Vendor 8164
	133:{'name':'SN-Subscriber-No-Interims', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	134:{'name':'SN-Permit-User-Mcast-PDUs', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	135:{'name':'SN-Prepaid-Final-Duration-Alg', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	136:{'name':'SN-IPv6-Min-Link-MTU', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	137:{'name':'SN-Charging-VPN-Name', 'type':AVP_TYPE_STR},	# Vendor 8164
	138:{'name':'SN-Chrg-Char-Selection-Mode', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	139:{'name':'SN-Cause-For-Rec-Closing', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	140:{'name':'SN-Change-Condition', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	141:{'name':'SN-Dynamic-Addr-Alloc-Ind-Flag', 'type':AVP_TYPE_STR},	# Vendor 8164
	142:{'name':'SN-Ntk-Initiated-Ctx-Ind-Flag', 'type':AVP_TYPE_STR},	# Vendor 8164
	143:{'name':'SN-Ntk-Session-Disconnect-Flag', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	144:{'name':'SN-Enable-QoS-Renegotiation', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	145:{'name':'SN-QoS-Renegotiation-Timeout', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	146:{'name':'SN-Mediation-No-Interims', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	147:{'name':'SN-QoS-Negotiated', 'type':AVP_TYPE_STR},	# Vendor 8164
	148:{'name':'SN-Primary-NBNS-Server', 'type':AVP_TYPE_STR},	# Vendor 8164
	149:{'name':'SN-Secondary-NBNS-Server', 'type':AVP_TYPE_STR},	# Vendor 8164
	150:{'name':'SN-IP-Header-Compression', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	151:{'name':'SN-ROHC-Mode', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	152:{'name':'SN-Assigned-VLAN-ID', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	153:{'name':'SN-Direction', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	154:{'name':'SN-MIP-HA-Assignment-Table', 'type':AVP_TYPE_STR},	# Vendor 8164
	5:{'name':'SN-Primary-DNS-Server', 'type':AVP_TYPE_STR},	# Vendor 8164
	157:{'name':'SN-DHCP-Lease-Expiry-Policy', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	158:{'name':'SN-Subscriber-Template-Name', 'type':AVP_TYPE_STR},	# Vendor 8164
	159:{'name':'SN-Subs-IMSA-Service-Name', 'type':AVP_TYPE_STR},	# Vendor 8164
	161:{'name':'SN-Traffic-Group', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	162:{'name':'SN-Rad-APN-Name', 'type':AVP_TYPE_STR},	# Vendor 8164
	163:{'name':'SN-MIP-Send-Ancid', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	164:{'name':'SN-MIP-Send-Imsi', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	165:{'name':'SN-MIP-Dual-Anchor', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	166:{'name':'SN-MIP-ANCID', 'type':AVP_TYPE_STR},	# Vendor 8164
	167:{'name':'SN-IMS-AM-Address', 'type':AVP_TYPE_STR},	# Vendor 8164
	168:{'name':'SN-IMS-AM-Domain-Name', 'type':AVP_TYPE_STR},	# Vendor 8164
	169:{'name':'SN-Service-Address', 'type':AVP_TYPE_STR},	# Vendor 8164
	170:{'name':'SN-PDIF-MIP-Required', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	171:{'name':'SN-FMC-Location', 'type':AVP_TYPE_STR},	# Vendor 8164
	172:{'name':'SN-PDIF-MIP-Release-TIA', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	173:{'name':'SN-PDIF-MIP-Simple-IP-Fallback', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	174:{'name':'SN-Tunnel-Gn', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	175:{'name':'SN-MIP-Reg-Lifetime-Realm', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	176:{'name':'SN-Ecs-Data-Volume', 'type':AVP_TYPE_STR},	# Vendor 8164
	177:{'name':'SN-QoS-Traffic-Policy', 'type':AVP_TYPE_STR},	# Vendor 8164
	91:{'name':'SN-QoS-Background-Class', 'type':AVP_TYPE_STR},	# Vendor 8164
	115:{'name':'SN-QoS-Class-Interactive-2-PHB', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	1:{'name':'SN-VPN-ID', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	6:{'name':'SN-Secondary-DNS-Server', 'type':AVP_TYPE_STR},	# Vendor 8164
	187:{'name':'SN-PPP-Reneg-Disc', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	188:{'name':'SN-MIP-Send-Correlation-Info', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	190:{'name':'SN-PDSN-NAS-Id', 'type':AVP_TYPE_STR},	# Vendor 8164
	191:{'name':'SN-PDSN-NAS-IP-Address', 'type':AVP_TYPE_STR},	# Vendor 8164
	192:{'name':'SN-Subscriber-Acct-Mode', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	193:{'name':'SN-IP-In-Plcy-Grp', 'type':AVP_TYPE_STR},	# Vendor 8164
	194:{'name':'SN-IP-Out-Plcy-Grp', 'type':AVP_TYPE_STR},	# Vendor 8164
	196:{'name':'SN-IP-Source-Violate-No-Acct', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	198:{'name':'SN-Firewall-Enabled', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	204:{'name':'SN-Admin-Expiry', 'type':AVP_TYPE_INT32},	# Vendor 8164
	34:{'name':'SN-Prepaid-Total-Octets', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	214:{'name':'SN-DNS-Proxy-Intercept-List', 'type':AVP_TYPE_STR},	# Vendor 8164
	7:{'name':'SN-Re-CHAP-Interval', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	219:{'name':'SN-Subscriber-Class', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	220:{'name':'SN-CFPolicy-ID', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	122:{'name':'SN-Internal-SM-Index', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	223:{'name':'SN-Primary-DCCA-Peer', 'type':AVP_TYPE_STR},	# Vendor 8164
	224:{'name':'SN-Secondary-DCCA-Peer', 'type':AVP_TYPE_STR},	# Vendor 8164
	225:{'name':'SN-Subs-Acc-Flow-Traffic-Valid', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	226:{'name':'SN-Acct-Input-Packets-Dropped', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	227:{'name':'SN-Acct-Output-Packets-Dropped', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	228:{'name':'SN-Acct-Input-Octets-Dropped', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	229:{'name':'SN-Acct-Output-Octets-Dropped', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	230:{'name':'SN-Acct-Input-Giga-Dropped', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	231:{'name':'SN-Acct-Output-Giga-Dropped', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	232:{'name':'SN-Inactivity-Time', 'type':AVP_TYPE_INT32},	# Vendor 8164
	233:{'name':'SN-Overload-Disc-Connect-Time', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	234:{'name':'SN-Overload-Disc-Inact-Time', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	235:{'name':'SN-Overload-Disconnect', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	236:{'name':'SN-Radius-Returned-Username', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	237:{'name':'Prohibit-Payload-Compression', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	238:{'name':'SN-ROHC-Profile-Name', 'type':AVP_TYPE_STR},	# Vendor 8164
	239:{'name':'SN-Firewall-Policy', 'type':AVP_TYPE_STR},	# Vendor 8164
	240:{'name':'SN-LI-Dest-Address', 'type':AVP_TYPE_STR},	# Vendor 8164
	8:{'name':'SN-PDSN-Correlation-Id', 'type':AVP_TYPE_STR},	# Vendor 8164
	248:{'name':'SN-MS-ISDN', 'type':AVP_TYPE_STR},	# Vendor 8164
	249:{'name':'SN-Routing-Area-Id', 'type':AVP_TYPE_STR},	# Vendor 8164
	250:{'name':'SN-Rulebase', 'type':AVP_TYPE_STR},	# Vendor 8164
	251:{'name':'SN-Call-Id', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	252:{'name':'SN-IMSI', 'type':AVP_TYPE_STR},	# Vendor 8164
	253:{'name':'SN-Long-Duration-Notification', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	254:{'name':'SN-SIP-Method', 'type':AVP_TYPE_STR},	# Vendor 8164
	255:{'name':'SN-Event', 'type':AVP_TYPE_STR},	# Vendor 8164
	256:{'name':'SN-Role-Of-Node', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	257:{'name':'SN-Session-Id', 'type':AVP_TYPE_STR},	# Vendor 8164
	11010:{'name':'SN-Fast-Reauth-Username', 'type':AVP_TYPE_STR},	# Vendor 8164
	11011:{'name':'SN-Pseudonym-Username', 'type':AVP_TYPE_STR},	# Vendor 8164
	260:{'name':'SN-IMS-Charging-Identifier', 'type':AVP_TYPE_STR},	# Vendor 8164
	261:{'name':'SN-Originating-IOI', 'type':AVP_TYPE_STR},	# Vendor 8164
	263:{'name':'SN-SDP-Session-Description', 'type':AVP_TYPE_STR},	# Vendor 8164
	264:{'name':'SN-GGSN-Address', 'type':AVP_TYPE_STR},	# Vendor 8164
	265:{'name':'SN-Sec-IP-Pool-Name', 'type':AVP_TYPE_STR},	# Vendor 8164
	266:{'name':'SN-Authorised-Qos', 'type':AVP_TYPE_STR},	# Vendor 8164
	267:{'name':'SN-Cause-Code', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	268:{'name':'SN-Node-Functionality', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	269:{'name':'SN-Is-Unregistered-Subscriber', 'type':AVP_TYPE_STR},	# Vendor 8164
	270:{'name':'SN-Content-Type', 'type':AVP_TYPE_STR},	# Vendor 8164
	271:{'name':'SN-Content-Length', 'type':AVP_TYPE_STR},	# Vendor 8164
	272:{'name':'SN-Content-Disposition', 'type':AVP_TYPE_STR},	# Vendor 8164
	273:{'name':'SN-CSCF-Rf-SDP-Media-Components', 'type':AVP_TYPE_STR},	# Vendor 8164
	274:{'name':'SN-ROHC-Flow-Marking-Mode', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	275:{'name':'SN-CSCF-App-Server-Info', 'type':AVP_TYPE_STR},	# Vendor 8164
	276:{'name':'SN-ISC-Template-Name', 'type':AVP_TYPE_STR},	# Vendor 8164
	277:{'name':'SN-CF-Forward-Unconditional', 'type':AVP_TYPE_STR},	# Vendor 8164
	278:{'name':'SN-CF-Forward-No-Answer', 'type':AVP_TYPE_STR},	# Vendor 8164
	279:{'name':'SN-CF-Forward-Busy-Line', 'type':AVP_TYPE_STR},	# Vendor 8164
	280:{'name':'SN-CF-Forward-Not-Regd', 'type':AVP_TYPE_STR},	# Vendor 8164
	281:{'name':'SN-CF-Follow-Me', 'type':AVP_TYPE_STR},	# Vendor 8164
	282:{'name':'SN-CF-CId-Display', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	283:{'name':'SN-CF-CId-Display-Blocked', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	284:{'name':'SN-CF-Call-Waiting', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	285:{'name':'SN-CF-Call-Transfer', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	287:{'name':'SN-Cscf-Subscriber-Ip-Address', 'type':AVP_TYPE_STR},	# Vendor 8164
	288:{'name':'SN-Software-Version', 'type':AVP_TYPE_STR},	# Vendor 8164
	290:{'name':'SN-Max-Sec-Contexts-Per-Subs', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	291:{'name':'SN-CF-Call-Local', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	292:{'name':'SN-CF-Call-LongDistance', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	293:{'name':'SN-CF-Call-International', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	294:{'name':'SN-CF-Call-Premium', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	295:{'name':'SN-CR-International-Cid', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	296:{'name':'SN-CR-LongDistance-Cid', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	297:{'name':'SN-NAT-IP-Address', 'type':AVP_TYPE_STR},	# Vendor 8164
	298:{'name':'SN-CF-Call-RoamingInternatnl', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	299:{'name':'SN-PDG-TTG-Required', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	300:{'name':'SN-Bandwidth-Policy', 'type':AVP_TYPE_STR},	# Vendor 8164
	301:{'name':'SN-Acs-Credit-Control-Group', 'type':AVP_TYPE_STR},	# Vendor 8164
	302:{'name':'SN-CBB-Policy', 'type':AVP_TYPE_STR},	# Vendor 8164
	303:{'name':'SN-QOS-HLR-Profile', 'type':AVP_TYPE_STR},	# Vendor 8164
	304:{'name':'SN-Fast-Reauth-Username', 'type':AVP_TYPE_STR},	# Vendor 8164
	305:{'name':'SN-Pseudonym-Username', 'type':AVP_TYPE_STR},	# Vendor 8164
	306:{'name':'SN-WiMAX-Auth-Only', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	307:{'name':'SN-TrafficSelector-Class', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	308:{'name':'SN-TPO-Policy', 'type':AVP_TYPE_STR},	# Vendor 8164
	309:{'name':'SN-DHCP-Options', 'type':AVP_TYPE_STR},	# Vendor 8164
	310:{'name':'SN-Handoff-Indicator', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	311:{'name':'SN-MIP-Send-Host-Config', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	313:{'name':'SN-User-Privilege', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	314:{'name':'SN-IPv6-Alloc-Method', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	319:{'name':'SN-WLAN-AP-Identifier', 'type':AVP_TYPE_STR},	# Vendor 8164
	320:{'name':'SN-WLAN-UE-Identifier', 'type':AVP_TYPE_STR},	# Vendor 8164
	131:{'name':'SN-Voice-Push-List-Name', 'type':AVP_TYPE_STR},	# Vendor 8164
	9:{'name':'SN-PPP-Data-Compression', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	61:{'name':'SN-PPP-Outbound-Username', 'type':AVP_TYPE_STR},	# Vendor 8164
	132:{'name':'SN-Unclassify-List-Name', 'type':AVP_TYPE_STR},	# Vendor 8164
	67:{'name':'SN-Subscriber-IP-Hdr-Neg-Mode', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	156:{'name':'SN-Tun-Addr-Policy', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	74:{'name':'SN-Tp-Dnlk-Committed-Data-Rate', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	1472:{'name':'Access-Network-Charging-Physical-Access-Id', 'type':AVP_TYPE_GROUP},	# Vendor 8164
	1473:{'name':'Access-Network-Charging-Physical-Access-Id-Value', 'type':AVP_TYPE_STR},	# Vendor 8164
	1474:{'name':'Access-Network-Charging-Physical-Access-Id-Realm', 'type':AVP_TYPE_STR},	# Vendor 8164
	79:{'name':'SN-QoS-Tp-Uplk', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	16:{'name':'SN-PPP-Keepalive', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	221:{'name':'SN-Subs-VJ-Slotid-Cmp-Neg-Mode', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	501:{'name':'SN-Volume-Quota-Threshold', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	502:{'name':'SN-Unit-Quota-Threshold', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	503:{'name':'SN-Time-Quota-Threshold', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	504:{'name':'SN-Total-Used-Service-Unit', 'type':AVP_TYPE_GROUP},	# Vendor 8164
	505:{'name':'SN-Absolute-Validity-Time', 'type':AVP_TYPE_STR},	# Vendor 8164
	65530:{'name':'SN-Proxy-MIPV6', 'type':AVP_TYPE_UINT32},	# Vendor 8164
	85:{'name':'SN-Subscriber-IP-TOS-Copy', 'type':AVP_TYPE_UINT32}	# Vendor 8164
} ,
# Vendor 12645 Vodafone
12645:{
	256:{'name':'Context-Type', 'type':AVP_TYPE_UINT32},	# Vendor 12645
	257:{'name':'Quota-Consumption-Time', 'type':AVP_TYPE_UINT32},	# Vendor 12645
	258:{'name':'Quota-Holding-Time', 'type':AVP_TYPE_UINT32},	# Vendor 12645
	259:{'name':'Time-Quota-Threshold', 'type':AVP_TYPE_UINT32},	# Vendor 12645
	260:{'name':'Radio-Access-Technology', 'type':AVP_TYPE_UINT32},	# Vendor 12645
	261:{'name':'Reporting-Reason', 'type':AVP_TYPE_UINT32},	# Vendor 12645
	262:{'name':'Rulebase-Id', 'type':AVP_TYPE_STR},	# Vendor 12645
	263:{'name':'Time-Of-First-Usage', 'type':AVP_TYPE_STR},	# Vendor 12645
	264:{'name':'Time-Of-Last-Usage', 'type':AVP_TYPE_STR},	# Vendor 12645
	265:{'name':'Trigger', 'type':AVP_TYPE_GROUP},	# Vendor 12645
	266:{'name':'Trigger-Type', 'type':AVP_TYPE_UINT32},	# Vendor 12645
	267:{'name':'User-Location-Information', 'type':AVP_TYPE_STR},	# Vendor 12645
	268:{'name':'Volume-Quota-Threshold', 'type':AVP_TYPE_UINT32}	# Vendor 12645
} ,
# Vendor 81000 ChinaTelecom
81000:{
	0:{'name':'Dummy', 'type':AVP_TYPE_STR}	# Vendor 81000
} ,
# Vendor 28458 NokiaSiemensNetworks
28458:{
	2016:{'name':'User-Agent-Type', 'type':AVP_TYPE_INT32}	# Vendor 28458
} ,
# Vendor 5771 Cisco
5771:{
	131072:{'name':'Cisco-Charging-Rule-Definition', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131073:{'name':'Content-Definition', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131074:{'name':'Billing-Policy-Definition', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131075:{'name':'Policy-Map-Definition', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131076:{'name':'Service-Definition', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131077:{'name':'Content-Policy-Map', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131078:{'name':'Service-Info', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131079:{'name':'Billing-Plan-Definition', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131080:{'name':'Volume-Threshold', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131081:{'name':'Time-Threshold', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131082:{'name':'Content-Idle-Timer', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131083:{'name':'Nexthop-Uplink', 'type':AVP_TYPE_STR},	# Vendor 5771
	131084:{'name':'Nexthop-Downlink', 'type':AVP_TYPE_STR},	# Vendor 5771
	131085:{'name':'L7-Parse-Protocol-Type', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131086:{'name':'Service-Status', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131087:{'name':'Service-Name', 'type':AVP_TYPE_STR},	# Vendor 5771
	131088:{'name':'Biling-Policy-Name', 'type':AVP_TYPE_STR},	# Vendor 5771
	131089:{'name':'Policy-Map-Name', 'type':AVP_TYPE_STR},	# Vendor 5771
	131090:{'name':'Policy-Map-Match', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131091:{'name':'Match-String', 'type':AVP_TYPE_STR},	# Vendor 5771
	131092:{'name':'Attribute-String', 'type':AVP_TYPE_STR},	# Vendor 5771
	131093:{'name':'Online-Billing-Basis', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131094:{'name':'Service-Activation', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131095:{'name':'CDR-Volume-Threshold', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131096:{'name':'CDR-Time-Threshold', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131097:{'name':'Advice-Of-Charge', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131098:{'name':'Append-URL', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131099:{'name':'Confirm-Token', 'type':AVP_TYPE_STR},	# Vendor 5771
	131100:{'name':'Service-Class', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131101:{'name':'Service-Idle-Time', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131102:{'name':'Owner-Id', 'type':AVP_TYPE_STR},	# Vendor 5771
	131103:{'name':'Owner-Name', 'type':AVP_TYPE_STR},	# Vendor 5771
	131104:{'name':'Online-Passthrough-Quota', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131105:{'name':'Online-Reauthorization-Threshold', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131106:{'name':'Online-Reauthorization-Timeout', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131107:{'name':'Initial-Timeout', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131108:{'name':'Maximum-Timeout', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131109:{'name':'Refund-policy', 'type':AVP_TYPE_STR},	# Vendor 5771
	131110:{'name':'Meter-Exclude', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131111:{'name':'Meter-Include-Imap', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131112:{'name':'Metering-Granularity', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131113:{'name':'Meter-Increment', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131114:{'name':'Meter-Initial', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131115:{'name':'Meter-Minimum', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131116:{'name':'Verify', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131117:{'name':'Confirm-Token', 'type':AVP_TYPE_STR},	# Vendor 5771
	131118:{'name':'Weight', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131119:{'name':'User-Idle-Timer', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131120:{'name':'Policy-Preload-Req-Type', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131121:{'name':'Policy-Preload-Object-Type', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131122:{'name':'Policy-Preload-Status', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131123:{'name':'Charging-Rule-Trigger-Type', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131124:{'name':'Charging-Rule-Event', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131125:{'name':'Service-Reporting-Level', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131126:{'name':'Accounting', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131127:{'name':'Accounting-Customer-String', 'type':AVP_TYPE_STR},	# Vendor 5771
	131128:{'name':'L7-Parse-Length', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131129:{'name':'Service-CDR-Threshold', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131130:{'name':'Intermediate-CDR-Threshold', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131131:{'name':'CDR-Generation-Delay', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131132:{'name':'Replicate-Session', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131133:{'name':'Replicate-Session-Delay', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131134:{'name':'Content-Pending-Timer', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131135:{'name':'Operation-Status', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131136:{'name':'Subscriber-IP-Source', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131137:{'name':'Nexthop', 'type':AVP_TYPE_STR},	# Vendor 5771
	131138:{'name':'Nexthop-Reverse', 'type':AVP_TYPE_STR},	# Vendor 5771
	131139:{'name':'Charging-Rule-Event-Trigger', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131140:{'name':'Billing-Plan-Name', 'type':AVP_TYPE_STR},	# Vendor 5771
	131141:{'name':'Content-Flow-Description', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131142:{'name':'Content-Flow-Filter', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131143:{'name':'Client-Group-Id', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131144:{'name':'ACL-Number', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131145:{'name':'ACL-Name', 'type':AVP_TYPE_STR},	# Vendor 5771
	131146:{'name':'Destination-IP-Address', 'type':AVP_TYPE_STR},	# Vendor 5771
	131147:{'name':'Destination-Mask', 'type':AVP_TYPE_STR},	# Vendor 5771
	131148:{'name':'Protocol-ID', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131149:{'name':'Start-of-Port-Range', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131150:{'name':'End-of-Port-Range', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131151:{'name':'Content-Name', 'type':AVP_TYPE_STR},	# Vendor 5771
	131152:{'name':'Failed-Preload-Object', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131153:{'name':'VRF-Name', 'type':AVP_TYPE_STR},	# Vendor 5771
	131154:{'name':'VLAN-Id', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131155:{'name':'Volume-Usage', 'type':AVP_TYPE_UINT64},	# Vendor 5771
	131156:{'name':'Time-Usage', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131157:{'name':'Duration', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131158:{'name':'First-Packet-Timestanp', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131159:{'name':'Last-Packet-Timestanp', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131160:{'name':'Cisco-Flow-Description', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131161:{'name':'Terminate-Bearer', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131162:{'name':'Service-Rating-Group', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131163:{'name':'Content-Scope', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131164:{'name':'Flow-Status-Policy-Mismatch', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131165:{'name':'Policy-Map-Type', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131166:{'name':'Policy-Map-Match-Install', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131167:{'name':'Policy-Map-Match-Remove', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131168:{'name':'Policy-Map-Replace', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131169:{'name':'Cisco-Flow-Status', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131170:{'name':'Service-QoS', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131171:{'name':'QoS-Rate-Limit-UL', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131172:{'name':'QoS-Rate-Limit-DL', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131173:{'name':'QoS-Rate-Limit', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131174:{'name':'Max-Bandwidth', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131175:{'name':'Rate-Limit-Conform-Action', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131176:{'name':'Rate-Limit-Exceed-Action', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131177:{'name':'Rate-Limit-Action', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131178:{'name':'DSCP', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131179:{'name':'Policy-Map-Install', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131180:{'name':'Policy-Map-Remove', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131181:{'name':'Billing-Policy-Install', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131182:{'name':'Billing-Policy-Remove', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131183:{'name':'Content-Install', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131184:{'name':'Content-Remove', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131185:{'name':'Service-Install', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131186:{'name':'Service-Remove', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131187:{'name':'Billing-Plan-Install', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131188:{'name':'Billing-Plan-Remove', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131189:{'name':'Policy-Preload-Error-Code', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131190:{'name':'Max-Burst-Size', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131191:{'name':'Failed-Preload-Obj-Name', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131192:{'name':'Cisco-Event-Trigger-Type', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131193:{'name':'Cisco-Event-Trigger', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131194:{'name':'TCP-SYN', 'type':AVP_TYPE_STR},	# Vendor 5771
	131195:{'name':'Cisco-Event', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131196:{'name':'Interleaved', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131197:{'name':'Control-URL', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131198:{'name':'Relative-URL', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131199:{'name':'Mining', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131200:{'name':'User-Default', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131201:{'name':'Priority', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131202:{'name':'Domain-Group-Name', 'type':AVP_TYPE_STR},	# Vendor 5771
	131203:{'name':'Domain-Group-Definition', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131204:{'name':'Domain-Group-Install', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131205:{'name':'Domain-Group-Remove', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131206:{'name':'Domain-Group-Activation', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131207:{'name':'Dual-Billing-Basis', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131208:{'name':'Dual-Passthrough-Quota', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131209:{'name':'Dual-Reauthorization-Threshold', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131210:{'name':'Virtual-Online', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131211:{'name':'Nexthop-Media', 'type':AVP_TYPE_STR},	# Vendor 5771
	131212:{'name':'Nexthop-Override', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131213:{'name':'Quota-Consumption-Time', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131214:{'name':'Class-Map-Name', 'type':AVP_TYPE_STR},	# Vendor 5771
	131215:{'name':'Header-Group-Name', 'type':AVP_TYPE_STR},	# Vendor 5771
	131216:{'name':'Header-Group-Definition', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131217:{'name':'Header-Group-Install', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131218:{'name':'Header-Group-Remove', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131219:{'name':'Header-Insert-Name', 'type':AVP_TYPE_STR},	# Vendor 5771
	131220:{'name':'Header-Field-Name', 'type':AVP_TYPE_STR},	# Vendor 5771
	131221:{'name':'Header-Class-Name', 'type':AVP_TYPE_STR},	# Vendor 5771
	131222:{'name':'Header-Class-Mode', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131223:{'name':'Header-Class', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131224:{'name':'Radius-Attribute-Type', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131225:{'name':'Radius-Vsa-Vendor-Id', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131226:{'name':'Radius-Vsa-Subattribute-Type', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131227:{'name':'Header-Item-Radius', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131228:{'name':'Header-Item', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131229:{'name':'Header-Item-String', 'type':AVP_TYPE_STR},	# Vendor 5771
	131230:{'name':'Header-Items-Encrypted', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131231:{'name':'Header-Insert-Definition', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131232:{'name':'Header-Insert-Install', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131233:{'name':'Header-Insert-Remove', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131234:{'name':'User-Idle-Pod', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131235:{'name':'Domain-Group-Clear', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131236:{'name':'Cisco-QoS-Profile-Name', 'type':AVP_TYPE_STR},	# Vendor 5771
	131237:{'name':'Cisco-QoS-Profile', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131238:{'name':'Cisco-QoS-Profile-Install', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131239:{'name':'Cisco-QoS-Profile-Remove', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131240:{'name':'Cisco-QoS-Profile-Uplink', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131241:{'name':'Cisco-QoS-Profile-Downlink', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131242:{'name':'Header-Item-Encryption', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131243:{'name':'Service-Group-Name', 'type':AVP_TYPE_STR},	# Vendor 5771
	131244:{'name':'Service-Group-Definition', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131245:{'name':'Service-Group-Install', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131246:{'name':'Service-Group-Remove', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131247:{'name':'Service-Group-Event', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131248:{'name':'Cisco-Report-Usage', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131249:{'name':'Accel', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131250:{'name':'Cisco-Answer-User-Usage', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131251:{'name':'Cisco-Request-Usage-Type', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131252:{'name':'Cisco-Request-Charging-Rule-Usage', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131253:{'name':'Cisco-Request-Service-Group-Usage', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131254:{'name':'Cisco-Answer-Charging-Rule-Usage', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131255:{'name':'Cisco-Answer-Service-Group-Usage', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131256:{'name':'User-Agent', 'type':AVP_TYPE_STR},	# Vendor 5771
	131257:{'name':'Service-Life-Time', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131258:{'name':'Volume-Threshold-64', 'type':AVP_TYPE_UINT64},	# Vendor 5771
	131259:{'name':'Delegated-IP-Install', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131260:{'name':'Delegated-IPv4-Definition', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131261:{'name':'Delegated-IPv6-Definition', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	131262:{'name':'Aggr-Prefix-Len', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131263:{'name':'Service-Identifier-Lo', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131264:{'name':'Service-Identifier-Hi', 'type':AVP_TYPE_UINT32},	# Vendor 5771
	131265:{'name':'Service-Identifier-Range', 'type':AVP_TYPE_GROUP},	# Vendor 5771
	507:{'name':'Flow-Description', 'type':AVP_TYPE_STR}	# Vendor 5771
} ,
# Vendor 5806 SKT
5806:{
	0:{'name':'Dummy', 'type':AVP_TYPE_UINT32}	# Vendor 5806
} ,
# Vendor 10415 TGPP
10415:{
	2048:{'name':'Supplementary-Service', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2049:{'name':'Participant-Action-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2050:{'name':'PDN-Connection-ID', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	2051:{'name':'Dynamic-Address-Flag', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2052:{'name':'Accumulated-Cost', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2053:{'name':'AoC-Cost-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2054:{'name':'AoC-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2055:{'name':'AoC-Request-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2056:{'name':'Current-Tariff', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2057:{'name':'Next-Tariff', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2058:{'name':'Rate-Element', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2059:{'name':'Scale-Factor', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2060:{'name':'Tariff-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2061:{'name':'Unit-Cost', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2062:{'name':'Incremental-Cost', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2063:{'name':'Local-Sequence-Number', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	2064:{'name':'Node-Id', 'type':AVP_TYPE_STR},	# Vendor 10415
	2065:{'name':'SGW-Change', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2066:{'name':'Charging-Characteristics-Selection-Mode', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2067:{'name':'SGW-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	2068:{'name':'Dynamic-Address-Flag-Extension', 'type':AVP_TYPE_INT32},	# Vendor 10415
	21:{'name':'3GPP-RAT-Type', 'type':AVP_TYPE_STR},	# Vendor 10415
	22:{'name':'3GPP-User-Location-Info', 'type':AVP_TYPE_STR},	# Vendor 10415
	23:{'name':'3GPP-MS-TimeZone', 'type':AVP_TYPE_STR},	# Vendor 10415
	24:{'name':'3GPP-CAMEL-Charging-Info', 'type':AVP_TYPE_STR},	# Vendor 10415
	4:{'name':'3GPP-CG-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	26:{'name':'3GPP-Negotiated-DSCP', 'type':AVP_TYPE_STR},	# Vendor 10415
	27:{'name':'3GPP-Allocate-IP-Type', 'type':AVP_TYPE_STR},	# Vendor 10415
	5:{'name':'3GPP-GPRS-Negotiated-QoS-profile', 'type':AVP_TYPE_STR},	# Vendor 10415
	1:{'name':'3GPP-IMSI', 'type':AVP_TYPE_STR},	# Vendor 10415
	6:{'name':'3GPP-SGSN-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	7:{'name':'3GPP-GGSN-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	8:{'name':'3GPP-IMSI-MCC-MNC', 'type':AVP_TYPE_STR},	# Vendor 10415
	2100:{'name':'Reserved', 'type':AVP_TYPE_STR},	# Vendor 10415
	2101:{'name':'Application-Server-ID', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	2102:{'name':'Application-Service-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2103:{'name':'Application-Session-ID', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	2104:{'name':'Delivery-Status', 'type':AVP_TYPE_STR},	# Vendor 10415
	2105:{'name':'Reserved', 'type':AVP_TYPE_STR},	# Vendor 10415
	2106:{'name':'Reserved', 'type':AVP_TYPE_STR},	# Vendor 10415
	2107:{'name':'Reserved', 'type':AVP_TYPE_STR},	# Vendor 10415
	2108:{'name':'Reserved', 'type':AVP_TYPE_STR},	# Vendor 10415
	2109:{'name':'Reserved', 'type':AVP_TYPE_STR},	# Vendor 10415
	2110:{'name':'IM-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2111:{'name':'Number-Of-Messages-Successfully-Exploded', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	2112:{'name':'Number-Of-Messages-Successfully-Sent', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	2113:{'name':'Total-Number-Of-Messages-Exploded', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	2114:{'name':'Total-Number-Of-Messages-Sent', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	2115:{'name':'DCD-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2116:{'name':'Content-ID', 'type':AVP_TYPE_STR},	# Vendor 10415
	2117:{'name':'Content-provider-ID', 'type':AVP_TYPE_STR},	# Vendor 10415
	2118:{'name':'Charge-Reason-Code', 'type':AVP_TYPE_INT32},	# Vendor 10415
	12:{'name':'3GPP-Selection-Mode', 'type':AVP_TYPE_STR},	# Vendor 10415
	13:{'name':'3GPP-Charging-Characteristics', 'type':AVP_TYPE_STR},	# Vendor 10415
	14:{'name':'3GPP-CG-IPv6-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	15:{'name':'3GPP-SGSN-IPv6-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	3:{'name':'3GPP-PDP-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	16:{'name':'3GPP-GGSN-IPv6-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	17:{'name':'3GPP-IPv6-DNS-Server', 'type':AVP_TYPE_STR},	# Vendor 10415
	18:{'name':'3GPP-SGSN-MCC-MNC', 'type':AVP_TYPE_STR},	# Vendor 10415
	19:{'name':'3GPP-Teardown-Indicator', 'type':AVP_TYPE_STR},	# Vendor 10415
	20:{'name':'3GPP-IMEISV', 'type':AVP_TYPE_STR},	# Vendor 10415
	25:{'name':'3GPP-Packet-Filter', 'type':AVP_TYPE_STR},	# Vendor 10415
	2200:{'name':'Subsession-Decision-Info', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2201:{'name':'Subsession-Enforcement-Info', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2202:{'name':'Subsession-Id', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	2203:{'name':'Subsession-Operation', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2204:{'name':'Multiple-BBERF-Action', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2906:{'name':'Pending-Policy-Counter-Change-Time', 'type':AVP_TYPE_STR},	# Vendor 10415
	3100:{'name':'IP-SM-GW-Number', 'type':AVP_TYPE_STR},	# Vendor 10415
	3101:{'name':'IP-SM-GW-Name', 'type':AVP_TYPE_STR},	# Vendor 10415
	3102:{'name':'User-Identifier', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	3103:{'name':'Service-ID', 'type':AVP_TYPE_INT32},	# Vendor 10415
	3104:{'name':'SCS-Identity', 'type':AVP_TYPE_STR},	# Vendor 10415
	3105:{'name':'Service-Parameters', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	3106:{'name':'T4-Parameters', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	3107:{'name':'Service-Data', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	3108:{'name':'T4-Data', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	3109:{'name':'HSS-Cause', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	3110:{'name':'SIR-Flags', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	3111:{'name':'External-Identifier', 'type':AVP_TYPE_STR},	# Vendor 10415
	2300:{'name':'Reserved', 'type':AVP_TYPE_STR},	# Vendor 10415
	2301:{'name':'SIP-Request-Timestamp-Fraction', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	2302:{'name':'SIP-Response-Timestamp-Fraction', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	2303:{'name':'Online-Charging-Flag', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2304:{'name':'CUG-Information', 'type':AVP_TYPE_STR},	# Vendor 10415
	2305:{'name':'Real-Time-Tariff-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2306:{'name':'Tariff-XML', 'type':AVP_TYPE_STR},	# Vendor 10415
	2307:{'name':'MBMS-GW-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	2308:{'name':'IMSI-Unauthenticated-Flag', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2309:{'name':'Account-Expiration', 'type':AVP_TYPE_STR},	# Vendor 10415
	2310:{'name':'AoC-Format', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2311:{'name':'AoC-Service', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2312:{'name':'AoC-Service-Obligatory-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2313:{'name':'AoC-Service-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2314:{'name':'AoC-Subscription-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2315:{'name':'Preferred-AoC-Currency', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	2317:{'name':'CSG-Access-Mode', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2318:{'name':'CSG-Membership-Indication', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2319:{'name':'User-CSG-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2320:{'name':'Outgoing-Session-Id', 'type':AVP_TYPE_STR},	# Vendor 10415
	2321:{'name':'Initial-IMS-Charging-Identifier', 'type':AVP_TYPE_STR},	# Vendor 10415
	9:{'name':'3GPP-GGSN-MCC-MNC', 'type':AVP_TYPE_STR},	# Vendor 10415
	10:{'name':'3GPP-NSAPI', 'type':AVP_TYPE_STR},	# Vendor 10415
	318:{'name':'3GPP-AAA-Server-Name', 'type':AVP_TYPE_STR},	# Vendor 10415
	319:{'name':'Maximum-Number-Accesses', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	2:{'name':'3GPP-Charging-Id', 'type':AVP_TYPE_STR},	# Vendor 10415
	11:{'name':'3GPP-Session-Stop-Indicator', 'type':AVP_TYPE_STR},	# Vendor 10415
	2400:{'name':'LMSI', 'type':AVP_TYPE_STR},	# Vendor 10415
	2401:{'name':'Serving-Node', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2402:{'name':'MME-Name', 'type':AVP_TYPE_STR},	# Vendor 10415
	2403:{'name':'MSC-Number', 'type':AVP_TYPE_STR},	# Vendor 10415
	2404:{'name':'LCS-Capabilities-Sets', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	2405:{'name':'GMLC-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	2406:{'name':'Additional-Serving-Node', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2407:{'name':'PSR-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	2408:{'name':'MME-Realm', 'type':AVP_TYPE_STR},	# Vendor 10415
	2409:{'name':'SGSN-Name', 'type':AVP_TYPE_STR},	# Vendor 10415
	2410:{'name':'SGSN-Realm', 'type':AVP_TYPE_STR},	# Vendor 10415
	2411:{'name':'RIA-Flags', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	400:{'name':'GBA-UserSecSettings', 'type':AVP_TYPE_STR},	# Vendor 10415
	401:{'name':'Transaction-Identifier', 'type':AVP_TYPE_STR},	# Vendor 10415
	402:{'name':'NAF-Hostname', 'type':AVP_TYPE_STR},	# Vendor 10415
	403:{'name':'GAA-Service-Identifier', 'type':AVP_TYPE_STR},	# Vendor 10415
	404:{'name':'Key-ExpiryTime', 'type':AVP_TYPE_STR},	# Vendor 10415
	405:{'name':'ME-Key-Material', 'type':AVP_TYPE_STR},	# Vendor 10415
	406:{'name':'UICC-Key-Material', 'type':AVP_TYPE_STR},	# Vendor 10415
	407:{'name':'GBA_U-Awareness-Indicator', 'type':AVP_TYPE_INT32},	# Vendor 10415
	408:{'name':'BootstrapInfoCreationTime', 'type':AVP_TYPE_STR},	# Vendor 10415
	409:{'name':'GUSS-Timestamp', 'type':AVP_TYPE_STR},	# Vendor 10415
	410:{'name':'GBA-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	411:{'name':'UE-Id', 'type':AVP_TYPE_STR},	# Vendor 10415
	412:{'name':'UE-Id-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	413:{'name':'UICC-App-Label', 'type':AVP_TYPE_STR},	# Vendor 10415
	414:{'name':'UICC-ME', 'type':AVP_TYPE_INT32},	# Vendor 10415
	415:{'name':'Requested-Key-Lifetime', 'type':AVP_TYPE_STR},	# Vendor 10415
	416:{'name':'Private-Identity-Request', 'type':AVP_TYPE_INT32},	# Vendor 10415
	417:{'name':'GBA-Push-Info', 'type':AVP_TYPE_STR},	# Vendor 10415
	418:{'name':'NAF-SA-Identifier', 'type':AVP_TYPE_STR},	# Vendor 10415
	419:{'name':'Security-Feature-Request', 'type':AVP_TYPE_STR},	# Vendor 10415
	420:{'name':'Security-Feature-Response', 'type':AVP_TYPE_STR},	# Vendor 10415
	2500:{'name':'Location-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2501:{'name':'LCS-EPS-Client-Name', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2502:{'name':'LCS-Requestor-Name', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2503:{'name':'LCS-Priority', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	2504:{'name':'LCS-QoS', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2505:{'name':'Horizontal-Accuracy', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	2506:{'name':'Vertical-Accuracy', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	2508:{'name':'Velocity-Requested', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2509:{'name':'Response-Time', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2510:{'name':'Supported-GAD-Shapes', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	2511:{'name':'LCS-Codeword', 'type':AVP_TYPE_STR},	# Vendor 10415
	2512:{'name':'LCS-Privacy-Check', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2513:{'name':'Accuracy-Fulfilment-Indicator', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2514:{'name':'Age-Of-Location-Estimate', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	2515:{'name':'Velocity-Estimate', 'type':AVP_TYPE_STR},	# Vendor 10415
	2516:{'name':'EUTRAN-Positioning-Data', 'type':AVP_TYPE_STR},	# Vendor 10415
	2517:{'name':'ECGI', 'type':AVP_TYPE_STR},	# Vendor 10415
	2518:{'name':'Location-Event', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2520:{'name':'LCS-Service-Type-ID', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	2521:{'name':'LCS-Privacy-Check-Non-Session', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2522:{'name':'LCS-Privacy-Check-Session', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2523:{'name':'LCS-QoS-Class', 'type':AVP_TYPE_INT32},	# Vendor 10415
	500:{'name':'Abort-Cause', 'type':AVP_TYPE_INT32},	# Vendor 10415
	501:{'name':'Access-Network-Charging-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	502:{'name':'Access-Network-Charging-Identifier', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	503:{'name':'Access-Network-Charging-Identifier-Value', 'type':AVP_TYPE_STR},	# Vendor 10415
	504:{'name':'AF-Application-Identifier', 'type':AVP_TYPE_STR},	# Vendor 10415
	505:{'name':'AF-Charging-Identifier', 'type':AVP_TYPE_STR},	# Vendor 10415
	506:{'name':'Authorization-Token', 'type':AVP_TYPE_STR},	# Vendor 10415
	507:{'name':'Flow-Description', 'type':AVP_TYPE_STR},	# Vendor 10415
	508:{'name':'Flow-Grouping', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	509:{'name':'Flow-Number', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	510:{'name':'Flows', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	511:{'name':'Flow-Status', 'type':AVP_TYPE_INT32},	# Vendor 10415
	512:{'name':'Flow-Usage', 'type':AVP_TYPE_INT32},	# Vendor 10415
	513:{'name':'Specific-Action', 'type':AVP_TYPE_INT32},	# Vendor 10415
	515:{'name':'Max-Requested-Bandwidth-DL', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	516:{'name':'Max-Requested-Bandwidth-UL', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	517:{'name':'Media-Component-Description', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	518:{'name':'Media-Component-Number', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	519:{'name':'Media-Sub-Component', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	520:{'name':'Media-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	521:{'name':'RR-Bandwidth', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	522:{'name':'RS-Bandwidth', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	523:{'name':'SIP-Forking-Indication', 'type':AVP_TYPE_INT32},	# Vendor 10415
	524:{'name':'Codec-Data AVP', 'type':AVP_TYPE_STR},	# Vendor 10415
	525:{'name':'Service-URN', 'type':AVP_TYPE_STR},	# Vendor 10415
	526:{'name':'Acceptable-Service-Info', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	527:{'name':'Service-Info-Status', 'type':AVP_TYPE_INT32},	# Vendor 10415
	528:{'name':'MPS-Identifier', 'type':AVP_TYPE_STR},	# Vendor 10415
	531:{'name':'Sponsor-Identity', 'type':AVP_TYPE_STR},	# Vendor 10415
	532:{'name':'Application-Service-Provider-Identity', 'type':AVP_TYPE_STR},	# Vendor 10415
	533:{'name':'Rx-Request-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	534:{'name':'Min-Requested-Bandwidth-DL', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	535:{'name':'Min-Requested-Bandwidth-UL', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	536:{'name':'Required-Access-Info', 'type':AVP_TYPE_INT32},	# Vendor 10415
	537:{'name':'IP-Domain-Id', 'type':AVP_TYPE_STR},	# Vendor 10415
	2600:{'name':'Reserved', 'type':AVP_TYPE_STR},	# Vendor 10415
	2601:{'name':'IMS-Application-Reference-Identifier', 'type':AVP_TYPE_STR},	# Vendor 10415
	2602:{'name':'Low-Priority-Indicator', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2603:{'name':'IP-Realm-Default-Indicator', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2604:{'name':'Local-GW-Inserted-Indicator', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2605:{'name':'Transcoder-Inserted-Indicator', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2606:{'name':'PDP-Address-Prefix-Length', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	600:{'name':'Visited-Network-Identifier', 'type':AVP_TYPE_STR},	# Vendor 10415
	601:{'name':'Public-Identity', 'type':AVP_TYPE_STR},	# Vendor 10415
	602:{'name':'Server-Name', 'type':AVP_TYPE_STR},	# Vendor 10415
	603:{'name':'Server-Capabilities', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	604:{'name':'Mandatory-Capability', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	605:{'name':'Optional-Capability', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	606:{'name':'User-Data', 'type':AVP_TYPE_STR},	# Vendor 10415
	607:{'name':'SIP-Number-Auth-Items', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	608:{'name':'SIP-Authentication-Scheme', 'type':AVP_TYPE_STR},	# Vendor 10415
	609:{'name':'SIP-Authenticate', 'type':AVP_TYPE_STR},	# Vendor 10415
	610:{'name':'SIP-Authorization', 'type':AVP_TYPE_STR},	# Vendor 10415
	611:{'name':'SIP-Authentication-Context', 'type':AVP_TYPE_STR},	# Vendor 10415
	612:{'name':'SIP-Auth-Data-Item', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	613:{'name':'SIP-Item-Number', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	614:{'name':'Server-Assignment-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	615:{'name':'Deregistration-Reason', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	616:{'name':'Reason-Code', 'type':AVP_TYPE_INT32},	# Vendor 10415
	617:{'name':'Reason-Info', 'type':AVP_TYPE_STR},	# Vendor 10415
	618:{'name':'Charging-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	619:{'name':'Primary-Event-Charging-Function-Name', 'type':AVP_TYPE_STR},	# Vendor 10415
	620:{'name':'Secondary-Event-Charging-Function-Name', 'type':AVP_TYPE_STR},	# Vendor 10415
	621:{'name':'Primary-Charging-Collection-Function-Name', 'type':AVP_TYPE_STR},	# Vendor 10415
	622:{'name':'Secondary-Charging-Collection-Function-Name', 'type':AVP_TYPE_STR},	# Vendor 10415
	623:{'name':'User-Authorization-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	624:{'name':'User-Data-Already-Available', 'type':AVP_TYPE_INT32},	# Vendor 10415
	625:{'name':'Confidentiality-Key', 'type':AVP_TYPE_STR},	# Vendor 10415
	626:{'name':'Integrity-Key', 'type':AVP_TYPE_STR},	# Vendor 10415
	627:{'name':'User-Data-Request-Type(Obsolete)', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	628:{'name':'Supported-Features', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	629:{'name':'Feature-List-ID', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	630:{'name':'Feature-List', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	631:{'name':'Supported-Applications', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	632:{'name':'Associated-Identities', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	633:{'name':'Originating-Request', 'type':AVP_TYPE_INT32},	# Vendor 10415
	634:{'name':'Wildcarded-PSI', 'type':AVP_TYPE_STR},	# Vendor 10415
	635:{'name':'SIP-Digest-Authenticate AVP', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	636:{'name':'Wildcarded-IMPU', 'type':AVP_TYPE_STR},	# Vendor 10415
	637:{'name':'UAR-Flags', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	638:{'name':'Loose-Route-Indication', 'type':AVP_TYPE_INT32},	# Vendor 10415
	639:{'name':'SCSCF-Restoration-Info', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	640:{'name':'Path', 'type':AVP_TYPE_STR},	# Vendor 10415
	641:{'name':'Contact', 'type':AVP_TYPE_STR},	# Vendor 10415
	642:{'name':'Subscription-Info', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	643:{'name':'Call-ID-SIP-Header', 'type':AVP_TYPE_STR},	# Vendor 10415
	644:{'name':'From-SIP-Header', 'type':AVP_TYPE_STR},	# Vendor 10415
	645:{'name':'To-SIP-Header', 'type':AVP_TYPE_STR},	# Vendor 10415
	646:{'name':'Record-Route', 'type':AVP_TYPE_STR},	# Vendor 10415
	647:{'name':'Associated-Registered-Identities', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	648:{'name':'Multiple-Registration-Indication', 'type':AVP_TYPE_INT32},	# Vendor 10415
	649:{'name':'Restoration-Info', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	650:{'name':'Session-Priority', 'type':AVP_TYPE_INT32},	# Vendor 10415
	651:{'name':'Identity-with-Emergency-Registration', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	700:{'name':'User-Identity', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	701:{'name':'MSISDN', 'type':AVP_TYPE_STR},	# Vendor 10415
	702:{'name':'User-Data', 'type':AVP_TYPE_STR},	# Vendor 10415
	703:{'name':'Data-Reference', 'type':AVP_TYPE_INT32},	# Vendor 10415
	704:{'name':'Service-Indication', 'type':AVP_TYPE_STR},	# Vendor 10415
	705:{'name':'Subs-Req-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	706:{'name':'Requested-Domain', 'type':AVP_TYPE_INT32},	# Vendor 10415
	707:{'name':'Current-Location', 'type':AVP_TYPE_INT32},	# Vendor 10415
	708:{'name':'Identity-Set', 'type':AVP_TYPE_INT32},	# Vendor 10415
	709:{'name':'Expiry-Time', 'type':AVP_TYPE_STR},	# Vendor 10415
	710:{'name':'Send-Data-Indication', 'type':AVP_TYPE_INT32},	# Vendor 10415
	711:{'name':'DSAI-Tag', 'type':AVP_TYPE_STR},	# Vendor 10415
	712:{'name':'One-Time-Notification', 'type':AVP_TYPE_INT32},	# Vendor 10415
	713:{'name':'Requested-Nodes', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	714:{'name':'Serving-Node-Indication', 'type':AVP_TYPE_INT32},	# Vendor 10415
	715:{'name':'Repository-Data-ID', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	716:{'name':'Sequence-Number', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	717:{'name':'Pre-paging-Supported', 'type':AVP_TYPE_INT32},	# Vendor 10415
	718:{'name':'Local-Time-Zone-Indication', 'type':AVP_TYPE_INT32},	# Vendor 10415
	719:{'name':'UDR-Flags', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	823:{'name':'Event-Type', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	824:{'name':'SIP-Method', 'type':AVP_TYPE_STR},	# Vendor 10415
	825:{'name':'Event', 'type':AVP_TYPE_STR},	# Vendor 10415
	826:{'name':'Content-Type', 'type':AVP_TYPE_STR},	# Vendor 10415
	827:{'name':'Content-Length', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	828:{'name':'Content-Disposition', 'type':AVP_TYPE_STR},	# Vendor 10415
	829:{'name':'Role-Of-Node', 'type':AVP_TYPE_INT32},	# Vendor 10415
	830:{'name':'User-Session-Id', 'type':AVP_TYPE_STR},	# Vendor 10415
	831:{'name':'Calling-Party-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	832:{'name':'Called-Party-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	833:{'name':'Time-Stamps', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	834:{'name':'SIP-Request-Timestamp', 'type':AVP_TYPE_STR},	# Vendor 10415
	835:{'name':'SIP-Response-Timestamp', 'type':AVP_TYPE_STR},	# Vendor 10415
	836:{'name':'Application-Server', 'type':AVP_TYPE_STR},	# Vendor 10415
	837:{'name':'Application-provided-Called-Party-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	838:{'name':'Inter-Operator-Identifier', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	839:{'name':'Originating-IOI', 'type':AVP_TYPE_STR},	# Vendor 10415
	840:{'name':'Terminating-IOI', 'type':AVP_TYPE_STR},	# Vendor 10415
	841:{'name':'IMS-Charging-Identifier', 'type':AVP_TYPE_STR},	# Vendor 10415
	842:{'name':'SDP-Session-Description', 'type':AVP_TYPE_STR},	# Vendor 10415
	843:{'name':'SDP-Media-components', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	844:{'name':'SDP-Media-Name', 'type':AVP_TYPE_STR},	# Vendor 10415
	845:{'name':'SDP-Media-Description', 'type':AVP_TYPE_STR},	# Vendor 10415
	846:{'name':'CG-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	847:{'name':'GGSN-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	848:{'name':'Served-Party-IP-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	849:{'name':'Authorised-QoS', 'type':AVP_TYPE_STR},	# Vendor 10415
	850:{'name':'Application-Server-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	851:{'name':'Trunk-Group-ID', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	852:{'name':'Incoming-Trunk-Group-ID', 'type':AVP_TYPE_STR},	# Vendor 10415
	853:{'name':'Outgoing-Trunk-Group-ID', 'type':AVP_TYPE_STR},	# Vendor 10415
	854:{'name':'Bearer-Service', 'type':AVP_TYPE_STR},	# Vendor 10415
	855:{'name':'Service-ID', 'type':AVP_TYPE_STR},	# Vendor 10415
	2904:{'name':'SL-Request-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2905:{'name':'Pending-Policy-Counter-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	858:{'name':'PoC-Controlling-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	859:{'name':'PoC-Group-Name', 'type':AVP_TYPE_STR},	# Vendor 10415
	860:{'name':'Cause', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	861:{'name':'Cause-Code', 'type':AVP_TYPE_INT32},	# Vendor 10415
	862:{'name':'Node-Functionality', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	863:{'name':'Service-Specific-Data', 'type':AVP_TYPE_STR},	# Vendor 10415
	864:{'name':'Originator', 'type':AVP_TYPE_INT32},	# Vendor 10415
	865:{'name':'PS-Furnish-Charging-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	866:{'name':'PS-Free-Format-Data', 'type':AVP_TYPE_STR},	# Vendor 10415
	867:{'name':'PS-Append-Free-Format-Data', 'type':AVP_TYPE_INT32},	# Vendor 10415
	868:{'name':'Time-Quota-Threshold', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	869:{'name':'Volume-Quota-Threshold', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	870:{'name':'Trigger-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	871:{'name':'Quota-Holding-Time', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	872:{'name':'Reporting-Reason', 'type':AVP_TYPE_INT32},	# Vendor 10415
	873:{'name':'Service-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	874:{'name':'PS-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	875:{'name':'WLAN-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	876:{'name':'IMS-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	877:{'name':'MMS-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	878:{'name':'LCS-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	879:{'name':'PoC-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	880:{'name':'MBMS-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	881:{'name':'Quota-Consumption-Time', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	882:{'name':'Media-Initiator-Flag', 'type':AVP_TYPE_INT32},	# Vendor 10415
	883:{'name':'PoC-Server-Role', 'type':AVP_TYPE_INT32},	# Vendor 10415
	884:{'name':'PoC-Session-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	885:{'name':'Number-Of-Participants', 'type':AVP_TYPE_INT32},	# Vendor 10415
	886:{'name':'Originator-Address', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	887:{'name':'Participants-Involved', 'type':AVP_TYPE_STR},	# Vendor 10415
	888:{'name':'Expires', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	889:{'name':'Message-Body', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	890:{'name':'WAG-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	891:{'name':'WAG-PLMN-Id', 'type':AVP_TYPE_STR},	# Vendor 10415
	892:{'name':'WLAN-Radio-Container', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	893:{'name':'WLAN-Technology', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	894:{'name':'WLAN-UE-Local-IPAddress', 'type':AVP_TYPE_STR},	# Vendor 10415
	895:{'name':'PDG-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	896:{'name':'PDG-Charging-Id', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	897:{'name':'Address-Data', 'type':AVP_TYPE_STR},	# Vendor 10415
	898:{'name':'Address-Domain', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	899:{'name':'Address-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	900:{'name':'TMGI', 'type':AVP_TYPE_STR},	# Vendor 10415
	901:{'name':'Required-MBMS-Bearer-Capabilities', 'type':AVP_TYPE_STR},	# Vendor 10415
	902:{'name':'MBMS-StartStop-Indication', 'type':AVP_TYPE_INT32},	# Vendor 10415
	903:{'name':'MBMS-Service-Area', 'type':AVP_TYPE_STR},	# Vendor 10415
	904:{'name':'MBMS-Session-Duration', 'type':AVP_TYPE_STR},	# Vendor 10415
	905:{'name':'Alternative-APN', 'type':AVP_TYPE_STR},	# Vendor 10415
	906:{'name':'MBMS-Service-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	907:{'name':'MBMS-2G-3G-Indicator', 'type':AVP_TYPE_INT32},	# Vendor 10415
	908:{'name':'MBMS-Session-Identity', 'type':AVP_TYPE_STR},	# Vendor 10415
	909:{'name':'RAI', 'type':AVP_TYPE_STR},	# Vendor 10415
	910:{'name':'Additional-MBMS-Trace-Info', 'type':AVP_TYPE_STR},	# Vendor 10415
	911:{'name':'MBMS-Time-To-Data-Transfer', 'type':AVP_TYPE_STR},	# Vendor 10415
	912:{'name':'MBMS-Session-Repetition-Number', 'type':AVP_TYPE_STR},	# Vendor 10415
	913:{'name':'MBMS-Required-QoS', 'type':AVP_TYPE_STR},	# Vendor 10415
	914:{'name':'MBMS-Counting-Information', 'type':AVP_TYPE_INT32},	# Vendor 10415
	915:{'name':'MBMS-User-Data-Mode-Indication', 'type':AVP_TYPE_INT32},	# Vendor 10415
	916:{'name':'MBMS-GGSN-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	917:{'name':'MBMS-GGSN-IPv6-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	918:{'name':'MBMS-BMSC-SSM-IP-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	919:{'name':'MBMS-BMSC-SSM-IPv6-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	920:{'name':'MBMS-Flow-Identifier', 'type':AVP_TYPE_STR},	# Vendor 10415
	921:{'name':'CN-IP-Multicast-Distribution', 'type':AVP_TYPE_INT32},	# Vendor 10415
	922:{'name':'MBMS-HC-Indicator', 'type':AVP_TYPE_INT32},	# Vendor 10415
	923:{'name':'MBMS-Access-Indicator', 'type':AVP_TYPE_INT32},	# Vendor 10415
	924:{'name':'MBMS-GW-SSM-IP-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	925:{'name':'MBMS-GW-SSM-IPv6-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	926:{'name':'MBMS-BMSC-SSM-UDP-Port', 'type':AVP_TYPE_STR},	# Vendor 10415
	927:{'name':'MBMS-GW-UDP-Port', 'type':AVP_TYPE_STR},	# Vendor 10415
	928:{'name':'MBMS-GW-UDP-Port-Indicator', 'type':AVP_TYPE_INT32},	# Vendor 10415
	929:{'name':'MBMS-Data-Transfer-Start', 'type':AVP_TYPE_UINT64},	# Vendor 10415
	930:{'name':'MBMS-Data-Transfer-Stop', 'type':AVP_TYPE_UINT64},	# Vendor 10415
	3001:{'name':'Device-Action', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	3002:{'name':'Device-Notification', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	3003:{'name':'Trigger-Data', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	3004:{'name':'Payload', 'type':AVP_TYPE_STR},	# Vendor 10415
	3005:{'name':'Action-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	3006:{'name':'Priority-Indication', 'type':AVP_TYPE_INT32},	# Vendor 10415
	3007:{'name':'Reference-Number', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	3008:{'name':'Request-Status', 'type':AVP_TYPE_INT32},	# Vendor 10415
	3009:{'name':'Delivery-Outcome', 'type':AVP_TYPE_INT32},	# Vendor 10415
	3010:{'name':'Application-Port-Identifier', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1000:{'name':'Bearer-Usage', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1001:{'name':'Charging-Rule-Install', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1002:{'name':'Charging-Rule-Remove', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1003:{'name':'Charging-Rule-Definition', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1004:{'name':'Charging-Rule-Base-Name', 'type':AVP_TYPE_STR},	# Vendor 10415
	1005:{'name':'Charging-Rule-Name', 'type':AVP_TYPE_STR},	# Vendor 10415
	1006:{'name':'Event-Trigger', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1007:{'name':'Metering-Method', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1008:{'name':'Offline', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1009:{'name':'Online', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1010:{'name':'Precedence', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1011:{'name':'Reporting-Level', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1012:{'name':'TFT-Filter', 'type':AVP_TYPE_STR},	# Vendor 10415
	1013:{'name':'TFT-Packet-Filter-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1014:{'name':'ToS-Traffic-Class', 'type':AVP_TYPE_STR},	# Vendor 10415
	1015:{'name':'PDP-Session-operation', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1016:{'name':'QoS-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1018:{'name':'Charging-Rule-Report', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1019:{'name':'PCC-Rule-Status', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1020:{'name':'Bearer-Identifier', 'type':AVP_TYPE_STR},	# Vendor 10415
	1021:{'name':'Bearer-Operation', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1022:{'name':'Access-Network-Charging-Identifier-Gx', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1023:{'name':'Bearer-Control-Mode', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1024:{'name':'Network-Request-Support', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1025:{'name':'Guaranteed-Bitrate-DL', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1026:{'name':'Guaranteed-Bitrate-UL', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1027:{'name':'IP-CAN-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1028:{'name':'QoS-Class-Identifier', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1029:{'name':'QoS-Negotiation', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1030:{'name':'QoS-Upgrade', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1031:{'name':'Rule-Failure-Code', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1032:{'name':'RAT-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1033:{'name':'Event-Report-Indication', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1034:{'name':'Allocation-Retention-Priority', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1035:{'name':'CoA-IP-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	1036:{'name':'Tunnel-Header-Filter', 'type':AVP_TYPE_STR},	# Vendor 10415
	1037:{'name':'Tunnel-Header-Length', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1038:{'name':'Tunnel-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1039:{'name':'CoA-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1040:{'name':'APN-Aggregate-Max-Bitrate-DL', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1041:{'name':'APN-Aggregate-Max-Bitrate-UL', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1042:{'name':'Revalidation-Time', 'type':AVP_TYPE_STR},	# Vendor 10415
	1043:{'name':'Rule-Activation-Time', 'type':AVP_TYPE_STR},	# Vendor 10415
	1044:{'name':'Rule-DeActivation-Time', 'type':AVP_TYPE_STR},	# Vendor 10415
	1045:{'name':'Session-Release-Cause', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1046:{'name':'Priority-Level', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1047:{'name':'Pre-emption-Capability', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1048:{'name':'Pre-emption-Vulnerability', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1049:{'name':'Default-EPS-Bearer-QoS', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1050:{'name':'AN-GW-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	1051:{'name':'QoS-Rule-Install', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1052:{'name':'QoS-Rule-Remove', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1053:{'name':'QoS-Rule-Definition', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1054:{'name':'QoS-Rule-Name', 'type':AVP_TYPE_STR},	# Vendor 10415
	1055:{'name':'QoS-Rule-Report', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1056:{'name':'Security-Parameter-Index', 'type':AVP_TYPE_STR},	# Vendor 10415
	1057:{'name':'Flow-Label', 'type':AVP_TYPE_STR},	# Vendor 10415
	1058:{'name':'Flow-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1059:{'name':'Packet-Filter-Content', 'type':AVP_TYPE_STR},	# Vendor 10415
	1060:{'name':'Packet-Filter-Identifier', 'type':AVP_TYPE_STR},	# Vendor 10415
	1061:{'name':'Packet-Filter-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1062:{'name':'Packet-Filter-Operation', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1063:{'name':'Resource-Allocation-Notification', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1064:{'name':'Session-Linking-Indicator', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1065:{'name':'PDN-Connection-ID', 'type':AVP_TYPE_STR},	# Vendor 10415
	1066:{'name':'Monitoring-Key', 'type':AVP_TYPE_STR},	# Vendor 10415
	1067:{'name':'Usage-Monitoring-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1068:{'name':'Usage-Monitoring-Level', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1069:{'name':'Usage-Monitoring-Report', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1070:{'name':'Usage-Monitoring-Support', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1071:{'name':'CSG-Information-Reporting', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1072:{'name':'Packet-Filter-Usage', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1073:{'name':'Charging-Correlation-Indicator', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1074:{'name':'QoS-Rule-Base-Name', 'type':AVP_TYPE_STR},	# Vendor 10415
	1075:{'name':'Routing-Rule-Remove', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1076:{'name':'Routing-Rule-Definition', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1077:{'name':'Routing-Rule-Identifier', 'type':AVP_TYPE_STR},	# Vendor 10415
	1078:{'name':'Routing-Filter', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1079:{'name':'Routing-IP-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	1080:{'name':'Flow-Direction', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1081:{'name':'Routing-Rule-Install', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1082:{'name':'Maximum-Bandwidth', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1083:{'name':'Max-Supported-Bandwidth-DL', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1084:{'name':'Max-Supported-Bandwidth-UL', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1100:{'name':'Served-User-Identity', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1101:{'name':'VASP-ID', 'type':AVP_TYPE_STR},	# Vendor 10415
	1102:{'name':'VAS-ID', 'type':AVP_TYPE_STR},	# Vendor 10415
	1103:{'name':'Trigger-Event', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1104:{'name':'Sender-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	1105:{'name':'Initial-Recipient-Address', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1106:{'name':'Result-Recipient-Address', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1107:{'name':'Sequence-Number', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1108:{'name':'Recipient-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	1109:{'name':'Routeing-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	1110:{'name':'Originating-Interface', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1111:{'name':'Delivery-Report', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1112:{'name':'Read-Reply', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1113:{'name':'Sender-Visibility', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1114:{'name':'Service-Key', 'type':AVP_TYPE_STR},	# Vendor 10415
	1115:{'name':'Billing-Information', 'type':AVP_TYPE_STR},	# Vendor 10415
	1116:{'name':'Status', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1117:{'name':'Status-Code', 'type':AVP_TYPE_STR},	# Vendor 10415
	1118:{'name':'Status-Text', 'type':AVP_TYPE_STR},	# Vendor 10415
	1119:{'name':'Routeing-Address-Resolution', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2902:{'name':'Policy-Counter-Status', 'type':AVP_TYPE_STR},	# Vendor 10415
	2901:{'name':'Policy-Counter-Identifier', 'type':AVP_TYPE_STR},	# Vendor 10415
	3200:{'name':'SM-Delivery-Outcome-T4', 'type':AVP_TYPE_INT32},	# Vendor 10415
	3201:{'name':'Absent-Subscriber-Diagnostic-T4', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2903:{'name':'Policy-Counter-Status-Report', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1200:{'name':'Domain-Name', 'type':AVP_TYPE_STR},	# Vendor 10415
	1201:{'name':'Recipient-Address', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1202:{'name':'Submission-Time', 'type':AVP_TYPE_STR},	# Vendor 10415
	1203:{'name':'MM-Content-Type', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1204:{'name':'Type-Number', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1205:{'name':'Additional-Type-Information', 'type':AVP_TYPE_STR},	# Vendor 10415
	1206:{'name':'Content-Size', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1207:{'name':'Additional-Content-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1208:{'name':'Addressee-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1209:{'name':'Priority', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1210:{'name':'Message-ID', 'type':AVP_TYPE_STR},	# Vendor 10415
	1211:{'name':'Message-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1212:{'name':'Message-Size', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1213:{'name':'Message-Class', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1214:{'name':'Class-Identifier', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1215:{'name':'Token-Text', 'type':AVP_TYPE_STR},	# Vendor 10415
	1216:{'name':'Delivery-Report-Requested', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1217:{'name':'Adaptations', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1218:{'name':'Applic-ID', 'type':AVP_TYPE_STR},	# Vendor 10415
	1219:{'name':'Aux-Applic-Info', 'type':AVP_TYPE_STR},	# Vendor 10415
	1220:{'name':'Content-Class', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1221:{'name':'DRM-Content', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1222:{'name':'Read-Reply-Report-Requested', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1223:{'name':'Reply-Applic-ID', 'type':AVP_TYPE_STR},	# Vendor 10415
	1224:{'name':'File-Repair-Supported', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1225:{'name':'MBMS-User-Service-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1226:{'name':'Unit-Quota-Threshold', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1227:{'name':'PDP-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	1228:{'name':'SGSN-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	1229:{'name':'PoC-Session-Id', 'type':AVP_TYPE_STR},	# Vendor 10415
	1230:{'name':'Deferred-Location-Event-Type', 'type':AVP_TYPE_STR},	# Vendor 10415
	1231:{'name':'LCS-APN', 'type':AVP_TYPE_STR},	# Vendor 10415
	1232:{'name':'LCS-Client-ID', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1233:{'name':'LCS-Client-Dialed-By-MS', 'type':AVP_TYPE_STR},	# Vendor 10415
	1234:{'name':'LCS-Client-External-ID', 'type':AVP_TYPE_STR},	# Vendor 10415
	1235:{'name':'LCS-Client-Name', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1236:{'name':'LCS-Data-Coding-Scheme', 'type':AVP_TYPE_STR},	# Vendor 10415
	1237:{'name':'LCS-Format-Indicator', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1238:{'name':'LCS-Name-String', 'type':AVP_TYPE_STR},	# Vendor 10415
	1239:{'name':'LCS-Requestor-ID', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1240:{'name':'LCS-Requestor-ID-String', 'type':AVP_TYPE_STR},	# Vendor 10415
	1241:{'name':'LCS-Client-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1242:{'name':'Location-Estimate', 'type':AVP_TYPE_STR},	# Vendor 10415
	1243:{'name':'Location-Estimate-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1244:{'name':'Location-Type', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1245:{'name':'Positioning-Data', 'type':AVP_TYPE_STR},	# Vendor 10415
	1246:{'name':'WLAN-Session-Id', 'type':AVP_TYPE_STR},	# Vendor 10415
	1247:{'name':'PDP-Context-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1248:{'name':'MMBox-Storage-Requested', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1249:{'name':'Service-Specific-Info', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1250:{'name':'Called-Asserted-Identity', 'type':AVP_TYPE_STR},	# Vendor 10415
	1251:{'name':'Requested-Party-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	1252:{'name':'PoC-User-Role', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1253:{'name':'PoC-User-Role-IDs', 'type':AVP_TYPE_STR},	# Vendor 10415
	1254:{'name':'PoC-User-Role-info-Units', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1255:{'name':'Talk-Burst-Exchange', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1256:{'name':'Service-Generic-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1257:{'name':'Service-Specific-Type', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1258:{'name':'Event-Charging-TimeStamp', 'type':AVP_TYPE_STR},	# Vendor 10415
	1259:{'name':'Participant-Access-Priority', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1260:{'name':'Participant-Group', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1261:{'name':'PoC-Change-Condition', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1262:{'name':'PoC-Change-Time', 'type':AVP_TYPE_STR},	# Vendor 10415
	1263:{'name':'Access-Network-Information', 'type':AVP_TYPE_STR},	# Vendor 10415
	1264:{'name':'Trigger', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1265:{'name':'Base-Time-Interval', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1266:{'name':'Envelope', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1267:{'name':'Envelope-End-Time', 'type':AVP_TYPE_STR},	# Vendor 10415
	1268:{'name':'Envelope-Reporting', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1269:{'name':'Envelope-Start-Time', 'type':AVP_TYPE_STR},	# Vendor 10415
	1270:{'name':'Time-Quota-Mechanism', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1271:{'name':'Time-Quota-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1272:{'name':'Early-Media-Description', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1273:{'name':'SDP-TimeStamps', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1274:{'name':'SDP-Offer-Timestamp', 'type':AVP_TYPE_STR},	# Vendor 10415
	1275:{'name':'SDP-Answer-Timestamp', 'type':AVP_TYPE_STR},	# Vendor 10415
	1276:{'name':'AF-Correlation-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1277:{'name':'PoC-Session-Initiation-type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1278:{'name':'Offline-Charging', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1279:{'name':'User-Participating-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1280:{'name':'Alternate-Charged-Party-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	1281:{'name':'IMS-Communication-Service-Identifier', 'type':AVP_TYPE_STR},	# Vendor 10415
	1282:{'name':'Number-Of-Received-Talk-Bursts', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1283:{'name':'Number-Of-Talk-Bursts', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1284:{'name':'Received-Talk-Burst-Time', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1285:{'name':'Received-Talk-Burst-Volume', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1286:{'name':'Talk-Burst-Time', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1287:{'name':'Talk-Burst-Volume', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1288:{'name':'Media-Initiator-Party', 'type':AVP_TYPE_STR},	# Vendor 10415
	1400:{'name':'Subscription-Data', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1401:{'name':'Terminal-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1402:{'name':'IMEI', 'type':AVP_TYPE_STR},	# Vendor 10415
	1403:{'name':'Software-Version', 'type':AVP_TYPE_STR},	# Vendor 10415
	1404:{'name':'QoS-Subscribed', 'type':AVP_TYPE_STR},	# Vendor 10415
	1405:{'name':'ULR-Flags', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1406:{'name':'ULA-Flags', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1407:{'name':'Visited-PLMN-Id', 'type':AVP_TYPE_STR},	# Vendor 10415
	1408:{'name':'Requested-EUTRAN-Authentication-Info', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1409:{'name':'Requested-UTRAN-GERAN-Authentication-Info', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1410:{'name':'Number-Of-Requested-Vectors', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1411:{'name':'Re-Synchronization-Info', 'type':AVP_TYPE_STR},	# Vendor 10415
	1412:{'name':'Immediate-Response-Preferred', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1413:{'name':'Authentication-Info', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1414:{'name':'E-UTRAN-Vector', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1415:{'name':'UTRAN-Vector', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1416:{'name':'GERAN-Vector', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1417:{'name':'Network-Access-Mode', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1418:{'name':'HPLMN-ODB', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1419:{'name':'Item-Number', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1420:{'name':'Cancellation-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1421:{'name':'DSR-Flags', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1422:{'name':'DSA-Flags', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1423:{'name':'Context-Identifier', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1424:{'name':'Subscriber-Status', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1425:{'name':'Operator-Determined-Barring', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1426:{'name':'Access-Restriction-Data', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1427:{'name':'APN-OI-Replacement', 'type':AVP_TYPE_STR},	# Vendor 10415
	1428:{'name':'All-APN-Configurations-Included-Indicator', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1429:{'name':'APN-Configuration-Profile', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1430:{'name':'APN-Configuration', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1431:{'name':'EPS-Subscribed-QoS-Profile', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1432:{'name':'VPLMN-Dynamic-Address-Allowed', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1433:{'name':'STN-SR', 'type':AVP_TYPE_STR},	# Vendor 10415
	1434:{'name':'Alert-Reason', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1435:{'name':'AMBR', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1436:{'name':'CSG-Subscription-Data', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1437:{'name':'CSG-Id', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1438:{'name':'PDN-GW-Allocation-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1439:{'name':'Expiration-Date', 'type':AVP_TYPE_STR},	# Vendor 10415
	1440:{'name':'RAT-Frequency-Selection-Priority-ID', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1441:{'name':'IDA-Flags', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1442:{'name':'PUA-Flags', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1443:{'name':'NOR-Flags', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1444:{'name':'User-Id', 'type':AVP_TYPE_STR},	# Vendor 10415
	1445:{'name':'Equipment-Status', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1446:{'name':'Regional-Subscription-Zone-Code', 'type':AVP_TYPE_STR},	# Vendor 10415
	1447:{'name':'RAND', 'type':AVP_TYPE_STR},	# Vendor 10415
	1448:{'name':'XRES', 'type':AVP_TYPE_STR},	# Vendor 10415
	1449:{'name':'AUTN', 'type':AVP_TYPE_STR},	# Vendor 10415
	1450:{'name':'KASME', 'type':AVP_TYPE_STR},	# Vendor 10415
	1452:{'name':'Trace-Collection-Entity', 'type':AVP_TYPE_STR},	# Vendor 10415
	1453:{'name':'Kc', 'type':AVP_TYPE_STR},	# Vendor 10415
	1454:{'name':'SRES', 'type':AVP_TYPE_STR},	# Vendor 10415
	1455:{'name':'Requesting-Node-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1456:{'name':'PDN-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1457:{'name':'Roaming-Restricted-Due-To-Unsupported-Feature', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1458:{'name':'Trace-Data', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1459:{'name':'Trace-Reference', 'type':AVP_TYPE_STR},	# Vendor 10415
	1462:{'name':'Trace-Depth', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1463:{'name':'Trace-NE-Type-List', 'type':AVP_TYPE_STR},	# Vendor 10415
	1464:{'name':'Trace-Interface-List', 'type':AVP_TYPE_STR},	# Vendor 10415
	1465:{'name':'Trace-Event-List', 'type':AVP_TYPE_STR},	# Vendor 10415
	1466:{'name':'OMC-Id', 'type':AVP_TYPE_STR},	# Vendor 10415
	1467:{'name':'GPRS-Subscription-Data', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1468:{'name':'Complete-Data-List-Included-Indicator', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1469:{'name':'PDP-Context', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1470:{'name':'PDP-Type', 'type':AVP_TYPE_STR},	# Vendor 10415
	1471:{'name':'TGPP2-MEID', 'type':AVP_TYPE_STR},	# Vendor 10415
	1472:{'name':'Specific-APN-Info', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1473:{'name':'LCS-Info', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1474:{'name':'GMLC-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	1475:{'name':'LCS-PrivacyException', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1476:{'name':'SS-Code', 'type':AVP_TYPE_STR},	# Vendor 10415
	1477:{'name':'SS-Status', 'type':AVP_TYPE_STR},	# Vendor 10415
	1478:{'name':'Notification-To-UE-User', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1479:{'name':'External-Client', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1480:{'name':'Client-Identity', 'type':AVP_TYPE_STR},	# Vendor 10415
	1481:{'name':'GMLC-Restriction', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1482:{'name':'PLMN-Client', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1483:{'name':'Service-Type', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1484:{'name':'ServiceTypeIdentity', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1485:{'name':'MO-LR', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1486:{'name':'Teleservice-List', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1487:{'name':'TS-Code', 'type':AVP_TYPE_STR},	# Vendor 10415
	1488:{'name':'Call-Barring-Infor-List', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1489:{'name':'SGSN-Number', 'type':AVP_TYPE_STR},	# Vendor 10415
	1490:{'name':'IDR-Flags', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1491:{'name':'ICS-Indicator', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1492:{'name':'IMS-Voice-Over-PS-Sessions-Supported', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1493:{'name':'Homogeneous-Support-of-IMS-Voice-Over-PS-Sessions', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1494:{'name':'Last-UE-Activity-Time', 'type':AVP_TYPE_STR},	# Vendor 10415
	1495:{'name':'EPS-User-State', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1496:{'name':'EPS-Location-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1497:{'name':'MME-User-State', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1498:{'name':'SGSN-User-State', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1499:{'name':'User-State', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1500:{'name':'Non-3GPP-User-Data', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1501:{'name':'Non-3GPP-IP-Access', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1502:{'name':'Non-3GPP-IP-Access-APN', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1503:{'name':'AN-Trusted', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1504:{'name':'ANID', 'type':AVP_TYPE_STR},	# Vendor 10415
	1505:{'name':'Trace-Info', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1506:{'name':'MIP-FA-RK', 'type':AVP_TYPE_STR},	# Vendor 10415
	1507:{'name':'MIP-FA-RK-SPI', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1600:{'name':'MME-Location-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1601:{'name':'SGSN-Location-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1602:{'name':'E-UTRAN-Cell-Global-Identity', 'type':AVP_TYPE_STR},	# Vendor 10415
	1603:{'name':'Tracking-Area-Identity', 'type':AVP_TYPE_STR},	# Vendor 10415
	1604:{'name':'Cell-Global-Identity', 'type':AVP_TYPE_STR},	# Vendor 10415
	1605:{'name':'Routing-Area-Identity', 'type':AVP_TYPE_STR},	# Vendor 10415
	1606:{'name':'Location-Area-Identity', 'type':AVP_TYPE_STR},	# Vendor 10415
	1607:{'name':'Service-Area-Identity', 'type':AVP_TYPE_STR},	# Vendor 10415
	1608:{'name':'Geographical-Information', 'type':AVP_TYPE_STR},	# Vendor 10415
	1609:{'name':'Geodetic-Information', 'type':AVP_TYPE_STR},	# Vendor 10415
	1610:{'name':'Current-Location-Retrieved', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1611:{'name':'Age-Of-Location-Information', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1612:{'name':'Active-APN', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1613:{'name':'SIPTO-Permission', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1614:{'name':'Error-Diagnostic', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1615:{'name':'UE-SRVCC-Capability', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1616:{'name':'MPS-Priority', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1617:{'name':'VPLMN-LIPA-Allowed', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1618:{'name':'LIPA-Permission', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1619:{'name':'Subscribed-Periodic-RAU-TAU-Timer', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1620:{'name':'Ext-PDP-Type', 'type':AVP_TYPE_STR},	# Vendor 10415
	1621:{'name':'Ext-PDP-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	1622:{'name':'MDT-Configuration', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1623:{'name':'Job-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1624:{'name':'Area-Scope', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1625:{'name':'List-Of-Measurements', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1626:{'name':'Reporting-Trigger', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1627:{'name':'Report-Interval', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1628:{'name':'Report-Amount', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1629:{'name':'Event-Threshold-RSRP', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1630:{'name':'Event-Threshold-RSRQ', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1631:{'name':'Logging-Interval', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1632:{'name':'Logging-Duration', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1633:{'name':'Relay-Node-Indicator', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1634:{'name':'MDT-User-Consent', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1635:{'name':'PUR-Flags', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1636:{'name':'Subscribed-VSRVCC', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1637:{'name':'Equivalent-PLMN-List', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1638:{'name':'CLR-Flags', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1639:{'name':'UVR-Flags', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1640:{'name':'UVA-Flags', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1641:{'name':'VPLMN-CSG-Subscription-Data', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	1642:{'name':'Time-Zone', 'type':AVP_TYPE_STR},	# Vendor 10415
	1643:{'name':'A-MSISDN', 'type':AVP_TYPE_STR},	# Vendor 10415
	1645:{'name':'MME-Number-for-MT-SMS', 'type':AVP_TYPE_STR},	# Vendor 10415
	1648:{'name':'SMS-Register-Request', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1650:{'name':'Daylight-Saving-Time', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1654:{'name':'Subscription-Data-Flags', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	1655:{'name':'Measurement-Period-UMTS', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1656:{'name':'Measurement-Period-LTE', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1657:{'name':'Collection-Period-RRM-LTE', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1658:{'name':'Collection-Period-RRM-UMTS', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1659:{'name':'Positioning-Method', 'type':AVP_TYPE_STR},	# Vendor 10415
	1660:{'name':'Measurement-Quantity', 'type':AVP_TYPE_STR},	# Vendor 10415
	1661:{'name':'Event-Threshold-Event-1F', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1662:{'name':'Event-Threshold-Event-1I', 'type':AVP_TYPE_INT32},	# Vendor 10415
	1663:{'name':'Restoration-Priority', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	2000:{'name':'SMS-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2001:{'name':'Data-Coding-Scheme', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2002:{'name':'Destination-Interface', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2003:{'name':'Interface-Id', 'type':AVP_TYPE_STR},	# Vendor 10415
	2004:{'name':'Interface-Port', 'type':AVP_TYPE_STR},	# Vendor 10415
	2005:{'name':'Interface-Text', 'type':AVP_TYPE_STR},	# Vendor 10415
	2006:{'name':'Interface-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2007:{'name':'SM-Message-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2008:{'name':'Originating-SCCP-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	2009:{'name':'Originator-Interface', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2010:{'name':'Recipient-SCCP-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	2011:{'name':'Reply-Path-Requested', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2012:{'name':'SM-Discharge-Time', 'type':AVP_TYPE_STR},	# Vendor 10415
	2013:{'name':'SM-Protocol-ID', 'type':AVP_TYPE_STR},	# Vendor 10415
	2014:{'name':'SM-Status', 'type':AVP_TYPE_STR},	# Vendor 10415
	2015:{'name':'SM-User-Data-Header', 'type':AVP_TYPE_STR},	# Vendor 10415
	2016:{'name':'SMS-Node', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2017:{'name':'SMSC-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	2018:{'name':'Client-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	2019:{'name':'Number-of-Messages-Sent', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	2020:{'name':'Low-Balance-Indication', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2021:{'name':'Remaining-Balance', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2022:{'name':'Refund-Information', 'type':AVP_TYPE_STR},	# Vendor 10415
	2023:{'name':'Carrier-Select-Routing-Information', 'type':AVP_TYPE_STR},	# Vendor 10415
	2024:{'name':'Number-Portability-Routing-Information', 'type':AVP_TYPE_STR},	# Vendor 10415
	2025:{'name':'PoC-Event-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2026:{'name':'Recipients', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2027:{'name':'Destination-Interface', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2028:{'name':'Recipient-Received-Address', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2029:{'name':'SM-Service-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2030:{'name':'MMTel-Information', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2031:{'name':'Service-type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2032:{'name':'Service-Mode', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2033:{'name':'Subscriber-Role', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2034:{'name':'Number-Of-Diversions', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	2035:{'name':'Associated-Party-Address', 'type':AVP_TYPE_STR},	# Vendor 10415
	2036:{'name':'SDP-Type', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2037:{'name':'Change-Condition', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2038:{'name':'Change-Time', 'type':AVP_TYPE_STR},	# Vendor 10415
	2039:{'name':'Diagnostics', 'type':AVP_TYPE_INT32},	# Vendor 10415
	2040:{'name':'Service-Data-Container', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2041:{'name':'Start-Time', 'type':AVP_TYPE_STR},	# Vendor 10415
	2042:{'name':'Stop-Time', 'type':AVP_TYPE_STR},	# Vendor 10415
	2043:{'name':'Time-First-Usage', 'type':AVP_TYPE_STR},	# Vendor 10415
	2044:{'name':'Time-Last-Usage', 'type':AVP_TYPE_STR},	# Vendor 10415
	2045:{'name':'Time-Usage', 'type':AVP_TYPE_UINT32},	# Vendor 10415
	2046:{'name':'Traffic-Data-Volumes', 'type':AVP_TYPE_GROUP},	# Vendor 10415
	2047:{'name':'Serving-Node-Type', 'type':AVP_TYPE_INT32}	# Vendor 10415
} ,
# Vendor 42 Sun
42:{
	1:{'name':'Ping-Timestamp-Secs', 'type':AVP_TYPE_UINT32},	# Vendor 42
	2:{'name':'Ping-Timestamp-Usecs', 'type':AVP_TYPE_UINT32},	# Vendor 42
	3:{'name':'Ping-Timestamp', 'type':AVP_TYPE_GROUP}	# Vendor 42
} ,
# Vendor 12951 VerizonWireless
12951:{
	0:{'name':'Dummy', 'type':AVP_TYPE_STR}	# Vendor 12951
} ,
# Vendor 13019 ETSI
13019:{
	512:{'name':'ETSI-Digest-Auth-Param', 'type':AVP_TYPE_STR},	# Vendor 13019
	513:{'name':'ETSI-Digest-Username', 'type':AVP_TYPE_STR},	# Vendor 13019
	514:{'name':'ETSI-Digest-URI', 'type':AVP_TYPE_STR},	# Vendor 13019
	515:{'name':'ETSI-Digest-Response', 'type':AVP_TYPE_STR},	# Vendor 13019
	516:{'name':'ETSI-Digest-CNonce', 'type':AVP_TYPE_STR},	# Vendor 13019
	517:{'name':'ETSI-Digest-Nonce-Count', 'type':AVP_TYPE_STR},	# Vendor 13019
	518:{'name':'ETSI-Digest-Method', 'type':AVP_TYPE_STR},	# Vendor 13019
	519:{'name':'ETSI-Digest-Entity-Body-Hash', 'type':AVP_TYPE_STR},	# Vendor 13019
	520:{'name':'ETSI-Digest-Nextnonce', 'type':AVP_TYPE_STR},	# Vendor 13019
	521:{'name':'ETSI-Digest-Response-Auth', 'type':AVP_TYPE_STR},	# Vendor 13019
	298:{'name':'ETSI-Experimental-Result-Code', 'type':AVP_TYPE_UINT32},	# Vendor 13019
	299:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	300:{'name':'Globally-Unique-Address', 'type':AVP_TYPE_GROUP},	# Vendor 13019
	301:{'name':'Address-Realm', 'type':AVP_TYPE_STR},	# Vendor 13019
	302:{'name':'Logical-Access-Id', 'type':AVP_TYPE_STR},	# Vendor 13019
	303:{'name':'Initial-Gate-Setting', 'type':AVP_TYPE_GROUP},	# Vendor 13019
	304:{'name':'QoS-Profile', 'type':AVP_TYPE_GROUP},	# Vendor 13019
	305:{'name':'IP-Connectivity-Status', 'type':AVP_TYPE_INT32},	# Vendor 13019
	306:{'name':'Access-Network-Type', 'type':AVP_TYPE_GROUP},	# Vendor 13019
	307:{'name':'Aggregation-Network-Type', 'type':AVP_TYPE_INT32},	# Vendor 13019
	308:{'name':'Maximum-Allowed-Bandwidth-UL', 'type':AVP_TYPE_UINT32},	# Vendor 13019
	309:{'name':'Maximum-Allowed-Bandwidth-DL', 'type':AVP_TYPE_UINT32},	# Vendor 13019
	310:{'name':'Maximum-Priority(deprecated)', 'type':AVP_TYPE_UINT32},	# Vendor 13019
	311:{'name':'Transport-Class', 'type':AVP_TYPE_UINT32},	# Vendor 13019
	312:{'name':'Application-Class-ID', 'type':AVP_TYPE_STR},	# Vendor 13019
	313:{'name':'Physical-Access-ID', 'type':AVP_TYPE_STR},	# Vendor 13019
	314:{'name':'Initial-Gate-Setting-ID', 'type':AVP_TYPE_UINT32},	# Vendor 13019
	315:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	316:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	317:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	318:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	319:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	320:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	321:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	322:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	323:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	324:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	325:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	326:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	327:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	328:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	329:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	330:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	331:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	332:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	333:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	334:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	335:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	336:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	337:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	338:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	339:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	340:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	341:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	342:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	343:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	344:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	345:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	346:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	347:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	348:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	349:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	350:{'name':'Location-Information', 'type':AVP_TYPE_GROUP},	# Vendor 13019
	351:{'name':'RACS-Contact-Point', 'type':AVP_TYPE_STR},	# Vendor 13019
	352:{'name':'Terminal-Type', 'type':AVP_TYPE_STR},	# Vendor 13019
	353:{'name':'Requested-Information', 'type':AVP_TYPE_INT32},	# Vendor 13019
	354:{'name':'Event-Type', 'type':AVP_TYPE_INT32},	# Vendor 13019
	355:{'name':'Civic-Location', 'type':AVP_TYPE_STR},	# Vendor 13019
	356:{'name':'Geospatial-Location', 'type':AVP_TYPE_STR},	# Vendor 13019
	357:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	358:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	359:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	360:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	361:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	362:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	363:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	364:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	365:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	366:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	367:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	368:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	369:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	370:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	371:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	372:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	373:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	374:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	375:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	376:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	377:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	378:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	379:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	380:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	381:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	382:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	383:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	384:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	385:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	386:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	387:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	388:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	389:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	390:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	391:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	392:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	393:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	394:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	395:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	396:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	397:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	398:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	399:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	400:{'name':'Session-Bundle-Id', 'type':AVP_TYPE_UINT32},	# Vendor 13019
	401:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	402:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	403:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	404:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	405:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	406:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	407:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	408:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	409:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	410:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	411:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	412:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	413:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	414:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	415:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	416:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	417:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	418:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	419:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	420:{'name':'Event-Type', 'type':AVP_TYPE_INT32},	# Vendor 13019
	421:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	422:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	423:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	424:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	425:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	426:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	427:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	428:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	429:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	430:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	431:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	432:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	433:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	434:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	435:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	436:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	437:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	438:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	439:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	440:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	441:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	442:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	443:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	444:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	445:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	446:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	447:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	448:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	449:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	450:{'name':'Binding-information', 'type':AVP_TYPE_GROUP},	# Vendor 13019
	451:{'name':'Binding-Input-List', 'type':AVP_TYPE_GROUP},	# Vendor 13019
	452:{'name':'Binding-Output-List', 'type':AVP_TYPE_GROUP},	# Vendor 13019
	453:{'name':'V6-Transport-address', 'type':AVP_TYPE_GROUP},	# Vendor 13019
	454:{'name':'V4-Transport-Address', 'type':AVP_TYPE_GROUP},	# Vendor 13019
	455:{'name':'Port-Number', 'type':AVP_TYPE_UINT32},	# Vendor 13019
	456:{'name':'Reservation-Class', 'type':AVP_TYPE_UINT32},	# Vendor 13019
	457:{'name':'Requested-Information', 'type':AVP_TYPE_INT32},	# Vendor 13019
	458:{'name':'Reservation-Priority', 'type':AVP_TYPE_INT32},	# Vendor 13019
	459:{'name':'Service-Class', 'type':AVP_TYPE_STR},	# Vendor 13019
	460:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	461:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	462:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	463:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	464:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	465:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	466:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	467:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	468:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	469:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	470:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	471:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	472:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	473:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	474:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	475:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	476:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	477:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	478:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	479:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	480:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	481:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	482:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	483:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	484:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	485:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	486:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	487:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	488:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	489:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	490:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	491:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	492:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	493:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	494:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	495:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	496:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	497:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	498:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	499:{'name':'Not defined in .xml', 'type':AVP_TYPE_STR},	# Vendor 13019
	500:{'name':'Line-Identifier', 'type':AVP_TYPE_STR},	# Vendor 13019
	501:{'name':'ETSI-SIP-Authenticate', 'type':AVP_TYPE_GROUP},	# Vendor 13019
	502:{'name':'ETSI-SIP-Authorization', 'type':AVP_TYPE_GROUP},	# Vendor 13019
	503:{'name':'ETSI-SIP-Authentication-Info', 'type':AVP_TYPE_GROUP},	# Vendor 13019
	504:{'name':'ETSI-Digest-Realm', 'type':AVP_TYPE_STR},	# Vendor 13019
	505:{'name':'ETSI-Digest-Nonce', 'type':AVP_TYPE_STR},	# Vendor 13019
	506:{'name':'ETSI-Digest-Domain', 'type':AVP_TYPE_STR},	# Vendor 13019
	507:{'name':'ETSI-Digest-Opaque', 'type':AVP_TYPE_STR},	# Vendor 13019
	508:{'name':'ETSI-Digest-Stale', 'type':AVP_TYPE_STR},	# Vendor 13019
	509:{'name':'ETSI-Digest-Algorithm', 'type':AVP_TYPE_STR},	# Vendor 13019
	510:{'name':'ETSI-Digest-QoP', 'type':AVP_TYPE_STR},	# Vendor 13019
	511:{'name':'ETSI-Digest-HA1', 'type':AVP_TYPE_STR}	# Vendor 13019
} ,
# Vendor 637 ALU
637:{
	1136:{'name':'Policy-Counter-Id', 'type':AVP_TYPE_STR},	# Vendor 637
	1137:{'name':'Policy-Counter-Value', 'type':AVP_TYPE_UINT32},	# Vendor 637
	1134:{'name':'Charging-Policy-Report', 'type':AVP_TYPE_GROUP},	# Vendor 637
	1135:{'name':'Policy-Counter', 'type':AVP_TYPE_GROUP},	# Vendor 637
	16:{'name':'Detailed-Result-Cause', 'type':AVP_TYPE_STR},	# Vendor 637
	17:{'name':'Detailed-Result-Code', 'type':AVP_TYPE_UINT32},	# Vendor 637
	15:{'name':'Detailed-Result', 'type':AVP_TYPE_GROUP}	# Vendor 637
} ,
# Vendor 94 Nokia
94:{
	5101:{'name':'Nokia-IMS-Media-Component-Id', 'type':AVP_TYPE_UINT32},	# Vendor 94
	5103:{'name':'Time-Of-First-Usage', 'type':AVP_TYPE_STR},	# Vendor 94
	5104:{'name':'Time-Of-Last-Usage', 'type':AVP_TYPE_STR},	# Vendor 94
	5105:{'name':'Session-Start-Indicator', 'type':AVP_TYPE_STR},	# Vendor 94
	5106:{'name':'Rulebase-Id', 'type':AVP_TYPE_STR},	# Vendor 94
	5109:{'name':'Quota-Consumption-Time', 'type':AVP_TYPE_UINT32},	# Vendor 94
	5110:{'name':'Quota-Holding-Time', 'type':AVP_TYPE_UINT32},	# Vendor 94
	5111:{'name':'Default-Quota', 'type':AVP_TYPE_GROUP},	# Vendor 94
	5112:{'name':'Nokia-URI', 'type':AVP_TYPE_STR},	# Vendor 94
	5113:{'name':'NSN-Token-Value', 'type':AVP_TYPE_STR}	# Vendor 94
} ,
# Vendor 5535 TGPP2
5535:{
	1000:{'name':'Bearer-Usage', 'type':AVP_TYPE_INT32},	# Vendor 5535
	1001:{'name':'Charging-Rule-Install', 'type':AVP_TYPE_GROUP},	# Vendor 5535
	1002:{'name':'Charging-Rule-Remove', 'type':AVP_TYPE_GROUP},	# Vendor 5535
	1003:{'name':'Charging-Rule-Definition', 'type':AVP_TYPE_GROUP},	# Vendor 5535
	1004:{'name':'Charging-Rule-Base-Name', 'type':AVP_TYPE_STR},	# Vendor 5535
	1005:{'name':'Charging-Rule-Name', 'type':AVP_TYPE_STR},	# Vendor 5535
	1006:{'name':'Event-Trigger', 'type':AVP_TYPE_INT32},	# Vendor 5535
	1007:{'name':'Metering-Method', 'type':AVP_TYPE_INT32},	# Vendor 5535
	1008:{'name':'Offline', 'type':AVP_TYPE_INT32},	# Vendor 5535
	1009:{'name':'Online', 'type':AVP_TYPE_INT32},	# Vendor 5535
	1010:{'name':'Precedence', 'type':AVP_TYPE_UINT32},	# Vendor 5535
	1011:{'name':'Primary-CCF-Address', 'type':AVP_TYPE_STR},	# Vendor 5535
	1012:{'name':'Primary-OCS-Address', 'type':AVP_TYPE_STR},	# Vendor 5535
	1014:{'name':'Reporting-Level', 'type':AVP_TYPE_INT32},	# Vendor 5535
	1015:{'name':'Secondary-CCF-Address', 'type':AVP_TYPE_STR},	# Vendor 5535
	1016:{'name':'Secondary-OCS-Address', 'type':AVP_TYPE_STR},	# Vendor 5535
	1017:{'name':'TFT-Filter', 'type':AVP_TYPE_STR},	# Vendor 5535
	1018:{'name':'TFT-Packet-Filter-Information', 'type':AVP_TYPE_GROUP},	# Vendor 5535
	1019:{'name':'ToS-Traffic-Class', 'type':AVP_TYPE_STR},	# Vendor 5535
	9010:{'name':'3GPP2-BSID', 'type':AVP_TYPE_STR}	# Vendor 5535
} }

