# antlr2xsd
Converts ANTLR g4 grammar to XSD for XML

See [test](test/test.py) for Modelica that converts a [Modelica.g4](test/g4/Modelica.g4) file to an [Pymoca.xsd](test/output/Pymoca.xsd) file.

Note that to make ANTLR preview work well with pycharm, LexAdaptor is disabled. The consequence is that you must just pass the parse rules of your g4 file for now.

### Roadmap
* [x] Read grammar rules and count multiplicity of rule references
* [ ] For alternatives in rules, if labelled, make a new type. If not labelled, add choices.
* [ ] Ignore non-optional tokens (e.g. '=' in equation), but keep optional tokens (e.g. 'fixed'), since they hold information if present or not.
* [ ] Convert types without rule references to simple types.
* [ ] Handle how to map lexer tokens to XSD types, user passed dict?
