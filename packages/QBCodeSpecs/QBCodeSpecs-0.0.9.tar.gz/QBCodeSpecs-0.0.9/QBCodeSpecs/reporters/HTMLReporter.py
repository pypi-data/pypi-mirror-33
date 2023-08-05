#!/usr/bin/env python
# -coding:utf-8
import io
from QBCodeSpecs.driver.ViolationDataMananger import *
from QBCodeSpecs.driver.Violation import *

class HTMLReporter(object):
	"""docstring for HTMLReporter"""


	


	def __init__(self):
		super(HTMLReporter, self).__init__()


	def write_head(self, f):
		head_string = "<head> 				 \
        <title>QBCodeTools Report</title>	 \
        <meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" /> \
        <style type='text/css'>				 \
.priority1, .priority2, .priority3,          \
.cmplr-error, .cmplr-warning, .checker-bug { \
    font-weight: bold;                       \
    text-align: center;                      \
}                                            \
.priority1, .priority2, .priority3 {         \
    color: #BF0A30;                          \
}                                            \
.priority1 { background-color: #FFC200; }    \
.priority2 { background-color: #FFD3A6; }    \
.priority3 { background-color: #FFEEB5; }    \
.cmplr-error, .cmplr-warning {               \
    background-color: #BF0A30;               \
}                                            \
.cmplr-error { color: #FFC200; }             \
.cmplr-warning { color: #FFD3A6; }           \
.checker-bug {                               \
    background-color: #002868;               \
    color: white;                            \
}                                            \
table {                                      \
    border: 2px solid gray;                  \
    border-collapse: collapse;               \
    -moz-box-shadow: 3px 3px 4px #AAA;       \
    -webkit-box-shadow: 3px 3px 4px #AAA;    \
    box-shadow: 3px 3px 4px #AAA;            \
}                                            \
td, th {                                     \
    border: 1px solid #D3D3D3;               \
    padding: 4px 20px 4px 20px;              \
}                                            \
th {                                         \
    text-shadow: 2px 2px 2px white;          \
    border-bottom: 1px solid gray;           \
    background-color: #E9F4FF;               \
} </style></head>"
		
		try:
			f.write(head_string)
		except Exception, e:
			print "write_head error"
			raise e

	def write_summary_table(self, f):
		summary = ("<table><thead><tr><th>扫描文件数</th><th>违规文件数</th>" + "<th>优先级 1</th><th>优先级 2</th><th>优先级 3</th>"
		+ "</tr></thead>"
		+ "<tbody><tr><td>" + violationDataMananger.get_total_files_number() + "</td><td>"
		+ violationDataMananger.numberOfFilesWithViolations() + "</td><td class='priority1'>"
		+ violationDataMananger.numberOfViolationsWithPriority(1) + "</td><td class='priority2'>"
		+ violationDataMananger.numberOfViolationsWithPriority(2) + "</td><td class='priority3'>"
		+ violationDataMananger.numberOfViolationsWithPriority(3) + "</tr></tbody></table>")
		
		try:
			f.write(summary)
		except Exception, e:
			print "write_summary_table error"
			raise e

	def write_detail_table(self, f, violation):
		detail = ("<tr><td>" + violation.path + "</td><td>" + str(violation.startline) + ":" + str(violation.startcolumn) + "</td>" 
		# + "<td>" + violation.get_rulename() + "</td>"
		+ "<td>" + violation.get_rulecategory() + "</td>"
		+ "<td class='priority" + violation.get_priority() + "'>"
		+ violation.get_priority() + "</td>"
		+ "<td>" + violation.message + "</td>"
		# + "<td><pre>" + violation.currCode + "<pre></td>"
		+ "<td><pre><code class=\"html\">" + violation.get_noncompliant_code() + "</code><pre></td>"
		+ "<td><pre><code class=\"html\">" + violation.get_democode() + "</code><pre></td></tr>")
		
		try:
			f.write(detail)
		except Exception, e:
			print "write_detail_table error"
			raise e

	def write_code_highlight(self, f):
		highlight = ("<link rel=\"stylesheet\" href=\"./styles/xcode.css\">"
		+ "<script src=\"./styles/highlight.pack.js\"></script>"
		+ "<script>hljs.initHighlightingOnLoad();</script>")
		try:
			f.write(highlight)
		except Exception, e:
			print "write_code_highlight error"
			raise e


	def report(self, filepath = ''):
		# filepath = '/Users/paulineli/Desktop/result.html'
		with open(filepath, 'w') as f:
			f.write("<!DOCTYPE html>")
			f.write("<html>")

			self.write_head(f)
			self.write_code_highlight(f)

			f.write("<body>")
			f.write("<h1>QBCodeSpecsTools 扫描报告</h1>")
			f.write("<hr />")
			f.write("<h2>汇总</h2>")
			
			self.write_summary_table(f)

			f.write("<hr />")
			f.write("<h2>详情</h2>")
			html_text = ("<table><thead><tr><th>文件路径</th><th>出错位置 行号:列号</th>" 
			# + "<th>Rule Name</th><th>Rule Category</th>" 
			+ "<th>规则类型</th>" 
			+ "<th>优先级</th><th>错误信息</th>"
			# + "<th>当前写法</th>"
			+ "<th>不合规范实例</th><th>规范实例</th></tr></thead><tbody>")
			f.write(html_text)
        	
			violationlist = violationDataMananger.list
			for violation in violationlist:
				self.write_detail_table(f, violation)

			html_text = ("</tbody></table>" + "<hr />" + "</body>" + "</html>")
			f.write(html_text)




