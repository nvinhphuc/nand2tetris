import argparse
from constants import DEST_TABLE, JUMP_TABLE, COMP_TABLE
from utils import dec2bin
import logging

class Parser:
    def __init__(self):
        return
    
    def __parse_a_instruction(self, line):
        address = int(line[1:])
        bin_address = dec2bin(decimal=address, num_bits=15)
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
        for line, location in lines:
            try:
                if line[0] == "@": # A-instruction
                    instructions.append(self.__parse_a_instruction(line))
                else: # C-instruction
                    instructions.append(self.__parse_c_instruction(line))
            except Exception:
                logging.error(f"line: {line}, location: {location}")
        return instructions

class Assembler:
    def __init__(self):
        self.parser = Parser()
    
    def __read_source(self, source_path):
        lines = []
        location = 1
        with open(source_path, "r") as source:
            for line in source:
                line = line.strip()
                ignore = line.startswith("//") or line == ""
                if not ignore:
                    lines.append((line, location))
                    location += 1
        return lines
    
    def __write_to_dest(self, instructions, dest_path):
        with open(dest_path, "w") as dest:
            dest.writelines(inst + "\n" for inst in instructions)
    
    def assemble(self, source_path, dest_path):
        lines = self.__read_source(source_path)
        instructions = self.parser.parse(lines)
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