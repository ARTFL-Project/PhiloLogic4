
class ContentExtractor(object):
	def __init__(self,path,field,context,destination):
		self.path = path
		self.field = field
		self.context = context
		self.destination = destination
		
	def __call__(self,element,event):
		if event[0] != "text":
			return False
		if element in self.context.findall(self.path):
			self.destination[self.field] = self.destination.get(self.field,"") + event[1]
			return True
		else: return False
		
class AttributeExtractor(object):
	def __init__(self,path,field,context,destination):
		self.path = path
		att_start = self.path.rfind("@")
		self.att_name = self.path[(att_start + 1):]
		self.path = self.path[:att_start]
		#print "setting up path %s" % self.path

		self.field = field
		self.context = context
		self.destination = destination
		
	def __call__(self,element,event):
		if event[0] == "start":
			#print "looking for @%s in %s" % (self.att_name, element.attrib)
			if element in self.context.findall(self.path) and self.att_name in element.attrib:
				self.destination[self.field] = self.destination.get(self.field,"") + (element.attrib[self.att_name] or "")
				return True
		return False
