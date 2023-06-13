from enum import Enum

class TokenType(Enum):
    KEYWORD = 1
    SYMBOL = 2
    IDENTIFIER = 3
    INT_CONST = 4
    STRING_CONST = 5

class ProcessingTokenStatus(Enum):
    NONE = 0
    IN_QUOTE = 1
    IN_SHORT_COMMENT = 2
    IN_LONG_COMMENT = 3

class Keyword(Enum):
    CLASS = 1
    METHOD = 2
    FUNCTION = 3
    CONSTRUCTOR = 4
    INT = 5
    BOOLEAN = 6
    CHAR = 7
    VOID = 8
    VAR = 9
    STATIC = 10
    FIELD = 11
    LET = 12
    DO = 13
    IF = 14
    ELSE = 15
    WHILE = 16
    RETURN = 17
    TRUE = 18
    FALSE = 19
    NULL = 20
    THIS = 21

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