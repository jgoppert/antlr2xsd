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
        listener_opts = {
            'root_name': 'modelica',
            'root_type': 'stored_definition',
            'tns': 'http://www.pymoca.com/Pymoca',
        }
        xsd = antlr2xsd.g4_parser.parse(
            os.path.join(TEST_DIR, 'g4', 'Modelica.g4'),
            listener_opts
        )
        xsd_str = etree.tostring(xsd, pretty_print=True).decode('utf-8')
        with open(os.path.join(TEST_DIR, 'output', 'Pymoca.xsd'), 'w') as f:
            f.write(xsd_str)
