import re
import os
import sys

class Toms:
	def __init__(self,file):
		self.filename = file
		self.fh = open(self.filename)
		self.pos = [0]
		self.line = ""
		self.data = {}
		self.cache = {}

	def __getitem__(self,n):
		try:
			len(n)
		except TypeError:
			n = [n]
		cachekey = len(n)
		try:
			if self.cache[cachekey]["id"] == n:
				return self.cache[cachekey]
		except (IndexError,KeyError):
			pass
		if len(n) < len(self.pos):
			n = [n[i] if i < len(n) else 0 for i,x in enumerate(self.pos)]
		if obj_cmp(self.pos,n) > 0:
			self.rewind()
		while obj_cmp(self.pos,n) < 0:
			self.line = self.fh.readline()
			self.parseline()
		if obj_cmp(self.pos,n) > 0:
			raise IndexError
		else:
			self.cache[cachekey] = self.data
			return self.data

	def rewind(self):
		self.fh.seek(0)
		self.pos = [0]
	
	def __iter__(self):
		self.rewind()
		self.pos = [0]
		while True:
			self.line = self.fh.readline()
			if self.line == "":
				raise StopIteration
			self.parseline()
			yield self.data

	def parseline(self):
		fields = self.line.strip().split("\t")
		idstr = fields.pop(0)
		self.pos = [int(x) for x in idstr.split(" ")]
		self.data = {"id":self.pos}
		while fields:
			(value,key) = fields.pop(), fields.pop()
			self.data[key] = value
		
def obj_cmp(x,y):
	for a,b in zip(x,y):
		if a < b:
			return -1
		if a > b:
			return 1
	else:
		return 0

def toms_select(toms, value_pattern, field_pattern=r".*?", corpus=None):
	if corpus:
		cptr = corpus.__iter__()
		c = cptr.next()
	result = []
	for i in toms:
		r = None
		for field in i:
			if field != "id":
				if re.match(field_pattern,field):
					if re.match(value_pattern,i[field], re.IGNORECASE):
						r = i
		if corpus:
			while obj_cmp(c,i["id"]) < 0:
				c = cptr.next()
			if obj_cmp(c,["id"]) > 0:
				r = None
		if r:
			result.append(r)
	return result
	
def printhelper(item,fd):
	output = ""
	id = item.pop("id")
	output += " ".join(id)
	for key,value in item.items():
		output += "\t%s\t%s" % (key,value)
	print >> fd, output

def mktoms(file_in=sys.stdin,file_out=sys.stdout):
	stack = []
	for line in file_in:
		(type,rest) = line.strip().split(" ",1)
		if type == "word":
			pass
		else:
			tagmatch = re.match(r"<([^/>]+?.*?)>|</(.+?)>",rest)
			if tagmatch:
				object = [x for x in rest[tagmatch.end(0):].split(" ") if x != ""]
				id = object[:7]
				byte = object[7]
				if tagmatch.group(1):
					tagtext = tagmatch.group(1)
					if " " in tagtext:
						(name,att) = tagtext.split(" ",1)
					else:
						name = tagtext
					stack.append({"id":id,"type":type,"name":name,"start":byte})
				elif tagmatch.group(2):
					item = stack.pop()
					item["end"] = byte
					if item["type"] != "para": 
						printhelper(item,file_out)
			elif type == "meta":
				(type,name,value) = line.strip().split(" ",2)
				if name not in stack[-1]:
					stack[-1][name] = value