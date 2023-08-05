#!/usr/bin/env python
# -coding:utf-8
import sys
from QBCodeSpecs.grammar.ObjectiveCParserListener import *
from QBCodeSpecs.driver.ViolationDataMananger import *
from QBCodeSpecs.driver.Violation import *
import re
import linecache


class CategoryMethodNameRuleListener(ObjectiveCParserListener):

	def __init__(self, violation):
		super(CategoryMethodNameRuleListener,self).__init__()
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
		violInfo.set_rulecategory("类别方法名定义")
		codeStr = linecache.getline(path, startline)
		# print "source code:" + codeStr
		violInfo.message = "类别方法名 " + codeStr +" 的定义需要包含前缀"
		# "方法定义 " + codeStr + " 返回值的类型应为instancetype"
		#"Conforming to regular expressions:" + "\"" + self.regex + "\"" 

		democode = "@interface NSData (ZOCTimeExtensions)\n\
- (NSString *)zoc_timeAgoShort;\n\
@end"
		violInfo.set_democode(democode)
		noncompliant = "@interface NSData (ZOCTimeExtensions)\n\
- (NSString *)timeAgoShort;\n\
@end"
		violInfo.set_noncompliant_code(noncompliant)
		violationDataMananger.addViolation(violInfo)

	def exitCategoryImplementation(self, ctx):

		identifier = ctx.identifier()
		# print "identifier--" + identifier.getText()
		identifierStr = identifier.getText()
		prefix = ""
		if len(identifierStr) > 3:
			prefix = identifierStr[0:3]
		if len(prefix) == 0:
			return

		prefix = prefix.lower() + "_"
		# print "prefix--" + prefix

		implementationDefinitionContext = ctx.implementationDefinitionList()

		classDefList = implementationDefinitionContext.classMethodDefinition()
		for classDef in classDefList:
			methodSel = classDef.methodDefinition().methodSelector()

			selectorStr = methodSel.getText()
			# print "class=" + methodSel.getText()
			if not selectorStr.startswith(prefix):
				token = methodSel.start
				startline = token.line
				startcolumn = token.column
				self.send_violation(startline, startcolumn)

				


		instanceDefList = implementationDefinitionContext.instanceMethodDefinition()
		for instanceDef in instanceDefList:
			methodSel = instanceDef.methodDefinition().methodSelector()
			selectorStr = methodSel.getText()
			# print "instance=" + methodSel.getText()
			if not selectorStr.startswith(prefix):
				token = methodSel.start
				startline = token.line
				startcolumn = token.column
				self.send_violation(startline, startcolumn)
				


