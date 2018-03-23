import os
import sys
from lxml import etree
import json
import unittest

import antlr2xsd

sys.path.append(os.path.pardir)

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


class TestXsd(unittest.TestCase):

    def test_to_xsd(self):
        data = antlr2xsd.g4_parser.parse(os.path.join(TEST_DIR, 'g4', 'Modelica.g4'))
        json_str = json.dumps(data, indent=2)
        with open(os.path.join(TEST_DIR, 'output', 'modelica.json'), 'w') as f:
            f.write(json_str)
        xsd = antlr2xsd.xsd_generator.generate(data)
        xsd_str = etree.tostring(xsd, pretty_print=True).decode('utf-8')
        with open(os.path.join(TEST_DIR, 'output', 'Pymoca.xsd'), 'w') as f:
            f.write(xsd_str)
