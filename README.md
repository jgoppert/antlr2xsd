# antlr2xsd
Converts ANTLR g4 grammar to XSD for XML

See [test](test/test.py) for Modelica that converts a [Modelica.g4](test/g4/Modelica.g4) file to an [Pymoca.xsd](test/output/Pymoca.xsd) file.

Note that to make ANTLR preview work well with pycharm, LexAdaptor is disabled. The consequence is that you must just pass the parse rules of your g4 file for now.
