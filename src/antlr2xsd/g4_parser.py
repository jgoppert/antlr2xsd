"""
Converts ANTLR g4 grammar files into xml XSD schemas.
"""
import os
import sys
from math import inf

import antlr4

sys.path.append(os.path.pardir)
from antlr2xsd.generated.ANTLRv4Lexer import ANTLRv4Lexer  # noqa: E402, I100
from antlr2xsd.generated.ANTLRv4Parser import ANTLRv4Parser  # noqa: E402
from antlr2xsd.generated.ANTLRv4ParserListener import ANTLRv4ParserListener  # noqa: E402


from lxml import etree
from math import inf


def new_elem(namespace, type_name, *args, **kwargs) -> etree._Element:
    tag = '{{{:s}}}{:s}'.format(namespace, type_name)
    return etree.Element('{{{:s}}}{:s}'.format(namespace, type_name), *args, **kwargs)


E = etree
XS = "http://www.w3.org/2001/XMLSchema"
E.register_namespace('xs', XS)


class Scope:

    def __init__(self):
        self.stack = []

    def push(self, data):
        self.stack.append(data)

    def pop(self):
        return self.stack.pop()

    def get(self):
        assert len(self.stack) > 0
        return self.stack[-1]


class Listener(ANTLRv4ParserListener):
    """
    Parses g4 file into an AST
    with info for XSD
    """

    def __init__(self, listener_opts):
        self.root = None  # type: etree._Element
        self.scope = {
            'type': Scope(),
            'elem_list': Scope()
        }
        self.tns = listener_opts['tns']
        self.root_name = listener_opts['root_name']
        self.root_type = listener_opts['root_type']
        E.register_namespace('tns', self.tns)
        self.xsd = {}
        self.depth = 0

    #------------------------------------------------------------------------
    # Logging
    #------------------------------------------------------------------------

    def enterEveryRule(self, ctx: antlr4.ParserRuleContext):
        self.depth += 1

    def exitEveryRule(self, ctx: antlr4.ParserRuleContext):
        self.depth -= 1

    def log(self, *args, **kwargs):
        print(self.depth * '-', *args, **kwargs)


    #------------------------------------------------------------------------
    # GrammarSpec, maps to root of XSD
    #------------------------------------------------------------------------

    def enterGrammarSpec(self, ctx:ANTLRv4Parser.GrammarSpecContext):
        """
        Create xsd document and add root element.
        """
        print() # new line for logging
        root = new_elem(
            XS, 'schema', targetNamespace=self.tns,
            xmlns=self.tns, elementFormDefault="qualified")
        root.append(new_elem(
            XS, 'element', name=self.root_name, type=self.root_type))
        self.xsd[ctx] = root
        self.root = root

    #------------------------------------------------------------------------
    # ParserRuleSpec are the top level rules that map to ComplexType
    #------------------------------------------------------------------------

    def enterParserRuleSpec(self, ctx:ANTLRv4Parser.ParserRuleSpecContext):
        ctype = new_elem(XS, 'complexType', name=ctx.RULE_REF().getText())
        self.root.append(ctype)
        self.scope['type'].push(ctype)
        self.scope['elem_list'].push(new_elem(XS, 'sequence'))

    def exitParserRuleSpec(self, ctx:ANTLRv4Parser.ParserRuleSpecContext):
        self.scope['type'].get().append(self.scope['elem_list'].pop())
        self.scope['type'].pop()

    #------------------------------------------------------------------------
    # LabeledAlt maps to a new type if a name is given
    #------------------------------------------------------------------------

    def enterLabeledAlt(self, ctx:ANTLRv4Parser.LabeledAltContext):
        if ctx.identifier() is None:
            return
        ctype = new_elem(XS, 'complexType', name=ctx.identifier().getText())
        self.scope['type'].push(ctype)
        seq = new_elem(XS, 'sequence')
        self.scope['elem_list'].push(seq)

    def exitLabeledAlt(self, ctx:ANTLRv4Parser.LabeledAltContext):
        if ctx.identifier() is None:
            return
        self.scope['type'].get().append(self.scope['elem_list'].pop())
        self.root.append(self.scope['type'].pop())

        # add reference to newly created type
        type = ctx.identifier().getText()
        elem = new_elem(
            XS, 'element', name=type,
            type=type)
        self.scope['elem_list'].get().append(elem)

    #------------------------------------------------------------------------
    # RuleAltList/ AltList are lists of choices, and maps to an XSD choice
    #------------------------------------------------------------------------

    def enterRuleAltList(self, ctx:ANTLRv4Parser.RuleAltListContext):
        if len(ctx.labeledAlt()) > 1:
            choice = new_elem(XS, 'choice')
            self.scope['elem_list'].push(choice)

    def exitRuleAltList(self, ctx:ANTLRv4Parser.RuleAltListContext):
        if len(ctx.labeledAlt()) > 1:
            choice = self.scope['elem_list'].pop()
            self.scope['elem_list'].get().append(choice)

    def enterAltList(self, ctx:ANTLRv4Parser.AltListContext):
        if len(ctx.alternative()) > 1:
            choice = new_elem(XS, 'choice')
            self.scope['elem_list'].push(choice)

    def exitAltList(self, ctx:ANTLRv4Parser.AltListContext):
        if len(ctx.alternative()) > 1:
            choice = self.scope['elem_list'].pop()
            self.scope['elem_list'].get().append(choice)

    #------------------------------------------------------------------------
    # alternative is a list of elements and maps to XSD sequence
    #------------------------------------------------------------------------

    def enterAlternative(self, ctx:ANTLRv4Parser.AlternativeContext):
        if not self.scope['elem_list'].get().tag.split('}')[1] == 'sequence':
            seq = new_elem(XS, 'sequence')
            self.scope['elem_list'].push(seq)

    def exitAlternative(self, ctx:ANTLRv4Parser.AlternativeContext):
        if not self.scope['elem_list'].get().tag.split('}')[1] == 'sequence':
            seq = self.scope['elem_list'].pop()
            self.scope['elem_list'].get().append(seq)

    #------------------------------------------------------------------------
    # Atom (Ruleref/ terminal) map to an XSD element
    #------------------------------------------------------------------------

    def exitRuleref(self, ctx:ANTLRv4Parser.RulerefContext):
        name = str(ctx.getText()).replace("'", "")
        elem = new_elem(
            XS, 'element', name=name,
            type=ctx.getText())
        self.scope['elem_list'].get().append(elem)

    def exitTerminal(self, ctx:ANTLRv4Parser.TerminalContext):
        name = str(ctx.getText()).replace("'", "")
        # skip single characters (punctuation)
        if len(name) < 3:
            return
        elem = new_elem(
            XS, 'element', name=name,
            type='xs:string')
        self.scope['elem_list'].get().append(elem)

    #------------------------------------------------------------------------
    # Adjust multiplicity based on EBNF suffixes
    #------------------------------------------------------------------------

    def exitEbnfSuffix(self, ctx:ANTLRv4Parser.EbnfSuffixContext):
        pass

    def exitBlockSuffix(self, ctx:ANTLRv4Parser.BlockSuffixContext):
        pass


def parse(g4_path, listener_opts):
    """
    Parse a g4 file and return an AST for XSD
    """
    input_stream = antlr4.FileStream(g4_path)
    lexer = ANTLRv4Lexer(input_stream)
    stream = antlr4.CommonTokenStream(lexer)
    parser = ANTLRv4Parser(stream)
    parse_tree = parser.grammarSpec()
    listener = Listener(listener_opts)
    parse_walker = antlr4.ParseTreeWalker()
    parse_walker.walk(listener, parse_tree)
    data = listener.xsd[parse_tree]
    return data
