#!/usr/bin/env python
# -coding:utf-8
import sys
from QBCodeSpecs.objcRecoginition import ObjectiveCParserListener
from QBCodeSpecs.driver.ViolationDataMananger import *
from QBCodeSpecs.driver.Violation import *
import re

class MethodNameRuleListener(ObjectiveCParserListener.ObjectiveCParserListener):
	def __init__(self, violation):
		super(MethodNameRuleListener,self).__init__()
		self.violation = violation
		if self.violation.configinfo.has_key("Regex"):
			self.regex = self.violation.configinfo["Regex"]
		else:
			self.regex = r"[a-z]"
		


	def send_violation(self, startline, startcolumn, selector):

		path = self.violation.path
		configInfo = self.violation.configinfo

		violInfo = Violation(path, configInfo)
		violInfo.startline = startline
		violInfo.startcolumn = startcolumn
		# violInfo.message = "Conforming to regular expressions:" + "\"" + self.regex + "\""
		violInfo.message =  "方法名 "+ "\"" + selector + "\"" + " 不符合正则 " + "\"" + self.regex + "\""
		violInfo.set_priority("2")
		violInfo.set_rulename("Name")
		violInfo.set_rulecategory("方法名定义")
		violInfo.set_democode("- (void)methodSeletor")
		violInfo.set_noncompliant_code("- (void)MethodSeletor \n\
- (void)_methodSeletor")
		violationDataMananger.addViolation(violInfo)


	def checkSelector(self, selector):
		if len(self.regex) > 0:
			if re.match(self.regex, selector.getText()):
			    print 'ok'
			else:
				token = selector.start
				print "error selector:" + "\"" + selector.getText() + "\"" + "------" + "[" + str(token.line) + ":" + str(token.column) + "]"
				self.send_violation(token.line, token.column, selector.getText())
				print 'failed'

	def exitMethodSelector(self, ctx):

		selector = ctx.selector()
		if selector != None:
			# print("selector:"+selector.getText());
			self.checkSelector(selector)


		keywordDeclarator = ctx.keywordDeclarator()
		if isinstance(keywordDeclarator, list):

			for index in range(len(keywordDeclarator)):
				selector = keywordDeclarator[index].selector()
				self.checkSelector(selector)
			
