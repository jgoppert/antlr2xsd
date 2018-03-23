# antlr2xsd
Converts ANTLR g4 grammar to XSD for XML

This is primarily useful for when you are mapping an ANTLR defined language to XML. There may also be a generic AST creation backend eventually that takes the same data and creates sane python classes to hold the information that is parsed from ANTLR. Another alternative would be to use XML bindings to generate an AST after the XML is created, but this might note be flexible enough for my goal. The overall motivation of this project is to create an XML representation of the [Pymoca](www.pymoca.com) Modelica compiler, but others may also find it useful.

See [test](test/test.py) for Modelica that converts a [Modelica.g4](test/g4/Modelica.g4) file to an [Pymoca.xsd](test/output/Pymoca.xsd) file.

Note that to make ANTLR preview work well with pycharm, LexAdaptor is disabled. The consequence is that you must just pass the parse rules of your g4 file for now.

### Roadmap
* [x] Read grammar rules and count multiplicity of rule references
* [ ] For alternatives in rules, if labelled, make a new type. If not labelled, add choices.
* [ ] Ignore non-optional tokens (e.g. '=' in equation), but keep optional tokens (e.g. 'fixed'), since they hold information if present or not.
* [ ] Convert types without rule references to simple types.
* [ ] Handle how to map lexer tokens to XSD types, user passed dict?
