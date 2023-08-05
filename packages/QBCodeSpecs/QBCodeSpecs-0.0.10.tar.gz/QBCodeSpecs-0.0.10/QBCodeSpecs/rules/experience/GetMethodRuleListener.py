#!/usr/bin/env python
# -coding:utf-8
import sys
from QBCodeSpecs.grammar.ObjectiveCParserListener import *
from QBCodeSpecs.driver.ViolationDataMananger import *
from QBCodeSpecs.driver.Violation import *
import re
import linecache


class GetMethodRuleListener(ObjectiveCParserListener):

	def __init__(self, violation):
		super(GetMethodRuleListener,self).__init__()
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
		violInfo.set_rulecategory("Getter写法")
		# codeStr = linecache.getline(path,self.startline)
		# print "source code:" + codeStr
		violInfo.message = "请直接通过属性名来定义方法"
		# "方法定义 " + codeStr + " 返回值的类型应为instancetype"
		#"Conforming to regular expressions:" + "\"" + self.regex + "\"" 

		democode = "- (id)name"
		violInfo.set_democode(democode)
		noncompliant = "- (id)getName"
		violInfo.set_noncompliant_code(noncompliant)
		violationDataMananger.addViolation(violInfo)

	def enterImplementationDefinitionList(self, ctx):


		classDefList = ctx.classMethodDefinition()
		for classDef in classDefList:
			methodSel = classDef.methodDefinition().methodSelector()

			selectorStr = methodSel.getText()
			print methodSel.getText()
			if selectorStr.startswith("get"):
				token = methodSel.start
				startline = token.line
				startcolumn = token.column
				self.send_violation(startline, startcolumn)
				


		instanceDefList = ctx.instanceMethodDefinition()
		for instanceDef in instanceDefList:
			methodSel = instanceDef.methodDefinition().methodSelector()
			selectorStr = methodSel.getText()
			# token = methodSel.start
			# print "line:" + str(token.line) + "column:" + str(token.column)
			print methodSel.getText()
			if selectorStr.startswith("get"):
				token = methodSel.start
				startline = token.line
				startcolumn = token.column
				self.send_violation(startline, startcolumn)
				


