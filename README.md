# antlr2xsd
Converts ANTLR g4 gramar to XSD (XML schemas)

This project is useful for when you are mapping an ANTLR defined language to XML. The overall motivation of this project is to create an XML representation of the AST (abstract syntax tree) for the [Pymoca](www.pymoca.com) Modelica compiler, but others may also find it useful.

See the [test](test/test.py) for Modelica that converts a [Modelica.g4](test/g4/Modelica.g4) file to an [Pymoca.xsd](test/output/Pymoca.xsd) file.

There are already some handwritten Modelica XSD schemas [ModelicaXML](https://github.com/modelica-association/ModelicaXML), but they don't closely map to the source tree, and for Pymoca, we want to be able to define an XSD for our AST for each step of compilation of the Modelica language from the raw source to the differential algebraic equation representation. So knowing that our XSD directly maps to the grammar is important. Writing XML schemas is also a long an tedious process and there are some design choices involved (e.g. choice vs. polymorphism) that you might want to change at a later date. Compiling the XSD from the grammar makes this process fast and flexible.

Note: In order to make ANTLR preview work well with PyCharm, LexAdaptor.py is disabled for the antlrg4 grammar. The consequence is that you must just pass the parse rules of your g4 file for now. This doesn't negatively effect the parsing, since we are just paring the g4 parser rules, so we don't care about the lexer. Things like STRING etc, will just be mapped to user defined types.

### Roadmap
* [x] Read grammar rules and count multiplicity of rule references
* [ ] For alternatives in rules, if labelled, make a new type. If not labelled, add choices.
* [ ] Ignore non-optional tokens (e.g. '=' in equation), but keep optional tokens (e.g. 'fixed'), since they hold information if present or not.
* [ ] Convert types without rule references to simple types.
* [ ] Handle how to map lexer tokens to XSD types, user passed dict?
