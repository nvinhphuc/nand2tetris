from enum import Enum

class TokenType(Enum):
    KEYWORD = "keyword"
    SYMBOL = "symbol"
    IDENTIFIER = "identifier"
    INT_CONST = "integerConstant"
    STRING_CONST = "stringConstant"

class ProcessingTokenStatus(Enum):
    NONE = 0
    IN_QUOTE = 1
    IN_SHORT_COMMENT = 2
    IN_LONG_COMMENT = 3

class Keyword(Enum):
    CLASS = "class"
    METHOD = "method"
    FUNCTION = "function"
    CONSTRUCTOR = "constructor"
    INT = "int"
    BOOLEAN = "boolean"
    CHAR = "char"
    VOID = "void"
    VAR = "var"
    STATIC = "static"
    FIELD = "field"
    LET = "let"
    DO = "do"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    RETURN = "return"
    TRUE = "true"
    FALSE = "false"
    NULL = "null"
    THIS = "this"

KEYWORD_DICT = {
    "class": Keyword.CLASS,
    "method": Keyword.METHOD,
    "function": Keyword.FUNCTION,
    "constructor": Keyword.CONSTRUCTOR,
    "int": Keyword.INT,
    "boolean": Keyword.BOOLEAN,
    "char": Keyword.CHAR,
    "void": Keyword.VOID,
    "var": Keyword.VAR,
    "static": Keyword.STATIC,
    "field": Keyword.FIELD,
    "let": Keyword.LET,
    "do": Keyword.DO,
    "if": Keyword.IF,
    "else": Keyword.ELSE,
    "while": Keyword.WHILE,
    "return": Keyword.RETURN,
    "true": Keyword.TRUE,
    "false": Keyword.FALSE,
    "null": Keyword.NULL,
    "this": Keyword.THIS,
}

SYMBOL_SET = {"{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"}

DELIMITER_SYMBOL_SET = {" ", "\n", "\t"}