

# class Violation(object):
# 	def  __init__(self, fileName, configInfo):
# 		self.fileName = fileName
# 		self.configInfo = configInfo
# 		self.lineNum = 0
# 		self.columnNum = 0

class Violation(object):
	"""docstring for ClassName"""
	def __init__(self, path, configinfo={}):
		super(Violation, self).__init__()
		self.path = path
		self.configinfo = configinfo
		self.startline = 0
		self.startcolumn = 0
		self.message = ""
		self.__rulename = ""
		self.__rulecategory = ""
		self.__democode = ""
		self.__noncomliant = ""
		self.__priority = "3"
		self.currCode = ""

	

	def get_rulename(self):
		if self.configinfo.has_key('RuleName'):
			return self.configinfo['RuleName']
		else:
			return self.__rulename

	def set_rulename(self, rulename):
		self.__rulename = rulename

	def get_rulecategory(self):

		if self.configinfo.has_key('RuleCategory'):
			return self.configinfo['RuleCategory']
		else:
			return self.__rulecategory

	def set_rulecategory(self, rulecategory):
		self.__rulecategory = rulecategory


	def get_priority(self):

		if self.configinfo.has_key('Priority'):
			return self.configinfo['Priority']
		else:
			return self.__priority

	def set_priority(self, priority):
		self.__priority = priority

	def get_democode(self):

		if self.configinfo.has_key('DemoCode'):
			return self.configinfo['DemoCode']
		else:
			return self.__democode

	def set_democode(self, democode):
		self.__democode = democode

	def get_noncompliant_code(self):
		if self.configinfo.has_key('Noncomliant'):
			return self.configinfo['Noncomliant']
		else:
			return self.__noncomliant

	def set_noncompliant_code(self, noncomliant):
		self.__noncomliant = noncomliant





	
		

