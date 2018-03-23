"""
Converts ANTLR g4 gramamr files into xml XSD schemas.
"""
import os
import sys
from math import inf

import antlr4

sys.path.append(os.path.pardir)
from antlr2xsd.generated.ANTLRv4Lexer import ANTLRv4Lexer  # noqa: E402, I100
from antlr2xsd.generated.ANTLRv4Parser import ANTLRv4Parser  # noqa: E402
from antlr2xsd.generated.ANTLRv4ParserListener import ANTLRv4ParserListener  # noqa: E402
from . import g4_ast as g4


class Listener(ANTLRv4ParserListener):
    """
    Parses g4 file into an AST
    with info for XSD
    """

    def __init__(self):
        self.scope = {
            'root': None,
            'rule': []
        }
        self.min_max_scope = []
        self.src = {}

    def enterGrammarSpec(self, ctx: ANTLRv4Parser.GrammarSpecContext):
        elem = g4.Root()
        self.scope['root'] = elem
        self.src[ctx] = elem

    def enterParserRuleSpec(self, ctx: ANTLRv4Parser.ParserRuleSpecContext):
        elem = g4.Rule(name=str(ctx.RULE_REF()))
        self.scope['rule'].append(elem)
        self.src[ctx] = elem

    def exitParserRuleSpec(self, ctx: ANTLRv4Parser.RuleSpecContext):
        self.scope['root'].rules.append(self.scope['rule'].pop())

    @staticmethod
    def handle_suffix(rule: g4.Rule, suffix: str):
        for ref in rule.refs:
            if suffix == "?":
                rule.refs[ref].min_occurs = 0
            elif suffix == "+":
                rule.refs[ref].min_occurs += 1
                rule.refs[ref].max_occurs = inf
            elif suffix == "*":
                rule.refs[ref].min_occurs *= 0
                rule.refs[ref].max_occurs *= inf

    def exitElement(self, ctx:ANTLRv4Parser.ElementContext):
        if ctx.ebnfSuffix() is not None:
            suffix = self.src[ctx.ebnfSuffix()]
            rule = self.scope['rule'][-1]
            self.handle_suffix(rule, suffix)

    def exitEbnf(self, ctx: ANTLRv4Parser.EbnfContext):
        if ctx.blockSuffix() is not None:
            suffix = self.src[ctx.blockSuffix()]
            rule = self.scope['rule'][-1]
            self.handle_suffix(rule, suffix)

    def exitBlockSuffix(self, ctx: ANTLRv4Parser.BlockSuffixContext):
        self.src[ctx] = self.src[ctx.ebnfSuffix()]

    def exitEbnfSuffix(self, ctx: ANTLRv4Parser.EbnfSuffixContext):
        self.src[ctx] = ctx.getText()

    def exitRuleref(self, ctx: ANTLRv4Parser.RulerefContext):
        rule = self.scope['rule'][-1]
        ref = str(ctx.RULE_REF())
        if ref not in rule.refs:
            rule.refs[ref] = g4.RuleRef(min_occurs=0, max_occurs=0)
        rule.refs[ref].min_occurs += 1
        rule.refs[ref].max_occurs += 1

    def enterLabeledAlt(self, ctx: ANTLRv4Parser.LabeledAltContext):
        if ctx.identifier() is not None:
            self.scope['rule'].append(g4.Rule('unknown'))

    def exitLabeledAlt(self, ctx: ANTLRv4Parser.LabeledAltContext):
        if ctx.identifier() is not None:
            rule_name = self.src[ctx.identifier()]
            self.scope['rule'][-1].name = rule_name
            self.scope['root'].rules.append(self.scope['rule'].pop())

    def exitIdentifier(self, ctx: ANTLRv4Parser.IdentifierContext):
        self.src[ctx] = ctx.getText()

    def exitRuleAltList(self, ctx: ANTLRv4Parser.RuleAltListContext):
        # TODO add choice
        # print(len(ctx.labeledAlt()))
        self.src[ctx] = g4.Choice()


def parse(g4_path):
    """
    Parse a g4 file and return an AST for XSD
    """
    input_stream = antlr4.FileStream(g4_path)
    lexer = ANTLRv4Lexer(input_stream)
    stream = antlr4.CommonTokenStream(lexer)
    parser = ANTLRv4Parser(stream)
    parse_tree = parser.grammarSpec()
    listener = Listener()
    parse_walker = antlr4.ParseTreeWalker()
    parse_walker.walk(listener, parse_tree)
    data = listener.src[parse_tree]
    return data
