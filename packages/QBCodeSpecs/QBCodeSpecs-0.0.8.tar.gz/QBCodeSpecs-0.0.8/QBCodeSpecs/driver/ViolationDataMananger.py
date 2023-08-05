#!/usr/bin/env python
# -coding:utf-8
import Violation
import linecache

class ViolationDataMananger(object):
	def __init__(self):
		self.list = [];
		self.__total_files_number = 0
		self.priority1 = 0
		self.priority2 = 0
		self.priority3 = 0
		self.files_set = set() 
		

	def addViolation(self, violation):
		# startline = violation.startline
		# path = violation.path
		# violation.currCode = linecache.getline(path,startline)
		self.list.append(violation)

	def get_total_files_number(self):
		return str(self.__total_files_number)

	def set_total_files_number(self, file_num):
		self.__total_files_number = file_num

	def summary(self):

		
		for violation in self.list:
			# violation files
			self.files_set.add(violation.path)

			# priority
			priority = violation.get_priority()
			if priority == "1" :
				self.priority1 += 1
			elif priority == "2" :
				self.priority2 += 1
			elif priority == "3" :
				self.priority3 += 1


	def numberOfViolationsWithPriority(self, level):
		if level == 1:
			return str(self.priority1)
		elif level == 2:
			return str(self.priority2)
		elif level == 3:
			return str(self.priority3)
		else:
			return str(0)


	def numberOfFilesWithViolations(self):
		return str(len(self.files_set))



violationDataMananger = ViolationDataMananger()
