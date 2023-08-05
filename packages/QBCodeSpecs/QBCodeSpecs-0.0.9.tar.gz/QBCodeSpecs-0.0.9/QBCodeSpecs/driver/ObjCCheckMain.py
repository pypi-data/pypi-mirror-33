#!/usr/bin/env python
# -coding:utf-8
import sys
from QBCodeSpecs.antlr4 import *
from QBCodeSpecs.objcRecoginition.ObjectiveCLexer import *
from QBCodeSpecs.objcRecoginition.ObjectiveCParser import *

from QBCodeSpecs.driver.ViolationDataMananger import *
from QBCodeSpecs.driver.Violation import *

from QBCodeSpecs.reporters.HTMLReporter import *
import QBCodeSpecs
import json
import os
import re
import click

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class ObjCCheckMain(object):
    
    def load_config(self, configpath):
        try:
            # 用户配置的config, 大部分在工程目录中
            with open(configpath,'r') as load_f:
                load_dict = json.load(load_f)
                self.config = load_dict
        except Exception, e:
            # 运行环境下的config
            configPath = "config/config.json"
            path = os.path.dirname(QBCodeSpecs.__file__)
            exploit_path=os.path.join(path,configPath)
            # sys.path.append(exploit_path)

            with open(exploit_path,'r') as load_f:
                load_dict = json.load(load_f)
                self.config = load_dict


    def __init__(self, filepathlist = [], config=None):
       
        super(ObjCCheckMain, self).__init__()
        self.filepathlist = filepathlist
        self.basepath = ""
        self.config = {}
        self.valid_class = {}

        self.load_config(config)
        self.valid_rule_listener_class()
        # print len(self.filepathlist)


#def walkerTree(stream, listener):
#    parser = ObjectiveCParser(stream)
#    tree = parser.translationUnit()
#    walker = ParseTreeWalker()
#    walker.walk(listener, tree)
    # print("LISP:")
    # print(tree.toStringTree(parser))
             
    def print_result(self):
        print "final results:--------------------------------"

        violations = violationDataMananger.list
        for x in violations:
            if isinstance(x, Violation):
                info = "filepath:" + x.path + " " + "line number:" + str(x.startline) + " "+ "columnNum:" + str(x.startcolumn) + " " + "Message:" + x.message + " " + "DemoCode:" + x.get_democode()
                print info
        return len(violations)

    def is_valid_rule(self, ruleclassname):
        
        rulename = self.ruleNameFormClassName(ruleclassname)
        
        if self.config.has_key('invalidRules'):

            invalidRules = self.config['invalidRules']
            if rulename in invalidRules:
                return False
        
        return True

    def ruleNameFormClassName(self, ruleclassname):
        if ruleclassname.endswith('RuleListener') == False:
            return ""

        rulenamelen = len(ruleclassname) - len('RuleListener')
        if rulenamelen == 0:
            return ""

        rulename = ruleclassname[0:rulenamelen]
        return rulename

    def ruleInfoOfDirctory(self, exploit_path):
        try:
            modules=[x for x in os.listdir(exploit_path) if os.path.isfile(os.path.join(exploit_path,x)) and os.path.splitext(x)[1]=='.py']
            for m in modules:
                # print 'm:--' + m
                if m!='__init__.py':
                    module_name=os.path.join(exploit_path,os.path.splitext(m)[0])
                    class_name = os.path.splitext(m)[0]



                    if self.is_valid_rule(class_name) :
                        module=__import__(os.path.splitext(m)[0])
                        ruleLinstenerCls=getattr(module,class_name)
                        self.valid_class[self.ruleNameFormClassName(class_name)] = ruleLinstenerCls
        except Exception, e:
            # print "ruleInfoOfDirctory:---"
            # print e
            pass
        


    def valid_rule_listener_class(self):
        # key: className value: Class

        # 默认规则
        validDir = ["name", "empty", "custom", "experience", "migrate", "size"]
        for rulesDir in validDir:
            rulepath = "rules/" + rulesDir

            # path=os.path.abspath('.')
            # print "path --" + path
            # print  sys.modules['QBCodeSpecs']
            path = os.path.dirname(QBCodeSpecs.__file__)
            # print path
            exploit_path=os.path.join(path,rulepath)
            sys.path.append(exploit_path)
            self.ruleInfoOfDirctory(exploit_path)

             
        # 用户自定义规则
        exploit_path = ''
        if self.config.has_key('customRuleFolder'):
            exploit_path = self.config['customRuleFolder']
        if len(exploit_path) > 0:
            # 需要将自定义规则文件夹添加到系统目录中
            sys.path.append(exploit_path)
            self.ruleInfoOfDirctory(exploit_path)
        
    def check_file(self, inputstream, filepath):

        lexer = ObjectiveCLexer(inputstream)
        stream = CommonTokenStream(lexer)
        parser = ObjectiveCParser(stream)
        tree = parser.translationUnit()
        walker = ParseTreeWalker()

        # load rules
        rules = {}
        if self.config.has_key('rules'):
            rules = self.config['rules']
        
        # print rules
        
        listenerClassDict = self.valid_class
        for (k,v) in  listenerClassDict.items(): 
            rulename = k
            listenerCls = v

            violation = None
            # has dict para
            if rules.has_key(rulename) :
                para = rules[rulename]
                violation = Violation(filepath, para)
            else:
                violation = Violation(filepath)
            listener = listenerCls(violation)
            walker.walk(listener, tree)


    def isIgnorePath(self, path):
        if len(path) == 0:
            return True

        if self.config.has_key('ignorePath') :
            ignorePath = self.config['ignorePath']
            for iPathRegex in ignorePath:
                # print "-----iPathRegex:" + iPathRegex
                # print "path:" + path
                if re.match(iPathRegex, path) :
                    return True
        return False

    def start_check(self):

        total_files = 0

        for filepath in self.filepathlist:

            if self.isIgnorePath(filepath) :
                continue

            absolute_path = ""
            if len(self.basepath) > 0:
                absolute_path = self.basepath + "/" + filepath
            else:
                absolute_path = filepath


            inputstream = None
            try:
                inputstream = FileStream(absolute_path, encoding='utf-8')
                # input = FileStream(filepath)
                print "open file--------------------------------"
                print "filepath:" + filepath
            except IOError:
                print "IOError**********************************"
                print "basepath:" + self.basepath
                print "filepath:" + filepath
                continue
            else:
                pass
            finally:
                pass

            if input == None:
                continue
            # print input

            # record total_files
            total_files = total_files + 1
            self.check_file(inputstream, absolute_path)
            
        if total_files == 0 :
            print "--------------no error---------------"
            return
        else :
            print "--------------check end---------------"
        violationDataMananger.set_total_files_number(total_files)
        violationDataMananger.summary()
        # self.print_result()

        reporter = HTMLReporter()
        reporter.report('QBCodeToolsResult.html')

        error_num = len(violationDataMananger.list)
        return error_num
        
        # print "return info: " + str(len(violationDataMananger.list))
        # return len(violationDataMananger.list)

@click.command()
@click.option('-i', default=None, help='待检测的文件路径，多个文件使用\';\'分割')
@click.option('-config', default=None, help='配置文件路径')
def enter(i=None, config=None):

    if i is None or len(i) == 0:
        sys.exit(0)

    base_path = ""
    
    fileNamesString = i
    filenamelist = fileNamesString.split(';')
    checker = ObjCCheckMain(filepathlist=filenamelist, config=config)
    
    error_num = checker.start_check()
    if error_num > 0:
        return sys.exit(1)
    else:
        return sys.exit(0)


# def main(argv=None):
#     # fileNamesString = sys.argv[1]
#     if argv is None:
#         argv = sys.argv

#     if len(argv) < 2:
#         return 0
          
#     fileNamesString = argv[1]
#     base_path = ""
#     if len(argv) > 2:
#         base_path = argv[2]
    
#     # print "fileNamesString--------"
#     # print fileNamesString
#     filenamelist = fileNamesString.split(';')
#     checker = ObjCCheckMain(filepathlist=filenamelist, basepath=base_path)
#     error_num = checker.start_check()
#     # if error_num > 0:
#     #     return 1
#     # else:
#     #     return 0
#     if error_num > 0:
#         return sys.exit(1)
#     else:
#         return sys.exit(0)


if __name__ == '__main__':
    # main()
    enter()
    # sys.exit(main())
