#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='pyDiameter',
    version='0.18.7.13',
    description=(
        'pyDiameter is created by George Zhao, who is working for NOKIA, 2010-2012, 2014-2018.\n This lib is used for encoding and decoding Diameter protocol message(an AAA protocol replace the RADIUS).'
    ),
    long_description="""
===================
Introduction
===================
pyDiameter is a library which is used to decoding and encoding Diameter protocol message.

Diameter protocol is an AAA protocol and defined in RFC6733 (RFC3588 is obsoleted by RFC6733).

Decoding a diameter protocol message means, the library will help application decode protolcol bytes to the library object, which is more simple to handle.

Encoding a diameter protocol message means, the library will help application encode the library object(usually a DiaMessage object in pyDiameter library) into a bytes variable.

pyDiameter is written by python purely.

pyDiameter is written on python 3.6.5, python 2 is not supported.

===================
Author
===================
George Zhao who is working for Nokia in 2010-2012, 2014-2018.

maito: georgezhao_1980@163.com

===================
How to get it
===================

::

	pip install pyDiameter

===================
Getting start
===================
To get a start for decoding or encoding a diameter message with pyDiameter, you can read the example after pip installing.

The example folder is located in pyDiameter folder in your site-packages of your Python.

Please refer to example-dictTest.py to get start for the Diameter protocol AVP dictionary.

Dictionary
===============
This dictionary contains more than 2000 AVP definitions, as well as including several popular vendors definitions (Base, 3GPP, Nokia, Ericsson, Cisco etc.)

Please note that, decoding is depending on the dictionary defined in pyDiameter.pyDiaAVPDict, if you have some special AVP definition which is not contained in this dictionary, example-dictTest.py could help you to know how to add new AVP definition in the dictionary, and how to update it.

Please make sure that there are all definitions you need defined in the dictionary before decoding the diameter message.

AVP and Message
===============
Please refer to example-avp.py to get start for the Diameter protolcol AVP handling.

And refer to example-msg1.py to get start for the Diameter protocol message handling.

If you want an example just like a 'Hello, world', please refer to code below.

::

	from pyDiameter.pyDiaMessage import DiaMessage
	from pyDiameter.pyDiaAVPTypes import DiaAVPStr
	from pyDiameter.pyDiaAVPPath import DiaAVPPath

	msg = DiaMessage()
	msg.setRequestFlag()
	avp = DiaAVPStr()
	avp.setAVPCode(263)
	avp.setAVPVSFlag()
	avp.setAVPVendor(10415)
	avp.setAVPValue(b'Hello, world.')
	dap = DiaAVPPath()
	dap.setPath('')
	msg.addAVPByPath(dap, avp)

pyDiameter supports only basic types defined in RFC6733.

Please refer to following table for supported types list. (import them from pyDiameter.pyDiaAVPTypes)

=============== ===============
pyDiameter 		RFC6733
=============== ===============
DiaAVPStr 		OctectString
DiaAVPInt32 	Integer32
DiaAVPUInt32 	Unsigned32
DiaAVPInt64 	Integer64
DiaAVPUInt64 	Unsigned64
DiaAVPFloat32 	Float32
DiaAVPFloat64 	Float64
DiaAVPGroup 	Grouped
===============	===============

All DiaAVPxxx classes are derived from DiaAVP which is defined in pyDiameter.pyDiaAVPBase. And users could not initialize a DiaAVP object since it is an abstract class.

All Sub-classes of DiaAVP have method called getAVPType().

It return a Python string which describes the type of the object.

The returned value could be one of values of following. (import them from pyDiameter.pyDiaAVPConst)

================== ===============
Const 				Value
================== ===============
AVP_TYPE_UNKNOWN 	unknown
AVP_TYPE_STR 		str
AVP_TYPE_INT32 		int32
AVP_TYPE_UINT32 	uint32
AVP_TYPE_INT64 		int64
AVP_TYPE_UINT64 	uint64
AVP_TYPE_FLOAT32 	float32
AVP_TYPE_FLOAT64 	float64
AVP_TYPE_GROUP		grp
================== ===============

AVP Path
===============
When you operate DiaMessage object in pyDiameter.pyDiaMessage, sometimes, you need visit, add or remove some AVPs from the message.

You can use DiaAVPPath object to locate the AVP in the message.

DiaAVPPath could be imported from pyDiameter.pyDiaAVPPath.

And DiaAVPPath object uses a diameter avp path language to describe the AVP path. (Defined by George Zhao, not a well-known language.)

The AVP path is described as:

::

'vendor/avpCode[sameCodeIndex]->vendor/avpCode[sameCodeIndex]->vendor/avpCode[sameCodeIndex]...'

e.g. 10415/628[1]->10415/630[0] means I want to visit the AVP, the location is: the first AVP 630(vendor 10415) under the second AVP 628(vendor 10415).

sameCodeIndex means if there are several same AVPs with same AVP code and vendor, which index is target to be visited.

**Note that, sameCodeIndex is counted from zero.**

Tools
===============

In pyDiameter.pyDiaAVPTools, we provide four functions to help you treat some special AVP types.

The address type, and the time type are both derived from OctectString basic type according to RFC6733.

================== ================================================================================================================================
Functions			Examples
================== ================================================================================================================================
address_to_bytes	address_to_bytes(('ipv4','172.18.0.1')); address_to_bytes(('ipv6','2000:1234:ac12:abcd:abcd:abcd:abcd:abc1'))
bytes_to_address	bytes_to_address(diameter_address_avp_bytes_buff)
time_to_bytes		time_to_bytes(year=1980, month=7 , day=8, hour=20, minute=0, second=0)
bytes_to_time		bytes_to_time(bytes_buff)
================== ================================================================================================================================

**Note that, time is counted from Year 1968 Jan 20, 03:14:08 to Year 2104, Feb 26, 09:42:23, according to RFC6733 and an even obsoleted RFC4330.**

**Only ipv4 and ipv6 are supported by tools, other protocols should be handled by user as an ordinary OctectString.**

**When you set ipv6 value, the compress ipv6 value could be supported by tools, like 2000::1 or ::1.**

Any other problem, please refer to 'Any problem' section below.

===================
Any problem
===================
Please contact georgezhao_1980@163.com

Author will check mail irregularly, support is not guaranteed.

Author will answer question as immediately as author can.
""",
    author='George Zhao',
    author_email='georgezhao_1980@163.com',
    maintainer='George Zhao',
    maintainer_email='georgezhao_1980@163.com',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    url='http://not-available.now',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
)