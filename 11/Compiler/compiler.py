import argparse
import logging
from models import TokenType, Keyword
from tokenizer import Tokenizer
from utils import to_xml_text, gen_uuid4

def new_node(tag, text = None, children = None):
    if children == None:
        children = []
    return { "tag": tag, "text": text, "children": children }

class Compiler:
    previous_token = None
    is_looked_ahead = False
    def __init__(self, source_file, dest_file) -> None:
        self.tokenizer = Tokenizer(source_file)
        self.dest_file = dest_file
        self.parsed_tree = {}
        self.root_id = None

    def print_parsed_tree(self):
        for key in self.parsed_tree:
            if self.parsed_tree[key]["text"] == None: self.parsed_tree[key]["text"] = 'None'
            self.parsed_tree[key]["children"] = list(self.parsed_tree[key]["children"])
        print(self.parsed_tree)

    def __advance_and_do_compile(self, compile_function, parent = None, keywords = None, symbols = None):
        if (self.tokenizer.has_more_tokens()):
            self.previous_token = self.tokenizer.current_token
            self.tokenizer.advance()
            if keywords == None and symbols == None:
                compile_function(parent)
            elif keywords != None:
                compile_function(parent, keywords)
            elif symbols != None:
                compile_function(parent, symbols)
        else:
            raise SyntaxError("There are no tokens left")
    
    def compile_nothing(self, *args):
        pass
    
    def is_keyword_in(self, keywords):
        if self.tokenizer.token_type() != TokenType.KEYWORD: return False
        if self.tokenizer.keyword() not in keywords: return False
        return True
    
    def is_identifier(self):
        return self.tokenizer.token_type() == TokenType.IDENTIFIER
    
    def is_symbol_in(self, symbols):
        if self.tokenizer.token_type() != TokenType.SYMBOL: return False
        if self.tokenizer.symbol() not in symbols: return False
        return True
    
    def compile_var_name(self, parent):
        self.compile_if_is_identifier(parent)
    
    def compile_keyword(self, parent):
        keyword_id = gen_uuid4()
        self.parsed_tree[keyword_id] = new_node(
            tag=TokenType.KEYWORD.value,
            text=self.tokenizer.keyword().value
        )
        self.parsed_tree[parent]["children"].append(keyword_id)

    def compile_identifier(self, parent):
        identifier_id = gen_uuid4()
        self.parsed_tree[identifier_id] = new_node(
            tag=TokenType.IDENTIFIER.value,
            text=to_xml_text(self.tokenizer.identifier()),
        )
        self.parsed_tree[parent]["children"].append(identifier_id)

    def compile_int_const(self, parent):
        int_const_id = gen_uuid4()
        self.parsed_tree[int_const_id] = new_node(
            tag=TokenType.INT_CONST.value,
            text=to_xml_text(self.tokenizer.int_val()),
        )
        self.parsed_tree[parent]["children"].append(int_const_id)

    def compile_string_const(self, parent):
        string_const_id = gen_uuid4()
        self.parsed_tree[string_const_id] = new_node(
            tag=TokenType.STRING_CONST.value,
            text=to_xml_text(self.tokenizer.string_val()),
        )
        self.parsed_tree[parent]["children"].append(string_const_id)

    def compile_symbol(self, parent):
        symbol_id = gen_uuid4()
        self.parsed_tree[symbol_id] = new_node(
            tag=TokenType.SYMBOL.value,
            text=to_xml_text(self.tokenizer.symbol()),
        )
        self.parsed_tree[parent]["children"].append(symbol_id)

    def compile_if_is_keyword_in(self, parent, keywords):
        if self.is_keyword_in(keywords=keywords): self.compile_keyword(parent)
        else: raise SyntaxError

    def compile_if_is_symbol_in(self, parent, symbols):
        if self.is_symbol_in(symbols=symbols): self.compile_symbol(parent)
        else:
            logging.error(f"current token: {self.tokenizer.current_token}")
            self.print_parsed_tree()
            raise SyntaxError

    def compile_if_is_identifier(self, parent):
        if self.is_identifier(): self.compile_identifier(parent)
        else: raise SyntaxError

    def compile_class_keyword(self, parent):
        if self.is_keyword_in(keywords={Keyword.CLASS}): self.compile_keyword(parent=parent)
        else: raise SyntaxError('Keyword "class" expected.')
            
    def compile_class_name(self, parent):
        if self.is_identifier(): self.compile_identifier(parent=parent)
        else: raise SyntaxError('An identifier is expected here.')
            
    def compile_opening_bracket(self, parent):
        if self.is_symbol_in(symbols={"{"}): self.compile_symbol(parent=parent)
        else:
            logging.error(f"Received token: {self.tokenizer.current_token}")
            raise SyntaxError('Symbol "{" expected.')

    def compile_static_field(self, parent):
        if self.is_keyword_in(keywords={Keyword.STATIC, Keyword.FIELD}): self.compile_keyword(parent)
        else: raise SyntaxError

    def compile_type(self, parent):
        if self.is_keyword_in(keywords={Keyword.INT, Keyword.CHAR, Keyword.BOOLEAN}): self.compile_keyword(parent)
        elif (self.tokenizer.token_type() == TokenType.IDENTIFIER): self.compile_identifier(parent)
        else: raise SyntaxError

    def compile_class(self):
        class_root_id = "root"
        self.root_id = class_root_id
        self.parsed_tree[class_root_id] = new_node(tag="class")
        self.__advance_and_do_compile(self.compile_class_keyword, parent=class_root_id)
        self.__advance_and_do_compile(self.compile_class_name, parent=class_root_id)
        self.__advance_and_do_compile(self.compile_opening_bracket, parent=class_root_id)

        while (self.tokenizer.has_more_tokens()):
            self.tokenizer.advance()
            if self.is_keyword_in(keywords={Keyword.STATIC, Keyword.FIELD}):
                self.compile_class_var_dec(parent=class_root_id)
            elif self.is_keyword_in(keywords={Keyword.CONSTRUCTOR, Keyword.FUNCTION, Keyword.METHOD}):
                self.compile_subroutine(parent=class_root_id)
            elif self.is_symbol_in({"}"}):
                self.compile_symbol(parent=class_root_id)
                break
            else:
                self.print_parsed_tree()
                logging.error(f"current token: {self.tokenizer.current_token}")
                raise SyntaxError


    def compile_class_var_dec(self, parent):
        class_var_dec_root_id = gen_uuid4()
        self.parsed_tree[class_var_dec_root_id] = new_node(tag="classVarDec")
        self.parsed_tree[parent]["children"].append(class_var_dec_root_id)
        self.compile_static_field(parent=class_var_dec_root_id)
        self.__advance_and_do_compile(self.compile_type, parent=class_var_dec_root_id)
        self.__advance_and_do_compile(self.compile_var_name_list, parent=class_var_dec_root_id)
            
    def compile_var_name_list(self, parent):
        self.compile_var_name(parent=parent)
        while (self.tokenizer.has_more_tokens()):
            self.tokenizer.advance()
            if self.is_symbol_in({","}):
                self.compile_symbol(parent=parent)
                self.__advance_and_do_compile(self.compile_var_name, parent=parent)
            elif self.is_symbol_in({";"}):
                self.compile_symbol(parent=parent)
                break
            else:
                raise SyntaxError
            
    def compile_var_dec(self, parent):
        var_dec_id = gen_uuid4()
        self.parsed_tree[var_dec_id] = new_node(tag="varDec")
        self.parsed_tree[parent]["children"].append(var_dec_id)
        
        self.compile_if_is_keyword_in(parent=var_dec_id, keywords={Keyword.VAR})
        self.__advance_and_do_compile(self.compile_type, parent=var_dec_id)
        self.__advance_and_do_compile(self.compile_var_name_list, parent=var_dec_id)

    def compile_subroutine(self, parent):
        subroutine_root_id = gen_uuid4()
        self.parsed_tree[subroutine_root_id] = new_node(tag="subroutineDec")
        self.parsed_tree[parent]["children"].append(subroutine_root_id)
        self.compile_if_is_keyword_in(parent=subroutine_root_id, keywords={Keyword.CONSTRUCTOR, Keyword.FUNCTION, Keyword.METHOD})
        self.__advance_and_do_compile(self.compile_subroutine_type, parent=subroutine_root_id)
        self.__advance_and_do_compile(self.compile_subroutine_name, parent=subroutine_root_id)
        self.__advance_and_do_compile(self.compile_opening_parenthesis, parent=subroutine_root_id)
        self.__advance_and_do_compile(self.compile_parameter_list, parent=subroutine_root_id) # already advance to the next token
        self.compile_closing_parenthesis(parent=subroutine_root_id)
        self.__advance_and_do_compile(self.compile_subroutine_body, parent=subroutine_root_id)

    def compile_subroutine_body(self, parent):
        subroutine_body_id = gen_uuid4()
        self.parsed_tree[subroutine_body_id] = new_node(tag="subroutineBody")
        self.parsed_tree[parent]["children"].append(subroutine_body_id)

        self.compile_opening_bracket(parent=subroutine_body_id)
        while (self.tokenizer.has_more_tokens()):
            self.tokenizer.advance()
            if self.is_keyword_in({Keyword.VAR}):
                self.compile_var_dec(parent=subroutine_body_id)
            else:
                break

        self.compile_statements(parent=subroutine_body_id) # already advance at the next token

        if self.is_symbol_in("}"): self.compile_symbol(parent=subroutine_body_id)
        

    def compile_subroutine_constructor_function_method(self, parent):
        if self.is_keyword_in(keywords={Keyword.CONSTRUCTOR, Keyword.FUNCTION, Keyword.METHOD}):
            self.compile_keyword(parent)
        else:
            raise SyntaxError
        
    def compile_subroutine_type(self, parent):
        if self.is_keyword_in(keywords={Keyword.INT, Keyword.CHAR, Keyword.BOOLEAN, Keyword.VOID}):
            self.compile_keyword(parent)
        elif self.is_identifier(): # className
            self.compile_identifier(parent)
        else:
            raise SyntaxError
        
    def compile_subroutine_name(self, parent):
        if self.is_identifier(): self.compile_identifier(parent)
        else: raise SyntaxError

    def compile_opening_parenthesis(self, parent):
        if self.is_symbol_in({"("}): self.compile_symbol(parent)
        else: raise SyntaxError

    def compile_closing_parenthesis(self, parent):
        if self.is_symbol_in({")"}): self.compile_symbol(parent)
        else: raise SyntaxError

    def compile_parameter_list(self, parent):
        parameter_list_id = gen_uuid4()
        self.parsed_tree[parameter_list_id] = new_node(tag="parameterList")
        self.parsed_tree[parent]["children"].append(parameter_list_id)

        if self.is_keyword_in(keywords={Keyword.INT, Keyword.CHAR, Keyword.BOOLEAN}):
            self.compile_type(parent=parameter_list_id)
            self.__advance_and_do_compile(self.compile_var_name, parent=parameter_list_id)

            while (self.tokenizer.has_more_tokens()):
                self.tokenizer.advance()
                if self.is_symbol_in({","}):
                    self.compile_symbol(parent=parameter_list_id)
                    self.__advance_and_do_compile(self.compile_type, parent=parameter_list_id)
                    self.__advance_and_do_compile(self.compile_var_name, parent=parameter_list_id)
                else:
                    return

    def write_node(self, node, spaces):
        if node['text'] == None:
            self.dest_file.write(spaces + f"<{node['tag']}>\n" + spaces + f"</{node['tag']}>\n")
        else:
            self.dest_file.write(spaces + f"<{node['tag']}> {node['text']} </{node['tag']}>\n")

    def write_to_dest(self, node_id, spaces=''):
        node = self.parsed_tree[node_id]
        if node is not None:
            if len(node["children"]) > 0:
                self.dest_file.write(spaces + f"<{node['tag']}>\n")
                for child_id in node["children"]:
                    self.write_to_dest(child_id, spaces=spaces+'  ')
                self.dest_file.write(spaces + f"</{node['tag']}>\n")
            else:
                self.write_node(node, spaces)


    def compile_statements(self, parent):
        statements_id = gen_uuid4()
        self.parsed_tree[statements_id] = new_node(tag="statements")
        self.parsed_tree[parent]["children"].append(statements_id)

        while (self.is_keyword_in(keywords={Keyword.LET, Keyword.IF, Keyword.WHILE, Keyword.DO, Keyword.RETURN})):
            if (self.is_keyword_in({Keyword.LET})):
                self.compile_let(parent=statements_id)
                self.__advance_and_do_compile(self.compile_nothing)
            elif (self.is_keyword_in({Keyword.IF})):
                self.compile_if(parent=statements_id) # already advance to the next token
            elif (self.is_keyword_in({Keyword.WHILE})):
                self.compile_while(parent=statements_id)
                self.__advance_and_do_compile(self.compile_nothing)
            elif (self.is_keyword_in({Keyword.DO})):
                self.compile_do(parent=statements_id)
                self.__advance_and_do_compile(self.compile_nothing)
            elif (self.is_keyword_in({Keyword.RETURN})):
                self.compile_return(parent=statements_id)
                self.__advance_and_do_compile(self.compile_nothing)
            else:
                return


    def compile_let(self, parent):
        let_statement_id = gen_uuid4()
        self.parsed_tree[let_statement_id] = new_node(tag="letStatement")
        self.parsed_tree[parent]["children"].append(let_statement_id)

        self.compile_if_is_keyword_in(parent=let_statement_id, keywords={Keyword.LET})
        self.__advance_and_do_compile(self.compile_var_name, parent=let_statement_id)
        self.__advance_and_do_compile(self.compile_nothing)

        if self.is_symbol_in(symbols={"["}):
            self.compile_symbol(parent=let_statement_id)
            self.__advance_and_do_compile(self.compile_expression, parent=let_statement_id) # already advance to the next token
            self.compile_if_is_symbol_in(parent=let_statement_id, symbols={"]"})
            self.__advance_and_do_compile(self.compile_if_is_symbol_in, parent=let_statement_id, symbols={"="})
            self.__advance_and_do_compile(self.compile_expression, parent=let_statement_id) # already advance to the next token
            self.compile_if_is_symbol_in(parent=let_statement_id, symbols={";"})
        elif self.is_symbol_in(symbols={"="}):
            self.compile_symbol(parent=let_statement_id)
            self.__advance_and_do_compile(self.compile_expression, parent=let_statement_id)
            self.compile_if_is_symbol_in(parent=let_statement_id, symbols={";"})

    def compile_if(self, parent):
        if_statement_id = gen_uuid4()
        self.parsed_tree[if_statement_id] = new_node(tag="ifStatement")
        self.parsed_tree[parent]["children"].append(if_statement_id)

        self.compile_if_is_keyword_in(parent=if_statement_id, keywords={Keyword.IF})
        self.__advance_and_do_compile(self.compile_if_is_symbol_in, parent=if_statement_id, symbols={"("})
        self.__advance_and_do_compile(self.compile_expression, parent=if_statement_id) # already advance to the next token
        self.compile_if_is_symbol_in(parent=if_statement_id, symbols={")"})
        self.__advance_and_do_compile(self.compile_if_is_symbol_in, parent=if_statement_id, symbols={"{"})
        self.__advance_and_do_compile(self.compile_statements, parent=if_statement_id) # already advance to the next token
        self.compile_if_is_symbol_in(parent=if_statement_id, symbols={"}"})
        
        # ELSE trailing
        self.__advance_and_do_compile(self.compile_nothing)
        if self.is_keyword_in(keywords={Keyword.ELSE}):
            self.compile_keyword(parent=if_statement_id)
            self.__advance_and_do_compile(self.compile_if_is_symbol_in, parent=if_statement_id, symbols={"{"})
            self.__advance_and_do_compile(self.compile_statements, parent=if_statement_id)
            self.compile_if_is_symbol_in(parent=if_statement_id, symbols={"}"})
            self.__advance_and_do_compile(self.compile_nothing)
        else:
            return

    def compile_while(self, parent):
        while_statement_id = gen_uuid4()
        self.parsed_tree[while_statement_id] = new_node(tag="whileStatement")
        self.parsed_tree[parent]["children"].append(while_statement_id)

        self.compile_if_is_keyword_in(parent=while_statement_id, keywords={Keyword.WHILE})
        self.__advance_and_do_compile(self.compile_if_is_symbol_in, parent=while_statement_id, symbols={"("})
        self.__advance_and_do_compile(self.compile_expression, parent=while_statement_id) # already advance to the next token
        self.compile_if_is_symbol_in(parent=while_statement_id, symbols={")"})
        self.__advance_and_do_compile(self.compile_if_is_symbol_in, parent=while_statement_id, symbols={"{"})
        self.__advance_and_do_compile(self.compile_statements, parent=while_statement_id) # already advance to the next token
        self.compile_if_is_symbol_in(parent=while_statement_id, symbols={"}"})


    def compile_do(self, parent):
        do_statement_id = gen_uuid4()
        self.parsed_tree[do_statement_id] = new_node(tag="doStatement")
        self.parsed_tree[parent]["children"].append(do_statement_id)

        self.compile_if_is_keyword_in(parent=do_statement_id, keywords={Keyword.DO})
        self.__advance_and_do_compile(self.compile_identifier, parent=do_statement_id)
        self.__advance_and_do_compile(self.compile_nothing)
        if self.is_symbol_in(symbols={"("}):
            self.compile_symbol(parent=do_statement_id)
            self.__advance_and_do_compile(self.compile_expression_list, parent=do_statement_id) # already advance to the next token
            self.compile_symbol(parent=do_statement_id) # symbol ")"
            self.__advance_and_do_compile(self.compile_if_is_symbol_in, parent=do_statement_id, symbols={";"})
        elif self.is_symbol_in(symbols={"."}):
            self.compile_symbol(parent=do_statement_id)
            self.__advance_and_do_compile(self.compile_identifier, parent=do_statement_id)
            self.__advance_and_do_compile(self.compile_nothing)
            if self.is_symbol_in(symbols={"("}):
                self.compile_symbol(parent=do_statement_id)
                self.__advance_and_do_compile(self.compile_expression_list, parent=do_statement_id) # already advance to the next token
                self.compile_symbol(parent=do_statement_id) # symbol ")""
                self.__advance_and_do_compile(self.compile_if_is_symbol_in, parent=do_statement_id, symbols={";"})
            elif self.is_symbol_in(symbols={";"}):
                self.__advance_and_do_compile(self.compile_if_is_symbol_in, parent=do_statement_id, symbols={";"})
            else:
                return
        else:
            return
        

    def compile_return(self, parent):
        return_statement_id = gen_uuid4()
        self.parsed_tree[return_statement_id] = new_node(tag="returnStatement")
        self.parsed_tree[parent]["children"].append(return_statement_id)

        self.compile_if_is_keyword_in(parent=return_statement_id, keywords={Keyword.RETURN})
        self.__advance_and_do_compile(self.compile_nothing)
        if self.is_symbol_in(symbols={";"}):
            self.compile_symbol(parent=return_statement_id)
        elif self.is_possibly_term():
            self.compile_expression(parent=return_statement_id) # already advance to the next token
            self.compile_symbol(parent=return_statement_id) # compile ;


    def is_int_const(self):
        return self.tokenizer.token_type() == TokenType.INT_CONST
    
    def is_string_const(self):
        return self.tokenizer.token_type() == TokenType.STRING_CONST

    def compile_expression(self, parent):
        expression_id = gen_uuid4()
        self.parsed_tree[expression_id] = new_node(tag="expression")
        self.parsed_tree[parent]["children"].append(expression_id)

        while self.is_possibly_term():
            self.compile_term(parent=expression_id)
            if self.is_symbol_in({"+", "-", "*", "/", "&", "|", "<", ">", "="}): # op
                self.compile_symbol(parent=expression_id)
                self.__advance_and_do_compile(self.compile_nothing)
            else:
                return

    def compile_term(self, parent):
        term_id = gen_uuid4()
        self.parsed_tree[term_id] = new_node(tag="term")
        self.parsed_tree[parent]["children"].append(term_id)

        if self.is_int_const():
            self.compile_int_const(parent=term_id)
            self.__advance_and_do_compile(self.compile_nothing)

        elif self.is_string_const():
            self.compile_string_const(parent=term_id)
            self.__advance_and_do_compile(self.compile_nothing)

        elif self.is_keyword_in(keywords={Keyword.TRUE, Keyword.FALSE, Keyword.NULL, Keyword.THIS}):
            self.compile_keyword(parent=term_id)
            self.__advance_and_do_compile(self.compile_nothing)

        elif self.is_symbol_in(symbols={"-", "~"}): # unaryOp
            self.compile_symbol(parent=term_id)
            self.__advance_and_do_compile(self.compile_term, parent=term_id)
            
        elif self.is_symbol_in({"+", "-", "*", "/", "&", "|", "<", ">", "="}): # op
            self.compile_symbol(parent=term_id)
            self.__advance_and_do_compile(self.compile_nothing)

        elif self.is_symbol_in(symbols={"("}):
            self.compile_symbol(parent=term_id)
            self.__advance_and_do_compile(self.compile_expression, parent=term_id) # already advance to the next token
            self.compile_if_is_symbol_in(parent=term_id, symbols={")"})
            self.__advance_and_do_compile(self.compile_nothing)

        elif self.is_identifier:
            self.previous_token = self.tokenizer.current_token
            self.compile_identifier(parent=term_id)
            self.__advance_and_do_compile(self.compile_nothing)
            if (self.is_symbol_in({"["})):
                self.compile_symbol(parent=term_id)
                self.__advance_and_do_compile(self.compile_expression, parent=term_id) # already advance to the next token
                self.compile_symbol(parent=term_id)
                self.__advance_and_do_compile(self.compile_nothing)
            elif (self.is_symbol_in({"("})):
                self.compile_symbol(parent=term_id)
                self.__advance_and_do_compile(self.compile_expression_list, parent=term_id) # already advance to the next token
                self.compile_symbol(parent=term_id)
                self.__advance_and_do_compile(self.compile_nothing)
            elif (self.is_symbol_in({"."})):
                self.compile_symbol(parent=term_id)
                self.__advance_and_do_compile(self.compile_identifier, parent=term_id)
                self.__advance_and_do_compile(self.compile_if_is_symbol_in, parent=term_id, symbols={"("})
                self.__advance_and_do_compile(self.compile_expression_list, parent=term_id) # already advance to the next token
                self.compile_symbol(parent=term_id)
                self.__advance_and_do_compile(self.compile_nothing)
            else:
                return
        else:
            raise SyntaxError
        
    def is_possibly_term(self):
        return self.tokenizer.token_type() == TokenType.INT_CONST or \
                self.tokenizer.token_type() == TokenType.STRING_CONST or \
                self.is_keyword_in({Keyword.TRUE, Keyword.FALSE, Keyword.NULL, Keyword.THIS}) or \
                self.is_identifier() or \
                self.is_symbol_in(symbols={"-", "~", '('})

    def compile_expression_list(self, parent):
        expression_list_id = gen_uuid4()
        self.parsed_tree[expression_list_id] = new_node(tag="expressionList")
        self.parsed_tree[parent]["children"].append(expression_list_id)

        while self.is_possibly_term():
            self.compile_expression(parent=expression_list_id) # already advance to the next token
            if (self.is_symbol_in(symbols={","})):
                self.compile_symbol(parent=expression_list_id)
                self.__advance_and_do_compile(self.compile_nothing)
            else:
                return
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assembler")
    parser.add_argument("--source", type=str, help="Path to the source file")
    parser.add_argument("--dest", type=str, help="Path to the destination file")
    args = parser.parse_args()

    with open(args.source, "r") as source:
        with open(args.dest, "w") as dest:
            compiler = Compiler(source_file=source, dest_file=dest)
            compiler.compile_class()
            compiler.write_to_dest(compiler.root_id)
            # compiler.print_parsed_tree()
