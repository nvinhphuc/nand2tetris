from models import TokenType, Keyword
from tokenizer import Tokenizer
from utils import to_xml_text, gen_uuid4

class Compiler:
    previous_token = None
    is_looked_ahead = False
    def __init__(self, source_file, dest_file) -> None:
        self.tokenizer = Tokenizer(source_file)
        self.parsed_tree = {}

    def __advance_and_do_compile(self, compile_function):
        if (self.tokenizer.has_more_tokens()):
            self.previous_token = self.tokenizer.current_token
            self.tokenizer.advance()
            compile_function()
        else:
            raise SyntaxError

    def __new_node(tag, text = None, children = []):
        return { "tag": tag, "text": text, "children": children }
    
    def compile_nothing(self):
        pass
    
    def is_keyword_in(self, keywords):
        if self.tokenizer.token_type() != TokenType.KEYWORD: return False
        if self.tokenizer.keyword() not in keywords: return False
        return True
    
    def is_identifier(self):
        return self.tokenizer.token_type() == TokenType.IDENTIFIER
    
    def is_symbol_in(self, symbols):
        if self.tokenizer.token_type() != TokenType.SYMBOL: return False
        if self.tokenizer.symbol not in symbols: return False
        return True
    
    def compile_keyword(self, parent):
        keyword_id = gen_uuid4()
        self.parsed_tree[keyword_id] = self.__new_node(
            tag=TokenType.KEYWORD.value,
            text=self.tokenizer.keyword().value
        )
        self.parsed_tree[parent]["children"].append(keyword_id)

    def compile_identifier(self, parent):
        identifier_id = gen_uuid4()
        self.parsed_tree[identifier_id] = self.__new_node(
            tag=TokenType.KEYWORD.value,
            text=to_xml_text(self.tokenizer.identifier()),
        )
        self.parsed_tree[parent]["children"].append(identifier_id)

    def compile_int_const(self, parent):
        int_const_id = gen_uuid4()
        self.parsed_tree[int_const_id] = self.__new_node(
            tag=TokenType.INT_CONST.value,
            text=to_xml_text(self.tokenizer.int_val()),
        )
        self.parsed_tree[parent]["children"].append(int_const_id)

    def compile_string_const(self, parent):
        string_const_id = gen_uuid4()
        self.parsed_tree[string_const_id] = self.__new_node(
            tag=TokenType.STRING_CONST.value,
            text=to_xml_text(self.tokenizer.string_val()),
        )
        self.parsed_tree[parent]["children"].append(string_const_id)

    def compile_symbol(self, parent):
        symbol_id = gen_uuid4()
        self.parsed_tree[symbol_id] = self.__new_node(
            tag=TokenType.KEYWORD.SYMBOL,
            text=to_xml_text(self.tokenizer.symbol()),
        )
        self.parsed_tree[parent]["children"].append(symbol_id)

    def compile_if_is_keyword_in(self, parent, keywords):
        if self.is_keyword_in(keywords=keywords): self.compile_keyword(parent)
        else: raise SyntaxError

    def compile_if_is_symbol_in(self, parent, symbols):
        if self.is_symbol_in(symbols=symbols): self.compile_symbol(parent)
        else: raise SyntaxError

    def compile_if_is_identifier(self, parent):
        if self.is_identifier(): self.compile_identifier(parent)
        else: raise SyntaxError

    def compile_class_keyword(self, parent):
        if self.is_keyword_in(keywords={Keyword.CLASS}): self.compile_keyword(parent=parent)
        else: raise SyntaxError('Keyword "class" expected.')
            
    def compile_class_identifier(self, parent):
        if self.is_identifier(): self.compile_identifier(parent=parent)
        else: raise SyntaxError('An identifier is expected here.')
            
    def compile_opening_bracket(self, parent):
        if self.is_symbol_in(symbols={"{"}): self.compile_symbol(parent=parent)
        else: raise SyntaxError('Symbol "{" expected.')

    def compile_class(self):
        class_root_id = gen_uuid4()
        self.parsed_tree[class_root_id] = { "tag": "class", "children": [] }
        self.__advance_and_do_compile(self.compile_class_keyword(parent=class_root_id))
        self.__advance_and_do_compile(self.compile_class_identifier(parent=class_root_id))
        self.__advance_and_do_compile(self.compile_opening_bracket(parent=class_root_id))

        while (self.tokenizer.has_more_tokens()):
            self.tokenizer.advance()
            if self.is_keyword_in(keywords={Keyword.STATIC, Keyword.FIELD}):
                self.compile_class_var_dec()
            # elif self.keyword_condition() // subroutine
            elif self.is_symbol_in({"}"}):
                self.compile_symbol(parent=class_root_id)
                break
            else:
                raise SyntaxError


    def compile_class_var_dec(self):
        class_var_dec_root_id = gen_uuid4()
        self.parsed_tree[class_var_dec_root_id] = self.__new_node(tag="classVarDec")
        self.compile_static_field(parent=class_var_dec_root_id)
        self.__advance_and_do_compile(self.compile_type(parent=class_var_dec_root_id))
        self.__advance_and_do_compile(self.compile_var_name_list(parent=class_var_dec_root_id))
            
    def compile_var_name_list(self, parent):
        self.compile_var_name(parent=parent)
        while (self.tokenizer.has_more_tokens()):
            self.tokenizer.advance()
            if self.is_symbol_in({","}):
                self.compile_symbol(parent=parent)
                self.__advance_and_do_compile(self.compile_var_name(parent=parent))
            elif self.is_symbol_in({";"}):
                self.compile_symbol(parent=parent)
                break
            else:
                raise SyntaxError

                
        
    def compile_static_field(self, parent):
        if self.is_keyword_in(keywords={Keyword.STATIC, Keyword.FIELD}):
            self.compile_keyword(parent)
        else:
            raise SyntaxError

    def compile_type(self, parent):
        if self.is_keyword_in(keywords={Keyword.INT, Keyword.CHAR, Keyword.BOOLEAN}):
            self.compile_keyword(parent)
        elif (self.tokenizer.token_type() == TokenType.IDENTIFIER):
            self.compile_identifier(parent)
        else:
            raise SyntaxError
        
    def compile_var_name(self, parent):
        self.compile_if_is_identifier(parent)

    def compile_subroutine(self):
        subroutine_root_id = gen_uuid4()
        self.parsed_tree[subroutine_root_id] = self.__new_node(tag="subroutineDec")
        self.compile_if_is_keyword_in(parent=subroutine_root_id, keywords={Keyword.CONSTRUCTOR, Keyword.FUNCTION, Keyword.METHOD})
        self.__advance_and_do_compile(self.compile_opening_parenthesis(parent=subroutine_root_id))
        self.__advance_and_do_compile(self.compile_subroutine_type(parent=subroutine_root_id))
        self.__advance_and_do_compile(self.compile_subroutine_name(parent=subroutine_root_id))
        self.__advance_and_do_compile(self.compile_parameter_list(parent=subroutine_root_id))
        # compile subroutine body


    def compile_subroutine_constructor_function_method(self, parent):
        if self.is_keyword_in(keywords={Keyword.CONSTRUCTOR, Keyword.FUNCTION, Keyword.METHOD}):
            self.compile_keyword(parent)
        else:
            raise SyntaxError
        
    def compile_subroutine_type(self, parent):
        if self.is_keyword_in(keywords={Keyword.INT, Keyword.CHAR, Keyword.BOOLEAN, Keyword.VOID}):
            self.compile_keyword(parent)
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
        self.compile_opening_parenthesis(parent)
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()
            if self.is_symbol_in({")"}):
                self.compile_symbol(parent)
            elif self.is_keyword_in(keywords={Keyword.INT, Keyword.CHAR, Keyword.BOOLEAN}):
                self.compile_type(parent)
                self.__advance_and_do_compile(self.compile_var_name(parent))
            else:
                raise SyntaxError
        while (self.tokenizer.has_more_tokens()):
            self.tokenizer.advance()
            if self.is_symbol_in({","}):
                self.compile_symbol(parent)
                self.__advance_and_do_compile(self.compile_type(parent))
                self.__advance_and_do_compile(self.compile_var_name(parent))
            elif self.is_symbol_in({")"}):
                self.compile_symbol(parent)
                break
            else:
                raise SyntaxError

    def compile_subroutine_body(self, parent):
        self.compile_opening_bracket(parent)
        self.__advance_and_do_compile(self.compile_nothing)
        if self.is_keyword_in({Keyword.VAR}):
            self.compile_var_dec(parent)
        elif self.is_keyword_in({Keyword.LET, Keyword.IF, Keyword.WHILE, Keyword.DO, Keyword.RETURN}):
            self.compile_statements ## TODO

        elif self.is_symbol_in("}"):
            self.compile_symbol(parent)


    def compile_var_dec(self, parent):
        self.compile_if_is_keyword_in(parent=parent, keywords={Keyword.VAR})
        self.__advance_and_do_compile(self.compile_type(parent))
        self.__advance_and_do_compile(self.compile_var_name_list(parent))


    def compile_statements(self, parent):
        ## TODO
        self.__advance_and_do_compile(self.compile_nothing)
        if (self.is_keyword_in({Keyword.IF})):
            self.compile_if(parent)
        elif (self.is_keyword_in({Keyword.WHILE})):
            self.compile_while(parent)
        elif (self.is_keyword_in({Keyword.DO})):
            self.compile_do(parent)
        elif (self.is_keyword_in({Keyword.RETURN})):
            self.compile_return(parent)

    def is_possibly_term(self):
        return self.tokenizer.token_type() == TokenType.INT_CONST or \
                self.tokenizer.token_type() == TokenType.STRING_CONST or \
                self.is_keyword_in({Keyword.TRUE, Keyword.FALSE, Keyword.NULL, Keyword.THIS}) or \
                self.is_identifier() or \
                self.is_symbol_in(symbols={"-", "~", '('})


    def compile_let(self, parent):
        self.compile_if_is_keyword_in(parent=parent, keywords={Keyword.LET})
        self.__advance_and_do_compile(self.compile_var_name(parent))
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()
            if self.is_symbol_in(symbols={"["}):
                self.__advance_and_do_compile(self.compile_if_is_symbol_in(parent=parent, symbols={"["}))
                self.__advance_and_do_compile(self.compile_expression(parent))
                self.__advance_and_do_compile(self.compile_if_is_symbol_in(parent=parent, symbols={"]"}))
            elif self.is_symbol_in(symbols={"="}):
                self.__advance_and_do_compile(self.compile_if_is_symbol_in(parent=parent, symbols={"="}))
                self.__advance_and_do_compile(self.compile_expression(parent))
                self.__advance_and_do_compile(self.compile_if_is_symbol_in(parent=parent, symbols={";"}))


    def compile_if(self, parent):
        self.compile_if_is_keyword_in(parent=parent, keywords={Keyword.IF})
        self.__advance_and_do_compile(self.compile_if_is_symbol_in(parent=parent, symbols={"("}))
        self.__advance_and_do_compile(self.compile_expression(parent))
        self.__advance_and_do_compile(self.compile_if_is_symbol_in(parent=parent, symbols={")"}))
        self.__advance_and_do_compile(self.compile_if_is_symbol_in(parent=parent, symbols={"{"}))
        self.__advance_and_do_compile(self.compile_statements(parent))
        self.__advance_and_do_compile(self.compile_if_is_symbol_in(parent=parent, symbols={"}"}))
        if self.tokenizer.has_more_tokens:
            self.tokenizer.advance()
            if self.is_keyword_in(keywords={Keyword.ELSE}):
                self.compile_keyword(parent)
                self.__advance_and_do_compile(self.compile_if_is_symbol_in(parent=parent, symbols={"{"}))
                # TODO: self.compile_statements(parent)
                self.__advance_and_do_compile(self.compile_if_is_symbol_in(parent=parent, symbols={"}"}))

    def compile_while(self, parent):
        self.compile_if_is_keyword_in(parent=parent, keywords={Keyword.WHILE})
        self.__advance_and_do_compile(self.compile_if_is_symbol_in(parent=parent, symbols={"("}))
        self.__advance_and_do_compile(self.compile_expression(parent))
        self.__advance_and_do_compile(self.compile_if_is_symbol_in(parent=parent, symbols={")"}))
        self.__advance_and_do_compile(self.compile_if_is_symbol_in(parent=parent, symbols={"{"}))
        self.__advance_and_do_compile(self.compile_statements(parent))
        self.__advance_and_do_compile(self.compile_if_is_symbol_in(parent=parent, symbols={"}"}))


    def compile_do(self, parent):
        self.compile_if_is_keyword_in(parent=parent, keywords={Keyword.WHILE})
        self.compile_subroutine_call(parent)
        self.__advance_and_do_compile(self.compile_if_is_symbol_in(parent=parent, symbols={";"}))

    def compile_subroutine_call(self, parent):
        self.compile_identifier(parent)
        self.__advance_and_do_compile(self.compile_nothing)
        if self.is_symbol_in(symbols={"("}):
            self.compile_symbol(parent)
            self.__advance_and_do_compile(self.compile_nothing)
            if self.is_symbol_in(symbols={")"}):
                self.compile_symbol(parent)
            else:
                self.compile_expression_list()
        elif self.is_symbol_in(symbols={"."}):
            self.compile_symbol(parent)
            self.__advance_and_do_compile(self.compile_identifier(parent))
            self.__advance_and_do_compile(self.compile_nothing)
            if self.is_symbol_in(symbols={"("}):
                self.compile_symbol(parent)
                self.__advance_and_do_compile(self.compile_nothing)
                if self.is_symbol_in(symbols={")"}):
                    self.compile_symbol(parent)
                else:
                    self.compile_expression_list()
        

    def compile_return(self, parent):
        self.compile_if_is_keyword_in(parent=parent, keywords={Keyword.RETURN})
        if self.tokenizer.has_more_tokens:
            self.tokenizer.advance()
            if self.is_symbol_in(symbols={";"}):
                self.compile_symbol(parent)
            elif self.is_possibly_term():
                self.compile_expression(parent)
                self.__advance_and_do_compile(self.compile_symbol(parent))


    def is_int_const(self):
        return self.tokenizer.token_type() == TokenType.INT_CONST
    
    def is_string_const(self):
        return self.tokenizer.token_type() == TokenType.STRING_CONST
    
    def is_op(self):
        return self.is_symbol_in({"+", "-", "*", "/", "&", "|", "<", ">", "="})

    def compile_expression(self, parent):
        self.compile_term(parent)

        if self.is_looked_ahead:
            if self.is_op():
                self.compile_symbol(parent)
                self.is_looked_ahead = False
                self.__advance_and_do_compile(self.compile_term)
            else:
                pass
        else:
            self.__advance_and_do_compile(self.compile_nothing)
            if self.is_op():
                self.compile_symbol(parent)
                self.__advance_and_do_compile(self.compile_term)
            else:
                pass




    def compile_term(self, parent):
        if self.is_int_const(): self.compile_int_const(parent)
        elif self.is_string_const(): self.compile_string_const(parent)
        elif self.is_keyword_in(keywords={Keyword.TRUE, Keyword.FALSE, Keyword.NULL, Keyword.THIS}): self.compile_keyword(parent)
        elif self.is_identifier:
            self.compile_identifier(parent)
            self.__advance_and_do_compile(self.compile_nothing)
            if self.is_symbol_in(symbols={"["}):
                self.compile_symbol(parent)
                self.__advance_and_do_compile(self.compile_expression)
                if self.is_looked_ahead:
                    self.compile_if_is_symbol_in({"]"})
                    self.is_looked_ahead = False
                else:
                    self.__advance_and_do_compile(self.compile_if_is_symbol_in({"]"}))
            elif self.is_symbol_in(symbols={"("}):
                self.compile_symbol(parent)
                self.__advance_and_do_compile(self.compile_nothing)
                if self.is_symbol_in(symbols={")"}):
                    self.compile_symbol(parent)
                else:
                    self.compile_expression_list()
            elif self.is_symbol_in(symbols={"."}):
                self.compile_symbol(parent)
                self.__advance_and_do_compile(self.compile_identifier(parent))
                self.__advance_and_do_compile(self.compile_nothing)
                if self.is_symbol_in(symbols={"("}):
                    self.compile_symbol(parent)
                    self.__advance_and_do_compile(self.compile_nothing)
                    if self.is_symbol_in(symbols={")"}):
                        self.compile_symbol(parent)
                    else:
                        self.compile_expression_list()
            else:
                self.is_looked_ahead = True
        elif self.is_symbol_in(symbols={"("}):
            self.compile_symbol(parent)
            self.compile_expression(parent)
            self.__advance_and_do_compile(self.compile_closing_parenthesis(parent))
        elif self.is_symbol_in(symbols={"-", "~"}):
            self.compile_symbol(parent)
            self.__advance_and_do_compile(self.compile_term(parent))

    def compile_expression_list(self, parent):
        if self.is_possibly_term():
            self.compile_expression(parent)
        while self.tokenizer.has_more_tokens():
            if not self.is_looked_ahead: self.tokenizer.advance()
            if self.is_symbol_in(symbols={")"}):
                self.compile_symbol(parent)
                break
            elif self.is_symbol_in(symbols={","}):
                self.compile_symbol(parent)
                self.__advance_and_do_compile(self.compile_expression(parent))