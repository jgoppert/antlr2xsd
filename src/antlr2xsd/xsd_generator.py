"""
Convert parsed dictionary to XSD
"""

from lxml import etree
from math import inf


def generate(data: dict) -> etree.ElementTree:
    """
    Takes a data dict from parse_g4 and
    convert it to an XSD
    """
    E = etree
    xs = "http://www.w3.org/2001/XMLSchema"
    tns = 'http://www.pymoca.com/Pymoca'
    E.register_namespace('xs', xs)
    E.register_namespace('tns', tns)

    def new_elem(namespace, type_name, *args, **kwargs) -> etree._Element:
        tag = '{{{:s}}}{:s}'.format(namespace, type_name)
        print('tag', tag)
        return etree.Element('{{{:s}}}{:s}'.format(namespace, type_name), *args, **kwargs)

    root = new_elem(xs, 'schema', targetNamespace=tns,  xmlns=tns, elementFormDefault="qualified")
    root.append(new_elem(xs, 'element', name='modelica', type='stored_definition'))

    # types
    for rule in data['rules']:
        rule_type = new_elem(xs, 'complexType', name=rule['name'])
        seq = new_elem(xs ,'sequence')
        rule_type.append(seq)
        for ref_name, ref in rule['refs'].items():
            elem = new_elem(xs, 'element',
                             name=ref_name,
                             type=ref_name)
            if ref['max'] == inf:
                ref['max'] = 'unbounded'
            if ref['min'] != 1:
                elem.attrib['minOccurs'] = str(ref['min'])
            if ref['max'] != 1:
                elem.attrib['maxOccurs'] = str(ref['max'])
            seq.append(elem)
        root.append(rule_type)
    return root
