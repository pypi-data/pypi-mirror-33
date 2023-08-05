#
# Copyright (c) 2012-2017 The ANTLR Project. All rights reserved.
# Use of this file is governed by the BSD 3-clause license that
# can be found in the LICENSE.txt file in the project root.
#


# A set of utility routines useful for all kinds of ANTLR trees.#
from io import StringIO
import QBCodeSpecs.antlr4
from QBCodeSpecs.antlr4.atn.ATN import ATN
from QBCodeSpecs.antlr4.Token import Token
from QBCodeSpecs.antlr4.Utils import escapeWhitespace
from QBCodeSpecs.antlr4.tree.Tree import RuleNode, ErrorNode, TerminalNode

class Trees(object):

    # Print out a whole tree in LISP form. {@link #getNodeText} is used on the
    #  node payloads to get the text for the nodes.  Detect
    #  parse trees and extract data appropriately.
    @classmethod
    def toStringTree(cls, t, ruleNames=None, recog=None, index = 0):
        if recog is not None:
            ruleNames = recog.ruleNames
        s = escapeWhitespace(cls.getNodeText(t, ruleNames), False)
        if t.getChildCount()==0:
            return s
        with StringIO() as buf:
            buf.write(u"\n")

            tab_num = index
            while tab_num > 0:
                buf.write(u"    ")
                tab_num = tab_num - 1

            buf.write(u"(")
            buf.write(s)
            buf.write(u' ')
            for i in range(0, t.getChildCount()):
                if i > 0:
                    buf.write(u' ')
                next_index = index + 1
                buf.write(cls.toStringTree(t.getChild(i), ruleNames, recog=None, index=next_index))
            buf.write(u")")
            return buf.getvalue()

    @classmethod
    def getNodeText(cls, t, ruleNames=None, recog=None):
        if recog is not None:
            ruleNames = recog.ruleNames
        if ruleNames is not None:
            if isinstance(t, RuleNode):
                if t.getAltNumber()!=ATN.INVALID_ALT_NUMBER:
                    return ruleNames[t.getRuleIndex()]+":"+str(t.getAltNumber())
                return ruleNames[t.getRuleIndex()]
            elif isinstance( t, ErrorNode):
                return unicode(t)
            elif isinstance(t, TerminalNode):
                if t.symbol is not None:
                    return t.symbol.text
        # no recog for rule names
        payload = t.getPayload()
        if isinstance(payload, Token ):
            return payload.text
        return unicode(t.getPayload())


    # Return ordered list of all children of this node
    @classmethod
    def getChildren(cls, t):
        return [ t.getChild(i) for i in range(0, t.getChildCount()) ]

    # Return a list of all ancestors of this node.  The first node of
    #  list is the root and the last is the parent of this node.
    #
    @classmethod
    def getAncestors(cls, t):
        ancestors = []
        t = t.getParent()
        while t is not None:
            ancestors.append(0, t) # insert at start
            t = t.getParent()
        return ancestors

    @classmethod
    def findAllTokenNodes(cls, t, ttype):
        return cls.findAllNodes(t, ttype, True)

    @classmethod
    def findAllRuleNodes(cls, t, ruleIndex):
        return cls.findAllNodes(t, ruleIndex, False)

    @classmethod
    def findAllNodes(cls, t, index, findTokens):
        nodes = []
        cls._findAllNodes(t, index, findTokens, nodes)
        return nodes

    @classmethod
    def _findAllNodes(cls, t, index, findTokens, nodes):
        from QBCodeSpecs.antlr4.ParserRuleContext import ParserRuleContext
        # check this node (the root) first
        if findTokens and isinstance(t, TerminalNode):
            if t.symbol.type==index:
                nodes.append(t)
        elif not findTokens and isinstance(t, ParserRuleContext):
            if t.ruleIndex == index:
                nodes.append(t)
        # check children
        for i in range(0, t.getChildCount()):
            cls._findAllNodes(t.getChild(i), index, findTokens, nodes)

    @classmethod
    def descendants(cls, t):
        nodes = [t]
        for i in range(0, t.getChildCount()):
            nodes.extend(cls.descendants(t.getChild(i)))
        return nodes
