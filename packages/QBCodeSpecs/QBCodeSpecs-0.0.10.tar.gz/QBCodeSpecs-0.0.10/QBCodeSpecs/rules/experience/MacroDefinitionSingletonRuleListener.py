#!/usr/bin/env python
# -coding:utf-8
import sys
from QBCodeSpecs.grammar.ObjectiveCParserListener import *
from QBCodeSpecs.driver.ViolationDataMananger import *
from QBCodeSpecs.driver.Violation import *
import re
import linecache


class MacroDefinitionSingletonRuleListener(ObjectiveCParserListener):

	def __init__(self, violation):
		super(MacroDefinitionSingletonRuleListener,self).__init__()
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
		violInfo.set_rulecategory("单例写法")
		# codeStr = linecache.getline(path,self.startline)
		# print "source code:" + codeStr
		violInfo.message = "请使用DEF_SINGLETON来定义单例"
		# "方法定义 " + codeStr + " 返回值的类型应为instancetype"
		#"Conforming to regular expressions:" + "\"" + self.regex + "\"" 

		democode = "@implementation MttPatchDataManager\n\
DEF_SINGLETON(MttPatchDataManager)\n\
...\n\
@end"
		violInfo.set_democode(democode)
		noncompliant = "+ (instancetype)sharedSettings\n\
{\n\
    static CBAppSettings *settings = nil;\n\
    static dispatch_once_t onceToken;\n\
    dispatch_once(&onceToken, ^{\n\
        settings = [[CBAppSettings alloc]init];\n\
    });\n\
    return settings;\n\
}"
		violInfo.set_noncompliant_code(noncompliant)
		violationDataMananger.addViolation(violInfo)

	def enterImplementationDefinitionList(self, ctx):


		classDefList = ctx.classMethodDefinition()
		for classDef in classDefList:
			# print "methodDefinition:" + classDef.methodDefinition().getText()
			methodSel = classDef.methodDefinition().methodSelector()

			selectorStr = methodSel.getText()
			# print methodSel.getText()
			if selectorStr.startswith("share"):
				token = methodSel.start
				startline = token.line
				startcolumn = token.column
				

				methodText = classDef.methodDefinition().getText()
				contentlist = re.findall(r"dispatch_once(.+?)\);", methodText)
				# print contentlist
				for content in contentlist:
					# print "content:" + content
					if len(content) > 0:
						if "alloc]init" in content or "new]" in content:
							self.send_violation(startline, startcolumn)
							break
				

				


