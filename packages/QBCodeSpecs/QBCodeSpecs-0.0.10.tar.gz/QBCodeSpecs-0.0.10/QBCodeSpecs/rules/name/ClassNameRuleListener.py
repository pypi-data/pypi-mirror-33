#!/usr/bin/env python
# -coding:utf-8
import sys
from QBCodeSpecs.grammar.ObjectiveCParserListener import *
from QBCodeSpecs.driver.ViolationDataMananger import *
from QBCodeSpecs.driver.Violation import *
import re



class ClassNameRuleListener(ObjectiveCParserListener):

	def __init__(self, violation):
		super(ClassNameRuleListener,self).__init__()
		self.violation = violation
		if self.violation.configinfo.has_key("Regex"):
			self.regex = self.violation.configinfo["Regex"]
		else:
			self.regex = r"[A-Z]"


	def send_violation(self, startline, startcolumn, classname):

		path = self.violation.path
		configInfo = self.violation.configinfo

		violInfo = Violation(path, configInfo)
		violInfo.startline = startline
		violInfo.startcolumn = startcolumn
		violInfo.message =  "类名 "+ "\"" + classname + "\"" + " 不符合正则 " + "\"" + self.regex + "\""
		violInfo.set_priority("2")
		violInfo.set_rulename("Name")
		violInfo.set_rulecategory("类名定义")
		violInfo.set_democode("@interface MttDataManager : NSObject")
		violInfo.set_noncompliant_code("@interface mttDataManager : NSObject \n\
@interface _MttDataManager : NSObject")
		
		violationDataMananger.addViolation(violInfo)
		
	def exitClassInterface(self, ctx):

		context = ctx.genericTypeSpecifier()

		# get class name
		identifier = context.identifier()
		print(identifier.getText())
		
		token = identifier.IDENTIFIER()
		commonToken = token.symbol
		print(commonToken)

		# line num
		print("line number:")
		print(commonToken.line)
		lineNum = commonToken.line
		
		# column num
		print("column number:")
		print(commonToken.column)
		columnNum = commonToken.column
		
		className = token.getText()

		if len(self.regex) > 0:
			if re.match(self.regex, className):
				print('ok')
			else:
				self.send_violation(lineNum, columnNum, className)
				print('failed')
		
			
