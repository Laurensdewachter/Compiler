import argparse
from src.parser.Parser import Parser
from src.parser.DotExporter import DotExporter

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

    # Generate AST
    ast = Parser.parse(input_file)

    if ast_file:
        DotExporter.export(ast, ast_file)

    if symb_file:
        # TODO: Implement symbol table renderer
        pass

    if target_llvm:
        # TODO: Implement LLVM compiler
        pass

    if target_mips:
        # TODO: Implement MIPS compiler
        pass
