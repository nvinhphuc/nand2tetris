import argparse
from models import TokenType, ProcessingTokenStatus, Keyword, KEYWORD_DICT, SYMBOL_SET, DELIMITER_SYMBOL_SET
from utils import is_number, to_xml_text
import xml.etree.ElementTree as ET

class Tokenizer:
    def __init__(self, source_file) -> None:
        self.source_file = source_file
        self.current_token = None
        self.token_queue = []
        self.token_status = ProcessingTokenStatus.NONE
        self.processing_token = ""
        self.current_line = ""

    def tokenize_a_line(self, line):
        idx = 0
        while idx < len(line):
            if self.token_status == ProcessingTokenStatus.NONE:
                if idx + 1 < len(line) and line[idx:idx+2] == "//":
                    self.token_status = ProcessingTokenStatus.IN_SHORT_COMMENT
                    idx += 2
                    continue
                elif idx + 2 < len(line) and line[idx:idx+3] == "/**":
                    self.token_status = ProcessingTokenStatus.IN_LONG_COMMENT
                    idx += 3
                    continue
                elif line[idx] in SYMBOL_SET:
                    if self.processing_token != "":
                        self.token_queue.append(self.processing_token)
                        self.processing_token = ""
                    self.token_queue.append(line[idx])
                elif line[idx] == '"':
                    self.processing_token += line[idx]
                    self.token_status = ProcessingTokenStatus.IN_QUOTE
                elif line[idx] in DELIMITER_SYMBOL_SET and self.processing_token != "":
                    self.token_queue.append(self.processing_token)
                    self.processing_token = ""
                elif line[idx] in DELIMITER_SYMBOL_SET and self.processing_token == "":
                    idx += 1
                    continue
                else:
                    self.processing_token += line[idx]
            elif self.token_status == ProcessingTokenStatus.IN_SHORT_COMMENT:
                if line[idx] == "\n":
                    self.token_status = ProcessingTokenStatus.NONE
            elif self.token_status == ProcessingTokenStatus.IN_LONG_COMMENT:
                if idx < len(line) - 1 and line[idx:idx+2] == "*/":
                    self.token_status = ProcessingTokenStatus.NONE
                    idx += 2
                    continue
            elif self.token_status == ProcessingTokenStatus.IN_QUOTE:
                if idx < len(line):
                    self.processing_token += line[idx]
                    if line[idx] == '"':
                        self.token_queue.append(self.processing_token)
                        self.processing_token = ""
                        self.token_status = ProcessingTokenStatus.NONE
                else:
                    raise SyntaxError("No closing quote at the end of line")
            idx += 1

    def has_more_tokens(self) -> bool:
        if (len(self.token_queue) > 0):
            return True
        else:
            current_line = self.source_file.readline()
            self.current_line = current_line
            if (current_line == ''):
                return False
            else:
                self.tokenize_a_line(current_line)
                return True
            
    def advance(self):
        if len(self.token_queue) > 0:
            self.current_token = self.token_queue.pop(0)
        else:
            self.current_token = None
        return self.current_token

    def token_type(self) -> TokenType:
        if KEYWORD_DICT.get(self.current_token) is not None:
            return TokenType.KEYWORD
        elif self.current_token in SYMBOL_SET:
            return TokenType.SYMBOL
        elif self.current_token[0] == '"':
            return TokenType.STRING_CONST
        elif is_number(self.current_token):
            return TokenType.INT_CONST
        else:
            if is_number(self.current_token[0]):
                raise SyntaxError("Identifier cannot begin with number")
            else:
                return TokenType.IDENTIFIER

    def keyword(self) -> Keyword:
        return KEYWORD_DICT[self.current_token]

    def symbol(self):
        return self.current_token

    def identifier(self):
        return self.current_token

    def int_val(self):
        return int(self.current_token)

    def string_val(self):
        # remove the opening and closing quotes
        return self.current_token[1:-1]



if __name__ == "__main__":
    # tokenizer = Tokenizer("a")
    # tokenizer.tokenize_a_line("// This file is part of www.nand2tetris.org")
    # print(tokenizer.token_queue)
    parser = argparse.ArgumentParser(description="Assembler")
    parser.add_argument("--source", type=str, help="Path to the source file")
    parser.add_argument("--dest", type=str, help="Path to the destination file")
    args = parser.parse_args()

    with open(args.source, "r") as source_file:
        with open(args.dest, "w") as xml_file:
            tokenizer = Tokenizer(source_file=source_file)
            xml_file.write("<tokens>\n")
            while (tokenizer.has_more_tokens()):
                current_token = tokenizer.advance()
                if current_token == None:
                    continue
                print(f"current_token: {current_token}")
                current_token_type = tokenizer.token_type()
                xml_token = to_xml_text(current_token)
                if (current_token_type == TokenType.KEYWORD):
                    xml_file.write(f"<keyword> {xml_token} </keyword>\n")
                elif (current_token_type == TokenType.SYMBOL):
                    xml_file.write(f"<symbol> {xml_token} </symbol>\n")
                elif (current_token_type == TokenType.IDENTIFIER):
                    xml_file.write(f"<identifier> {xml_token} </identifier>\n")
                elif (current_token_type == TokenType.INT_CONST):
                    xml_file.write(f"<integerConstant> {xml_token} </integerConstant>\n")
                elif (current_token_type == TokenType.STRING_CONST):
                    xml_file.write(f"<stringConstant> {to_xml_text(tokenizer.string_val())} </stringConstant>\n")
            
            xml_file.write("</tokens>\n")
