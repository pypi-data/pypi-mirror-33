#!/usr/bin/env python
# -coding:utf-8
import sys
from QBCodeSpecs.objcRecoginition.ObjectiveCParserListener import *
from QBCodeSpecs.driver.ViolationDataMananger import *
from QBCodeSpecs.driver.Violation import *
import re
import linecache


class WeakDelegateRuleListener(ObjectiveCParserListener):

	def __init__(self, violation):
		super(WeakDelegateRuleListener,self).__init__()
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
		violInfo.set_priority("1")
		violInfo.set_rulecategory("Delegate属性定义")
		codeStr = linecache.getline(path,self.startline)
		# print "source code:" + codeStr
		violInfo.message = "delegate的属性使用retain来修饰可能存在循环引用"
		#"Conforming to regular expressions:" + "\"" + self.regex + "\"" 

		democode = "@property (nonatomic, weak) id&lt;ObjcDelegate&gt; delegate;"
		violInfo.set_democode(democode)
		noncompliant = "@property (nonatomic, retain) id&lt;ObjcDelegate&gt; delegate;"
		violInfo.set_noncompliant_code(noncompliant)
		violationDataMananger.addViolation(violInfo)

	def exitPropertyDeclaration(self, ctx):
		hasRetainAttribute = False
		# 包含<Delegate>
		hasDelegateFlag = False
		# hasDelegateDeclarator = False
		startline = 0
		startcolumn = 0

		# 属性
		attributesList = ctx.propertyAttributesList().propertyAttribute()
		for x in attributesList:
			# print "attribute:--" + x.getText()
			if "retain" in x.getText():
				hasRetainAttribute = True

		# 类型
		declaration = ctx.fieldDeclaration()
		qualifierList = declaration.specifierQualifierList().typeSpecifier()
		for x in qualifierList:
			# print "typeSpecifier:--" + x.getText()
			qualifierStr = x.getText()
			typeStr = re.findall(r"<(.+?)>", qualifierStr)
			for y in typeStr:
				# print "re--"+y
				if "delegate" in y or "Delegate" in y:
					# print "in hasDelegateFlag"
					token = x.start
					startline = token.line
					startcolumn = token.column
					hasDelegateFlag = True
			
			

		# 变量
		# declaratorList = declaration.fieldDeclaratorList().fieldDeclarator()
		# for x in declaratorList:
		# 	print "fieldDeclarator:--" + x.getText()
		# 	if "delegate" in x.getText() or "Delegate" in x.getText():
		# 		hasDelegateDeclarator = True

		if hasRetainAttribute and hasDelegateFlag:
			self.send_violation(startline, startcolumn)
			# print "retain delegate"



