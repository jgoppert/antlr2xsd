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
            'rule': None,
            'ebnf': []
        }
        self.min_max_scope = []
        self.src = {}

    def enterGrammarSpec(self, ctx: ANTLRv4Parser.GrammarSpecContext):
        elem = g4.Root()
        self.scope['root'] = elem
        self.src[ctx] = elem

    def enterParserRuleSpec(self, ctx: ANTLRv4Parser.ParserRuleSpecContext):
        elem = g4.Rule(name=str(ctx.RULE_REF()))
        self.scope['ebnf'].append({})
        self.scope['rule'] = elem
        self.src[ctx] = elem

    def exitParserRuleSpec(self, ctx: ANTLRv4Parser.RuleSpecContext):
        self.scope['rule'].refs.update(self.scope['ebnf'].pop())
        self.scope['root'].rules.append(self.scope['rule'])

    def enterEbnf(self, ctx: ANTLRv4Parser.EbnfContext):
        self.scope['ebnf'].append({})

    def exitEbnf(self, ctx: ANTLRv4Parser.EbnfContext):
        if ctx.blockSuffix() is not None:
            suffix = self.src[ctx.blockSuffix()]
            refs = self.scope['ebnf'][-1]
            if suffix == "?":
                for ref in refs:
                    refs[ref].min_occurs = 0
            elif suffix == "+":
                for ref in refs:
                    refs[ref].min_occurs += 1
                    refs[ref].max_occurs = inf
            elif suffix == "*":
                for ref in refs:
                    refs[ref].min_occurs *= 0
                    refs[ref].max_occurs *= inf
        inner = self.scope['ebnf'].pop()
        outer = self.scope['ebnf'][-1]
        for k in inner.keys():
            if k not in outer.keys():
                outer[k] = g4.RuleRef(min_occurs=0, max_occurs=0)
            outer[k].min_occurs += inner[k].min_occurs
            outer[k].max_occurs += inner[k].max_occurs

    def exitBlockSuffix(self, ctx: ANTLRv4Parser.BlockSuffixContext):
        self.src[ctx] = self.src[ctx.ebnfSuffix()]

    def exitEbnfSuffix(self, ctx: ANTLRv4Parser.EbnfSuffixContext):
        self.src[ctx] = ctx.getText()

    def exitRuleref(self, ctx: ANTLRv4Parser.RulerefContext):
        refs = self.scope['ebnf'][-1]
        rule_ref = str(ctx.RULE_REF())
        if rule_ref not in refs:
            refs[rule_ref] = g4.RuleRef(min_occurs=0, max_occurs=0)
        refs[rule_ref].min_occurs += 1
        refs[rule_ref].max_occurs += 1

    def enterLabeledAlt(self, ctx: ANTLRv4Parser.LabeledAltContext):
        if ctx.identifier() is not None:
            self.scope['ebnf'].append({})

    def exitLabeledAlt(self, ctx: ANTLRv4Parser.LabeledAltContext):
        if ctx.identifier() is not None:
            rule_name = self.src[ctx.identifier()]
            rule = g4.Rule(name=rule_name)
            rule.refs.update(self.scope['ebnf'].pop())
            self.scope['root'].rules.append(rule)

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
