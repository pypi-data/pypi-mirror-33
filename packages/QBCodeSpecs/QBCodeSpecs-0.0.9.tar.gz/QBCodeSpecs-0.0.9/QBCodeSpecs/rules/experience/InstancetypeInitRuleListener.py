#!/usr/bin/env python
# -coding:utf-8
import sys
from QBCodeSpecs.objcRecoginition.ObjectiveCParserListener import *
from QBCodeSpecs.driver.ViolationDataMananger import *
from QBCodeSpecs.driver.Violation import *
import re
import linecache


class InstancetypeInitRuleListener(ObjectiveCParserListener):

	def __init__(self, violation):
		super(InstancetypeInitRuleListener,self).__init__()
		self.violation = violation
		self.startline = 0
		self.startcolumn = 0


	def send_violation(self, startline, startcolumn):

		path = self.violation.path
		configInfo = self.violation.configinfo

		violInfo = Violation(path, configInfo)
		violInfo.startline = startline
		violInfo.startcolumn = startcolumn

		# violInfo.set_rulename("")
		violInfo.set_rulecategory("初始化返回值类型")
		codeStr = linecache.getline(path,self.startline)
		# print "source code:" + codeStr
		violInfo.message = "方法定义 " + codeStr + " 返回值的类型应为instancetype"
		#"Conforming to regular expressions:" + "\"" + self.regex + "\"" 

		democode = "- (instancetype)init"
		violInfo.set_democode(democode)
		noncompliant = "- (id)init"
		violInfo.set_noncompliant_code(noncompliant)
		violationDataMananger.addViolation(violInfo)

	def enterImplementationDefinitionList(self, ctx):


		classDefList = ctx.classMethodDefinition()
		for classDef in classDefList:
			methodSel = classDef.methodDefinition().methodSelector()

			selectorStr = methodSel.getText()
			print methodSel.getText()
			if selectorStr.startswith("init"):
				
				
				
				methodType = classDef.methodDefinition().methodType()
				typeName = methodType.typeName().getText()
				# print "---typeName:" + typeName
				if not "instancetype" in typeName:
					# print "ok"
					token = methodSel.start
					self.startline = token.line
					self.startcolumn = token.column
					self.send_violation(token.line, token.column)
				# else:
				# 	print "fail"


		instanceDefList = ctx.instanceMethodDefinition()
		for instanceDef in instanceDefList:
			methodSel = instanceDef.methodDefinition().methodSelector()
			selectorStr = methodSel.getText()
			# token = methodSel.start
			# print "line:" + str(token.line) + "column:" + str(token.column)
			print methodSel.getText()
			if selectorStr.startswith("init"):
				token = methodSel.start
				self.startline = token.line
				self.startcolumn = token.column
				# foundShared = True
				methodType = instanceDef.methodDefinition().methodType()
				typeName = methodType.typeName().getText()
				# print "---typeName:" + typeName
				if not "instancetype" in typeName:
					# print "ok"
					token = methodSel.start
					self.startline = token.line
					self.startcolumn = token.column
					self.send_violation(token.line, token.column)
				# else:
				# 	print "fail"


