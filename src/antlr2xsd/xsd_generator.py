"""
Convert parsed dictionary to XSD
"""

from lxml import etree


def generate(data: dict) -> etree.ElementTree:
    """
    Takes a data dict from parse_g4 and
    convert it to an XSD
    """
    E = etree

    # namespaces
    nsmap = {
        None: 'http://www.w3.org/2001/XMLSchema',
        'tns': 'http://www.pymoca.com/Pymoca'
    }
    root = E.Element('schema', nsmap=nsmap, targetNamespace='http://www.pymoca.com/Pymoca')  # type: etree._Element
    #< schema
    #xmlns = "http://www.w3.org/2001/XMLSchema"
    #targetNamespace = "http://www.example.com/SpaceWarGame"
    #xmlns: tns = "http://www.example.com/SpaceWarGame" >


    # root element
    root.append(E.Element('element', name='modelica', type='tns:stored_definition'))

    # types
    for rule in data['rules']:
        rule_type = E.Element(
            'complexType',
            name=rule['name'])  # type: etree._Element
        seq = E.Element('sequence')
        rule_type.append(seq)
        for ref_name, ref in rule['refs'].items():
            elem = E.Element('element',
                             name=ref_name,
                             type='tns:' + ref_name)
            if ref['min'] != '1':
                elem.attrib['minOccurs'] = ref['min']
            if ref['max'] != '1':
                elem.attrib['maxOccurs'] = ref['max']
            seq.append(elem)
        root.append(rule_type)
    return root
