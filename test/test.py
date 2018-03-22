import os
import sys
from math import inf
from lxml import etree
import json

import antlr2xsd

sys.path.append(os.path.pardir)

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


def test_to_xsd():
    data = antlr2xsd.parse_g4(os.path.join(TEST_DIR, 'Modelica.g4'))
    json_str = json.dumps(data, indent=2)
    with open(os.path.join(TEST_DIR, 'output', 'modelica.json'), 'w') as f:
        f.write(json_str)
    xsd = antlr2xsd.to_xsd(data)
    xsd_str = etree.tostring(xsd, pretty_print=True).decode('utf-8')
    with open(os.path.join(TEST_DIR, 'output', 'modelica.xsd'), 'w') as f:
        f.write(xsd_str)
