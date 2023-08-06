# Created by george zhao, who is working for NOKIA, 2010-2012, 2014-2018.												#
# This lib is based on python 3.6.5																						#

# This class is defined for locating a AVP in a Diameter Message.														#
# When it is used in DiaMessage, it is a path start from the root of the message.										#
# The DiaAVPPath use a path index, defined as: "vendor/avpcode[sameAVPIndex]->vendor/avpCode[sameAVPIndex]->..."		#
# e.g. "10415/517[0]->10415/519[1]->10415/507[0]"																		#
# In this path index, vendor is vendor code for the AVP, avpCode is code of the AVP.									#
# sameAVPIndex means which AVP you want to visit, if there are several AVPs have same vendor and code.					#

import re

class DiaAVPPath:
	def __init__(self):
		self.__pathArray=[]
		
	def __analyzePath(self, path):
		seperator = "->"
		nodes = []
		start = 0
		while True:
			end = path.find(seperator, start)
			if -1 == end:
				break
			else:
				if not start == end:
					nodes.append(path[start:end])
					start = end + len(seperator)
				else:
					break;
		if -1 == end:
			nodes.append(path[start:])
		return nodes
		
	def __analyzeNode(self, node):
		try:
			vendor = int(node[:node.find("/")])
			code = int(node[node.find("/")+1:node.find("[")])
			sai = int(node[node.find("[")+1:node.find("]")])
		except ValueError:
			raise ValueError("For vendor, code and sameAVPIndex, only number is allowed.")
			return None
		if sai < 0: raise ValueError("SameAVPIndex should be a positive value or zero.")
		r = [vendor, code, sai]
		return r
		
	def __analyzePathNodes(self, nodes):
		for node in nodes:
			s = re.match("\d+/\d+\[\d+]$", node)
			if not None == s:
				avpData = self.__analyzeNode(node)
				if not None == avpData:
					self.__pathArray.append(avpData)
			else:
				break;
		
	def setPath(self, path):
		nodes = self.__analyzePath(path)
		self.__analyzePathNodes(nodes)
		
	def getLayersCount(self):
		return len(self.__pathArray)
		
	def getAVPVendor(self, layer):
		return self.__pathArray[layer][0]
		
	def getAVPCode(self, layer):
		return self.__pathArray[layer][1]
	
	def getAVPSameAVPIndex(self, layer):
		return self.__pathArray[layer][2]
		
	def removeTop(self):
		if self.getLayersCount() >= 0:
			del self.__pathArray[0]
		
	def removeTail(self):
		if self.getLayersCount() >= 0:
			del self.__pathArray[len(self.__pathArray)-1]
			
	def getPath(self):
		i = 0
		r = ''
		while i < self.getLayersCount():
			if not i == self.getLayersCount() - 1:
				r += str(self.getAVPVendor(i)) + "/" + str(self.getAVPCode(i)) + "["+str(self.getAVPSameAVPIndex(i)) + "]"+"->"
			else:
				r += str(self.getAVPVendor(i)) + "/" + str(self.getAVPCode(i)) + "["+str(self.getAVPSameAVPIndex(i)) + "]"
			i += 1
		return r