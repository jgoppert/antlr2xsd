/*
 * [The "BSD license"]
 *  Copyright (c) 2012-2014 Terence Parr
 *  Copyright (c) 2012-2014 Sam Harwell
 *  Copyright (c) 2015 Gerald Rosenberg
 *  All rights reserved.
 *
 *  Redistribution and use in source and binary forms, with or without
 *  modification, are permitted provided that the following conditions
 *  are met:
 *
 *  1. Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *  2. Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *  3. The name of the author may not be used to endorse or promote products
 *     derived from this software without specific prior written permission.
 *
 *  THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
 *  IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 *  OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 *  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
 *  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
 *  NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 *  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 *  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 *  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
 *  THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */
/*	A grammar for ANTLR v4 written in ANTLR v4.
 *
 *	Modified 2015.06.16 gbr
 *	-- update for compatibility with Antlr v4.5
 *	-- add mode for channels
 *	-- moved members to LexerAdaptor
 * 	-- move fragments to imports
 */

grammar ANTLRv4;

import LexBasic;

// The main entry point for parsing a v4 grammar.
grammarSpec
   : DOC_COMMENT* grammarType identifier ';' prequelConstruct* rules EOF
   ;

grammarType
   : 'grammar'
   ;

// This is the list of all constructs that can be declared before
// the set of rules that compose the grammar, and is invoked 0..n
// times by the grammarPrequel rule.
prequelConstruct
   : optionsSpec
   | delegateGrammars
   | tokensSpec
   | channelsSpec
   ;

// ------------
// Options - things that affect analysis and/or code generation
optionsSpec
   : 'options' '{' (option ';')* '}'
   ;

option
   : identifier '=' optionValue
   ;

optionValue
   : identifier ('.' identifier)*
   | STRING_LITERAL
   | INT
   ;

// ------------
// Delegates
delegateGrammars
   : 'import' delegateGrammar (',' delegateGrammar)* ';'
   ;

delegateGrammar
   : identifier '=' identifier
   | identifier
   ;

// ------------
// Tokens & Channels
tokensSpec
   : 'tokens' '{' idList? '}'
   ;

channelsSpec
   : 'channels' '{' idList? '}'
   ;

idList
   : identifier (',' identifier)* ','?
   ;

rules
   : ruleSpec*
   ;

ruleSpec
   : parserRuleSpec
   | lexerRuleSpec
   ;

parserRuleSpec
   : DOC_COMMENT* ruleModifiers? ID throwsSpec? rulePrequel* ':' ruleBlock ';'
   ;

rulePrequel
   : optionsSpec
   ;

// --------------
// Exception spec
throwsSpec
   : 'throws' identifier (',' identifier)*
   ;

ruleModifiers
   : ruleModifier +
   ;

// An individual access modifier for a rule. The 'fragment' modifier
// is an internal indication for lexer rules that they do not match
// from the input but are like subroutines for other lexer rules to
// reuse for certain lexical patterns. The other modifiers are passed
// to the code generation templates and may be ignored by the template
// if they are of no use in that language.
ruleModifier
   : 'public'
   | 'private'
   | 'protected'
   ;

ruleBlock
   : ruleAltList
   ;

ruleAltList
   : labeledAlt ('|' labeledAlt)*
   ;

labeledAlt
   : alternative ('#' identifier)?
   ;

// --------------------
// Lexer rules
lexerRuleSpec
   : DOC_COMMENT* 'fragment' ID ':' lexerRuleBlock ';'
   ;

lexerRuleBlock
   : lexerAltList
   ;

lexerAltList
   : lexerAlt ('|' lexerAlt)*
   ;

lexerAlt
   : lexerElements lexerCommands?
   |
   // explicitly allow empty alts
   ;

lexerElements
   : lexerElement +
   ;

lexerElement
   : labeledLexerElement ebnfSuffix?
   | lexerAtom ebnfSuffix?
   | lexerBlock ebnfSuffix?
   ;

// but preds can be anywhere
labeledLexerElement
   : identifier ('=' | '+=') (lexerAtom | lexerBlock)
   ;

lexerBlock
   : '(' lexerAltList ')'
   ;

// E.g., channel(HIDDEN), skip, more, mode(INSIDE), push(INSIDE), pop
lexerCommands
   : '->' lexerCommand (',' lexerCommand)*
   ;

lexerCommand
   : lexerCommandName '(' lexerCommandExpr ')'
   | lexerCommandName
   ;

lexerCommandName
   : identifier
   | 'mode'
   ;

lexerCommandExpr
   : identifier
   | INT
   ;

// --------------------
// Rule Alts
altList
   : alternative ('|' alternative)*
   ;

alternative
   : elementOptions? element +
   |
   // explicitly allow empty alts
   ;

element
   : labeledElement (ebnfSuffix |)
   | atom (ebnfSuffix |)
   | ebnf
   ;

labeledElement
   : identifier ('=' | '+=') (atom | block)
   ;

// --------------------
// EBNF and blocks
ebnf
   : block blockSuffix?
   ;

blockSuffix
   : ebnfSuffix
   ;

ebnfSuffix
   : '?' '?'?
   | '*' '?'?
   | '+' '?'?
   ;

lexerAtom
   : characterRange
   | terminal
   | notSet
   | LEXER_CHAR_SET
   | '.' elementOptions?
   ;

atom
   : terminal
   | ruleref
   | notSet
   | '.' elementOptions?
   ;

// --------------------
// Inverted element set
notSet
   : '~' setElement
   | '~' blockSet
   ;

blockSet
   : '(' setElement ('|' setElement)* ')'
   ;

setElement
   : ID elementOptions?
   | STRING_LITERAL elementOptions?
   | characterRange
   | LEXER_CHAR_SET
   ;

// -------------
// Grammar Block
block
   : '(' (optionsSpec? ':')? altList ')'
   ;

// ----------------
// Parser rule ref
ruleref
   : ID elementOptions?
   ;

// ---------------
// Character Range
characterRange
   : STRING_LITERAL '..' STRING_LITERAL
   ;

terminal
   : ID elementOptions?
   | STRING_LITERAL elementOptions?
   ;

// Terminals may be adorned with certain options when
// reference in the grammar: TOK<,,,>
elementOptions
   : '<' elementOption (',' elementOption)* '>'
   ;

elementOption
   : identifier
   | identifier '=' (identifier | STRING_LITERAL)
   ;

identifier
   : ID
   ;

// ======================================================
// Lexer specification
//
// -------------------------
// Comments

DOC_COMMENT
   : DocComment -> channel(HIDDEN)
   ;


BLOCK_COMMENT
   : BlockComment -> channel(HIDDEN)
   ;


LINE_COMMENT
   : LineComment -> channel (HIDDEN)
   ;

// -------------------------
// Integer
//

INT
   : DecimalNumeral
   ;

// -------------------------
// Literal string
//
// ANTLR makes no distinction between a single character literal and a
// multi-character string. All literals are single quote delimited and
// may contain unicode escape sequences of the form \uxxxx, where x
// is a valid hexadecimal number (per Unicode standard).

STRING_LITERAL
   : SQuoteLiteral
   ;


UNTERMINATED_STRING_LITERAL
   : USQuoteLiteral
   ;

// -------------------------
// Arguments
//
// Certain argument lists, such as those specifying call parameters
// to a rule invocation, or input parameters to a rule specification
// are contained within square brackets.

BEGIN_ARGUMENT
   : '['{ handleBeginArgument(); };

// -------------------------
// Actions

BEGIN_ACTION
   : '{'
   ;

// -------------------------
// Identifiers - allows unicode rule/token names

ID
   : NameStartChar (NameChar)*
   ;

WS  :  Ws -> channel(HIDDEN); // toss out whitespace

// -------------------------
// Illegal Characters
//
// This is an illegal character trap which is always the last rule in the
// lexer specification. It matches a single character of any value and being
// the last rule in the file will match when no other rule knows what to do
// about the character. It is reported as an error but is not passed on to the
// parser. This means that the parser to deal with the gramamr file anyway
// but we will not try to analyse or code generate from a file with lexical
// errors.
//
// Comment this rule out to allow the error to be propagated to the parser

ERRCHAR
   : . -> channel (HIDDEN)
   ;


// vi:ts=4:sw=4:expandtab:
