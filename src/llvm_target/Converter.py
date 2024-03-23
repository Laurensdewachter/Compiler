from llvmlite import ir, binding
from ..parser.TreeNode import *
from src.main.SymbolTable import SymbolTable, SymbolTableEntryType


def node_to_llvmtype(node: TreeNode, symbol_table: SymbolTable) -> ir.Type:
    if isinstance(node, IntNode):
        return ir.IntType(32)
    if isinstance(node, FloatNode):
        return ir.FloatType()
    if isinstance(node, StringNode):
        return ir.ArrayType(ir.IntType(8), len(node.value))
    if isinstance(node, (PlusNode, MultNode, DivNode, MinusNode)):
        return node_to_llvmtype(node.children[0], symbol_table)
    if isinstance(node, IdNode):
        symbol_table_type = symbol_table.find_entry(node.value).type
        match symbol_table_type:
            case SymbolTableEntryType.Int:
                return ir.IntType(32)
            case SymbolTableEntryType.Float:
                return ir.FloatType()
            case SymbolTableEntryType.String:
                return ir.ArrayType(ir.IntType(8), 0)
            case _:
                raise Exception(f"Unknown type: {symbol_table_type}")

    raise Exception(f"Unknown type: {node}")


class LlvmConverter:
    def __init__(self, symbol_table: SymbolTable):
        self.blocks = []
        self.builders = []
        self.module = ir.Module("module")
        self.symbol_table = symbol_table

    def store_value(self, value: TreeNode, llvm_var: ir.Value) -> None:
        builder = self.builders[-1]

        match value:
            case IntNode():
                builder.store(ir.Constant(ir.IntType(32), int(value.value)), llvm_var)
            case FloatNode():
                builder.store(ir.Constant(ir.FloatType(), float(value.value)), llvm_var)
            case StringNode():
                builder.store(
                    ir.Constant(
                        ir.ArrayType(ir.IntType(8), len(value.value)), value.value
                    ),
                    llvm_var,
                )
            case IdNode():
                builder.store(
                    builder.load(self.symbol_table.find_entry(value.value).llvm_var),
                    llvm_var,
                )
            case PlusNode():
                builder.store(self.addition(value), llvm_var)
            case MultNode():
                builder.store(self.multiplication(value), llvm_var)
            case DivNode():
                builder.store(self.division(value), llvm_var)
            case MinusNode():
                builder.store(self.subtraction(value), llvm_var)
            case _:
                raise Exception(f"Unknown type at Generation of assignment: {value}")

    def node_to_llvm(self, node: TreeNode) -> ir.Value:
        builder = self.builders[-1]
        match node:
            case IntNode():
                return ir.Constant(ir.IntType(32), int(node.value))
            case FloatNode():
                return ir.Constant(ir.FloatType(), float(node.value))
            case IdNode():
                return builder.load(self.symbol_table.find_entry(node.value).llvm_var)
            case PlusNode():
                return self.addition(node)
            case MultNode():
                return self.multiplication(node)
            case DivNode():
                return self.division(node)
            case MinusNode():
                return self.subtraction(node)
            case _:
                raise Exception(f"Unknown type: {node}")

    def addition(self, node: TreeNode) -> ir.Value:
        builder = self.builders[-1]
        left = node.children[0]
        right = node.children[1]

        left_llvm = self.node_to_llvm(left)
        right_llvm = self.node_to_llvm(right)

        var = builder.add(left_llvm, right_llvm)

        return var

    def multiplication(self, node: TreeNode) -> ir.Value:
        builder = self.builders[-1]
        left = node.children[0]
        right = node.children[1]

        left_llvm = self.node_to_llvm(left)
        right_llvm = self.node_to_llvm(right)

        var = builder.mul(left_llvm, right_llvm)

        return var

    def division(self, node: TreeNode) -> ir.Value:
        builder = self.builders[-1]
        left = node.children[0]
        right = node.children[1]

        left_llvm = self.node_to_llvm(left)
        right_llvm = self.node_to_llvm(right)

        var = builder.udiv(left_llvm, right_llvm)

        return var

    def subtraction(self, node: TreeNode) -> ir.Value:
        builder = self.builders[-1]
        left = node.children[0]
        right = node.children[1]

        left_llvm = self.node_to_llvm(left)
        right_llvm = self.node_to_llvm(right)

        var = builder.sub(left_llvm, right_llvm)

        return var

    def convert(self, node: TreeNode) -> None:

        if isinstance(node, MainNode):
            function = ir.Function(
                self.module, ir.FunctionType(ir.IntType(32), []), "main"
            )
            self.blocks.append(function.append_basic_block("main"))
            self.builders.append(ir.IRBuilder(self.blocks[-1]))

        if isinstance(node, AssignNode):
            assignee = self.symbol_table.find_entry(node.children[0].value).llvm_var
            value = node.children[1]

            self.store_value(value, assignee)

        if isinstance(node, NewVariableNode):
            builder = self.builders[-1]

            symbol_table_entry = self.symbol_table.find_entry(node.children[0].value)

            var_type = node_to_llvmtype(node.children[1], self.symbol_table)
            var = builder.alloca(var_type, name=node.children[0].value)

            symbol_table_entry.llvm_var = var
            value = node.children[1]

            self.store_value(value, var)

        if isinstance(node, ReturnNode):
            block = self.blocks[-1]
            builder = self.builders[-1]

            if isinstance(node.children[0], IntNode):
                builder.ret(ir.Constant(ir.IntType(32), int(node.children[0].value)))
            elif isinstance(node.children[0], FloatNode):
                builder.ret(ir.Constant(ir.FloatType(), float(node.children[0].value)))
            elif isinstance(node.children[0], StringNode):
                builder.ret(
                    ir.Constant(
                        ir.ArrayType(ir.IntType(8), len(node.children[0].value)),
                        node.children[0].value,
                    )
                )
            elif isinstance(node.children[0], IdNode):
                builder.ret(
                    builder.load(
                        self.symbol_table.find_entry(node.children[0].value).llvm_var
                    )
                )

        for child in node.children:
            self.convert(child)

    def return_llvm_code(self) -> str:
        return str(self.module)
