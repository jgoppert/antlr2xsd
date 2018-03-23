"""
Convert parsed dictionary to XSD
"""

from lxml import etree
from math import inf
from . import g4_ast as g4


def new_elem(namespace, type_name, *args, **kwargs) -> etree._Element:
    tag = '{{{:s}}}{:s}'.format(namespace, type_name)
    return etree.Element('{{{:s}}}{:s}'.format(namespace, type_name), *args, **kwargs)


E = etree
XS = "http://www.w3.org/2001/XMLSchema"
TNS = 'http://www.pymoca.com/Pymoca'
E.register_namespace('xs', XS)
E.register_namespace('tns', TNS)


class XsdListener(g4.TreeListener):

    def __init__(self):
        super().__init__()
        root = new_elem(XS, 'schema', targetNamespace=TNS, xmlns=TNS, elementFormDefault="qualified")
        root.append(new_elem(XS, 'element', name='modelica', type='stored_definition'))
        self.root = root
        self.scope = {
            'type': [],
            'seq': [],
        }

    def enterType(self, tree: g4.Type):
        type = new_elem(XS, 'complexType', name=tree.name)
        seq = new_elem(XS, 'sequence')
        type.append(seq)

        self.root.append(type)

        self.scope['type'].append(type)
        self.scope['seq'].append(seq)

    def exitType(self, tree: g4.Type):
        self.scope['type'].pop()
        self.scope['seq'].pop()

    def exitTypeRef(self, tree: g4.TypeRef):
        elem = new_elem(XS, 'element',
                        name=tree.name,
                        type=tree.name)
        v_min = str(tree.min_occurs)
        v_max = str(tree.max_occurs)
        if v_max == 'inf':
            v_max = 'unbounded'
        if v_min != '1':
            elem.attrib['minOccurs'] = v_min
        if v_max != '1':
            elem.attrib['maxOccurs'] = v_max
        self.scope['seq'][-1].append(elem)


def generate(tree: g4.Root) -> etree.ElementTree:
    """
    Takes an AST from parse_g4 and
    convert it to an XSD
    """
    listener = XsdListener()
    walker = g4.TreeWalker()
    walker.walk(listener, tree)
    return listener.root
