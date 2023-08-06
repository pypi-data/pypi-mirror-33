# Created by george zhao, who is working for NOKIA, 2010-2012, 2014-2018.												#
# This lib is based on python 3.6.5																						#

# In tools module, all functions name use python style.																	#

from datetime import datetime, timedelta
from pyDiameter.pyDiaConst import DEFAULT_BYTES_ORDER
from pyDiameter.pyDiaConst import ZERO_LEN_BYTES
from pyDiameter.pyDiaConst import NULL_BYTE

# For address to bytes convertion.																						#
__IPV4_TYPE_STR = 'ipv4'
__IPV6_TYPE_STR = 'ipv6'
__IPV4_TYPE_VALUE = 1
__IPV6_TYPE_VALUE = 2
__IPV4_VALUE_BUFF_LEN = 4
__IPV6_VALUE_BUFF_LEN = 16
__PROTOCOL_TYPE_BUFF_LEN = 2

def __bytes_to_ipv4(bytes):
	assert len(bytes) == __IPV4_VALUE_BUFF_LEN
	r = ''
	for b in bytes:
		r += str(b)
		r += '.'
	return r[:-1]
	
def __bytes_to_ipv6(bytes, compress = 0):
	assert len(bytes) == __IPV6_VALUE_BUFF_LEN
	i = 0
	r = ''
	for b in bytes:
		r += (('%02x') %b)
		if (i+1) % 2 == 0: r += ':'
		i += 1
	r = r[:-1]
	if compress == 0: return r
	i = 0
	last_start = -1
	max_zero_len = 0
	start = 0
	end = 0
	print(r, len(r))
	while i < len(r):
		start = r.find('0000:', end)
		if -1 == start:
			break
		i = start
		j = i
		while j < len(r):
			if r[j] == '0' or r[j] == ':':
				j += 1
			else:
				break;
		if (j-i) > max_zero_len: 
			max_zero_len = j - i
			last_start = start
		end = j
		print (start, end)
		input()
	if 0 == last_start and max_zero_len >= 8 : r = r[:last_start] + '::' + r[last_start+max_zero_len:]
	elif 0 < last_start and max_zero_len >= 8 : r = r[:last_start] + ':' + r[last_start+max_zero_len:]
	r = r.replace('0000:', '0:')
	return r
	
def __ipv4_to_bytes(address):
	r = ZERO_LEN_BYTES
	numstrs = address.split(".")
	for numstr in numstrs:
		i = int(numstr)
		r += i.to_bytes(1, DEFAULT_BYTES_ORDER)
	return r
	
def __ipv6_to_bytes(address):
	def __hexstr_to_bytes(hexStr):
		if len(hexStr) == 1: hexStr = '0' + hexStr
		assert len(hexStr) % 2 == 0
		i = 0
		r =  ZERO_LEN_BYTES
		while i < len(hexStr):
			s = hexStr[i:i+2]
			r += int(s, 16).to_bytes(1, DEFAULT_BYTES_ORDER)
			i += 2
		return r
	i = 0
	r = ZERO_LEN_BYTES
	multiZeroIndex = address.find('::')
	if -1 == multiZeroIndex:
		address = address.replace(':','')
		r = __hexstr_to_bytes(address)
	else: 
		r1 = __hexstr_to_bytes(address[:multiZeroIndex].replace(':',''))
		r2 = __hexstr_to_bytes(address[multiZeroIndex+2:].replace(':',''))
		r = r1 + NULL_BYTE * int((__IPV6_VALUE_BUFF_LEN - len(r1) - len(r2))) + r2
	return r
	
def bytes_to_address(bytes_buff, compress = 0):
	address_type_bytes = bytes_buff[:__PROTOCOL_TYPE_BUFF_LEN]
	address_value_bytes = bytes_buff[__PROTOCOL_TYPE_BUFF_LEN:]
	if __IPV4_TYPE_VALUE == int.from_bytes(address_type_bytes,DEFAULT_BYTES_ORDER): 
		address_type = __IPV4_TYPE_STR
		address_value = __bytes_to_ipv4(address_value_bytes)
	elif __IPV6_TYPE_VALUE == int.from_bytes(address_type_bytes,DEFAULT_BYTES_ORDER): 
		address_type = __IPV6_TYPE_STR
		address_value = __bytes_to_ipv6(address_value_bytes, compress)
	return (address_type, address_value)
	
def address_to_bytes(address_tuple):
	address_type, address_value = address_tuple
	r = ZERO_LEN_BYTES
	if address_type == __IPV4_TYPE_STR: 
		r = __IPV4_TYPE_VALUE.to_bytes(2, DEFAULT_BYTES_ORDER)
		r += __ipv4_to_bytes(address_value)
	elif address_type == __IPV6_TYPE_STR: 
		r = __IPV6_TYPE_VALUE.to_bytes(2, DEFAULT_BYTES_ORDER)
		r += __ipv6_to_bytes(address_value)
	else:
		raise ValueError('Only ipv4 and ipv6 are supported by this function.')
	return r
	
# For time and bytes convertion.																									#
# Even RFC5905 obsoletes RFC4330,																									#
# but Diameter Base Protocol RFC6773 still tell us Time format should support time from year 1968 to 2104							#
# Actually, Time format could be translated to anytime.																				#
# In this tool, we will format bytes to time string according to RFC6773 Section 6. 												#
# Year 1968 Jan 20, 03:14:08 to Year 2104, Feb 26, 09:42:23																			#
# Year 1968 Jan 20, 03:14:08 is the time 2147483648(0x80000000) seconds elapse from 1900, Jan 1, 00:00:00							#
__Y1968_JAN_SECS = 2147483648
__TOTAL_SECS = 4294967296
__TIMESTAMP_BYTES_LEN = 4

def bytes_to_time(bytesBuff):
	epoc = datetime(1968, 1, 20, 3, 14, 8)
	s = int.from_bytes(bytesBuff, DEFAULT_BYTES_ORDER)
	s -= __Y1968_JAN_SECS
	if s < 0: s += __TOTAL_SECS
	dt = timedelta(seconds = s)
	r = epoc + dt
	return (r.year, r.month, r.day, r.hour, r.minute, r.second)
		
def time_to_bytes(year = 1900, month = 1, day = 1, hour = 0, minute = 0, second = 0):
	epoc = datetime(1900, 1, 1, 0, 0, 0)
	target_date = datetime(year, month, day, hour, minute, second)
	s = int((target_date - epoc).total_seconds())
	b = (s % __TOTAL_SECS)
	return b.to_bytes(__TIMESTAMP_BYTES_LEN, DEFAULT_BYTES_ORDER)
