import argparse
from typing import List, Tuple
from constants import DEST_TABLE, JUMP_TABLE, COMP_TABLE, PREDEFINED_SYMBOLS
from utils import dec2bin
import logging

class Parser:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
    
    def __parse_a_instruction(self, line):
        address = line[1:]
        if (address[0] >= '0' and address[0] <= '9'): # is number address
            bin_address = dec2bin(decimal=int(address), num_bits=15)
        else: # is symbol address
            logging.info(f"SYMBOL: {address}, value: {self.symbol_table[address]}")
            bin_address = dec2bin(decimal=self.symbol_table[address], num_bits=15)
        return "0" + bin_address
    
    def __split_c_instruction(self, line):
        parts = line.split("=")
        if len(parts) == 1:
            dest = ""
            comp_jump = parts[0].split(";")
        elif len(parts) == 2:
            dest = parts[0].strip()
            comp_jump = parts[1].split(";")
        else:
            raise SyntaxError
        
        comp = comp_jump[0].strip()

        if len(comp_jump) == 2: jump = comp_jump[1].strip()
        elif len(comp_jump) == 1: jump = ""
        else:
            raise SyntaxError

        return dest, comp, jump
    
    def __parse_c_instruction(self, line):
        dest, comp, jump = self.__split_c_instruction(line)
        return "111" + COMP_TABLE[comp] + DEST_TABLE[dest] + JUMP_TABLE[jump]
    
    def parse(self, lines):
        instructions = []
        for line in lines:
            try:
                if line[0] == "@": # A-instruction
                    instructions.append(self.__parse_a_instruction(line))
                elif line[0] == "(": # Symbol declaration
                    continue
                else: # C-instruction
                    instructions.append(self.__parse_c_instruction(line))
            except Exception:
                logging.error(f"line: {line}")
        return instructions

class Assembler:
    def __init__(self):
        return
    
    def __read_source(self, source_path):
        lines = []
        with open(source_path, "r") as source:
            for line in source:
                line = line.strip()
                ignore = line.startswith("//") or line == ""
                if not ignore:
                    lines.append(line.split("//")[0].strip())
        return lines
    
    def __write_to_dest(self, instructions, dest_path):
        with open(dest_path, "w") as dest:
            dest.writelines(inst + "\n" for inst in instructions)

    def __build_symbol_tables(self, lines):
        symbol_table = {**PREDEFINED_SYMBOLS}

        def get_labels(lines: List[str]):
            location = 0
            for line in lines:
                if line.startswith("("):
                    label = line[1:-1] # Remove first "(" and last ")" characters
                    logging.info(f"label: {label}, location: {location}")
                    if (symbol_table.get(label) is None):
                        symbol_table[label] = location
                    else:
                        raise Exception(f'Keyword "{label}" have already existed!')
                    continue
                location += 1
                    
        def get_variables(lines: List[str]):
            ram_address = 16 # In HACK platform, the RAM space designated for storing variables starts at 16
            for line in lines:
                if line.startswith("@") and not (line[1] >= '0' and line[1] <= '9'):
                    variable = line[1:]
                    if (symbol_table.get(variable) is None):
                        symbol_table[variable] = ram_address
                        ram_address += 1
        
        get_labels(lines)
        get_variables(lines)

        return symbol_table
    
    def assemble(self, source_path, dest_path):
        lines = self.__read_source(source_path)
        symbol_table = self.__build_symbol_tables(lines)
        parser = Parser(symbol_table)
        instructions = parser.parse(lines)
        self.__write_to_dest(instructions, dest_path)
    

def main():
    assembler = Assembler()
    assembler.assemble(source_path=args.source, dest_path=args.dest)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assembler")
    parser.add_argument("--source", type=str, help="Path to the source file")
    parser.add_argument("--dest", type=str, help="Path to the destination file")
    args = parser.parse_args()
    main()