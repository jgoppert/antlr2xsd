import os
import sys
from math import inf

import antlr4

from lxml import etree

# import json
sys.path.append(os.path.pardir)
from antlr2xsd.generated.ANTLRv4Lexer import ANTLRv4Lexer  # noqa: E402, I100
from antlr2xsd.generated.ANTLRv4Parser import ANTLRv4Parser  # noqa: E402
from antlr2xsd.generated.ANTLRv4ParserListener import ANTLRv4ParserListener  # noqa: E402


class Listener(ANTLRv4ParserListener):

    def __init__(self):
        self.scope = {
            'root': None,
            'rule': None,
            'ebnf': []
        }
        self.min_max_scope = []
        self.src = {}

    def enterGrammarSpec(self, ctx: ANTLRv4Parser.GrammarSpecContext):
        e = {
            'rules': []
        }
        self.scope['root'] = e
        self.src[ctx] = e

    def enterParserRuleSpec(self, ctx: ANTLRv4Parser.ParserRuleSpecContext):
        e = {
            'name': str(ctx.RULE_REF()),
            'refs': {}
        }
        self.scope['ebnf'].append({})
        self.scope['rule'] = e
        self.src[ctx] = e

    def exitParserRuleSpec(self, ctx: ANTLRv4Parser.RuleSpecContext):
        ebnf = self.scope['ebnf'][-1]
        for k in ebnf.keys():
            self.scope['rule']['refs'][k] = ebnf[k]
        self.scope['root']['rules'].append(self.scope['rule'])

    def enterEbnf(self, ctx: ANTLRv4Parser.EbnfContext):
        self.scope['ebnf'].append({})

    def exitEbnf(self, ctx: ANTLRv4Parser.EbnfContext):
        if ctx.blockSuffix() is not None:
            suffix = self.src[ctx.blockSuffix()]
            refs = self.scope['ebnf'][-1]
            if suffix == "?":
                for r in refs:
                    refs[r]['min'] = 0
            elif suffix == "+":
                for r in refs:
                    refs[r]['min'] += 1
                    refs[r]['max'] = inf
            elif suffix == "*":
                for r in refs:
                    refs[r]['min'] *= 0
                    refs[r]['max'] *= inf
        inner = self.scope['ebnf'].pop()
        outer = self.scope['ebnf'][-1]
        for k in inner.keys():
            if k not in outer.keys():
                outer[k] = {
                    'min': 0,
                    'max': 0
                }
            outer[k]['min'] += inner[k]['min']
            outer[k]['max'] += inner[k]['max']

    def exitBlockSuffix(self, ctx: ANTLRv4Parser.BlockSuffixContext):
        self.src[ctx] = self.src[ctx.ebnfSuffix()]

    def exitEbnfSuffix(self, ctx: ANTLRv4Parser.EbnfSuffixContext):
        self.src[ctx] = ctx.getText()

    def exitRuleref(self, ctx: ANTLRv4Parser.RulerefContext):
        refs = self.scope['ebnf'][-1]
        rule_ref = str(ctx.RULE_REF())
        if rule_ref not in refs:
            refs[rule_ref] = {
                'min': 0,
                'max': 0
            }
        refs[rule_ref] = {
            'min': refs[rule_ref]['min'] + 1,
            'max': refs[rule_ref]['max'] + 1
        }

    def exitRuleAltList(self, ctx: ANTLRv4Parser.RuleAltListContext):
        pass


def parse_g4(g4_path):
    input_stream = antlr4.FileStream(g4_path)
    lexer = ANTLRv4Lexer(input_stream)
    stream = antlr4.CommonTokenStream(lexer)
    parser = ANTLRv4Parser(stream)
    parse_tree = parser.grammarSpec()
    listener = Listener()
    parse_walker = antlr4.ParseTreeWalker()
    parse_walker.walk(listener, parse_tree)
    return listener.src[parse_tree]


def to_xsd(data):
    root = etree.Element('schema')
    for rule in data['rules']:
        type = etree.Element(
            'complex_type',
            name=rule['name'])  # type: etree._Element
        for ref_name, ref in rule['refs'].items():
            type.append(etree.Element('element', name=ref_name, type=ref_name))
            min = str(ref['min'])
            if ref['max'] == inf:
                max = 'unbounded'
            else:
                max = str(ref['max'])
            if min == '1' and max == '1':
                continue
            type.attrib['min_occurs'] = min
            type.attrib['max_occurs'] = max
        root.append(type)
    return root
