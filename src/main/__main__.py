import argparse
from src.parser.Parser import Parser
from src.parser.DotExporter import DotExporter
from src.parser.SymbolTable import *
from src.parser.SemanticAnalyzer import *
from src.llvm_target.Converter import LlvmConverter

parser: argparse.ArgumentParser = argparse.ArgumentParser(prog="C-Compiler")
parser.add_argument("--input", help="input file", required=True)
parser.add_argument("--render_ast", help="render AST as dot-file")
parser.add_argument("--render_symb", help="render symbol table as dot-file")
parser.add_argument("--target_llvm", help="compile to LLVM")
parser.add_argument("--target_mips", help="compile to MIPS")
parser.add_argument(
    "--no-const-folding", help="disable constant folding", default=False
)
parser.add_argument(
    "--no-const-propagation", help="disable constant propagation", default=False
)

if __name__ == "__main__":
    args = parser.parse_args()

    input_file = args.input
    ast_file = args.render_ast
    symb_file = args.render_symb
    target_llvm = args.target_llvm
    target_mips = args.target_mips
    no_const_folding = args.no_const_folding
    no_const_propagation = args.no_const_propagation

    # Generate AST
    ast: TreeNode = Parser.parse(input_file, no_const_folding, no_const_propagation)
    # Generate symbol table
    symbol_table: SymbolTable = SymbolTable()
    symbol_table.build_symbol_table(ast)
    # Analyze semantic
    # semantic_errors: list[str] = SemanticAnalyzer.analyze(ast, symbol_table)
    # for error in semantic_errors:
    #     print(error)
    # if semantic_errors:
    #     quit(-1)

    if ast_file:
        DotExporter.export(ast, ast_file)

    if symb_file:
        with open(symb_file + ".txt", "w") as f:
            f.write(str(symbol_table))

    if target_llvm:
        # Generate llvm target
        converter = LlvmConverter(symbol_table, input_file)
        converter.convert(ast)

        with open(target_llvm, "w") as f:
            f.write(converter.return_llvm_code())

    if target_mips:
        # TODO: Implement MIPS compiler
        pass
