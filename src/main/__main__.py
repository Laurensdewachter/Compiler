import argparse
from src.parser.Parser import Parser
from src.parser.DotExporter import DotExporter
from src.main.SymbolTable import *
from src.llvm_target.Converter import LlvmConverter

parser: argparse.ArgumentParser = argparse.ArgumentParser(prog="C-Compiler")
parser.add_argument("--input", help="input file", required=True)
parser.add_argument("--render_ast", help="render AST as dot-file")
parser.add_argument("--render_symb", help="render symbol table as dot-file")
parser.add_argument("--target_llvm", help="compile to LLVM")
parser.add_argument("--target_mips", help="compile to MIPS")

if __name__ == "__main__":
    args = parser.parse_args()

    input_file = args.input
    ast_file = args.render_ast
    symb_file = args.render_symb
    target_llvm = args.target_llvm
    target_mips = args.target_mips

    # Generate CST
    cst = Parser.parse(input_file)

    symbol_table = SymbolTable()
    symbol_table.build_symbol_table(cst)

    # Render CST
    DotExporter.export(cst, "output")

    converter = LlvmConverter(symbol_table)
    converter.convert(cst)

    if ast_file:
        DotExporter.export(cst, ast_file)

    if symb_file:
        # TODO: Implement symbol table renderer
        pass

    if target_llvm:
        # TODO: Implement LLVM compiler
        with open(target_llvm, "w") as f:
            f.write(converter.return_llvm_code())

    if target_mips:
        # TODO: Implement MIPS compiler
        pass
