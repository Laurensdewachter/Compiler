from llvmlite import ir, binding
from ..parser.TreeNode import *
from src.main.SymbolTable import SymbolTable, SymbolTableEntryType
import subprocess


def node_to_llvmtype(node: TreeNode, symbol_table: SymbolTable) -> ir.Type:
    match node:
        case IntNode():
            return ir.IntType(32)
        case FloatNode():
            return ir.FloatType()
        case StringNode():
            return ir.ArrayType(ir.IntType(8), len(node.value))
        case PlusNode():
            return node_to_llvmtype(node.children[0], symbol_table)
        case MultNode():
            return node_to_llvmtype(node.children[0], symbol_table)
        case DivNode():
            return node_to_llvmtype(node.children[0], symbol_table)
        case MinusNode():
            return node_to_llvmtype(node.children[0], symbol_table)
        case EqualNode():
            return ir.IntType(1)
        case NeqNode():
            return ir.IntType(1)
        case GtNode():
            return ir.IntType(1)
        case LtNode():
            return ir.IntType(1)
        case GeqNode():
            return ir.IntType(1)
        case LeqNode():
            return ir.IntType(1)
        case ModNode():
            return ir.IntType(32)
        case IdNode():
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
        case _:
            raise Exception(f"Unknown type: {node}")


class LlvmConverter:
    def __init__(self, symbol_table: SymbolTable):
        self.blocks = []
        self.builders = []

        # Get the target triple using llvm-config
        target_triple = (
            subprocess.check_output(["llvm-config", "--host-target"]).decode().strip()
        )
        self.module = ir.Module("module")
        self.module.triple = target_triple

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
                        ir.ArrayType(ir.IntType(8), len(value.value)),
                        bytearray(value.value.encode("utf-8")),
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
            case EqualNode():
                left = self.node_to_llvm(value.children[0])
                right = self.node_to_llvm(value.children[1])
                type = self.symbol_table.find_entry(value.children[0].value).type
                if type == SymbolTableEntryType.Int:
                    builder.store(builder.icmp_signed("==", left, right), llvm_var)
                elif type == SymbolTableEntryType.Float:
                    builder.store(builder.fcmp_ordered("==", left, right), llvm_var)
                else:
                    raise Exception(
                        f"Unknown type at Generation of assignment: {value}"
                    )
            case NeqNode():
                left = self.node_to_llvm(value.children[0])
                right = self.node_to_llvm(value.children[1])
                type = self.symbol_table.find_entry(value.children[0].value).type
                if type == SymbolTableEntryType.Int:
                    builder.store(builder.icmp_signed("!=", left, right), llvm_var)
                elif type == SymbolTableEntryType.Float:
                    builder.store(builder.fcmp_ordered("!=", left, right), llvm_var)
                else:
                    raise Exception(
                        f"Unknown type at Generation of assignment: {value}"
                    )
            case GtNode():
                left = self.node_to_llvm(value.children[0])
                right = self.node_to_llvm(value.children[1])
                type = self.symbol_table.find_entry(value.children[0].value).type
                if type == SymbolTableEntryType.Int:
                    builder.store(builder.icmp_signed(">", left, right), llvm_var)
                elif type == SymbolTableEntryType.Float:
                    builder.store(builder.fcmp_ordered(">", left, right), llvm_var)
                else:
                    raise Exception(
                        f"Unknown type at Generation of assignment: {value}"
                    )
            case LtNode():
                left = self.node_to_llvm(value.children[0])
                right = self.node_to_llvm(value.children[1])
                type = self.symbol_table.find_entry(value.children[0].value).type
                if type == SymbolTableEntryType.Int:
                    builder.store(builder.icmp_signed("<", left, right), llvm_var)
                elif type == SymbolTableEntryType.Float:
                    builder.store(builder.fcmp_ordered("<", left, right), llvm_var)
                else:
                    raise Exception(
                        f"Unknown type at Generation of assignment: {value}"
                    )

            case GeqNode():
                left = self.node_to_llvm(value.children[0])
                right = self.node_to_llvm(value.children[1])
                type = self.symbol_table.find_entry(value.children[0].value).type
                if type == SymbolTableEntryType.Int:
                    builder.store(builder.icmp_signed(">=", left, right), llvm_var)
                elif type == SymbolTableEntryType.Float:
                    builder.store(builder.fcmp_ordered(">=", left, right), llvm_var)
                else:
                    raise Exception(
                        f"Unknown type at Generation of assignment: {value}"
                    )

            case LeqNode():
                left = self.node_to_llvm(value.children[0])
                right = self.node_to_llvm(value.children[1])
                type = self.symbol_table.find_entry(value.children[0].value).type
                if type == SymbolTableEntryType.Int:
                    builder.store(builder.icmp_signed("<=", left, right), llvm_var)
                elif type == SymbolTableEntryType.Float:
                    builder.store(builder.fcmp_ordered("<=", left, right), llvm_var)
                else:
                    raise Exception(
                        f"Unknown type at Generation of assignment: {value}"
                    )
            case ModNode():
                left = self.node_to_llvm(value.children[0])
                right = self.node_to_llvm(value.children[1])
                builder.store(builder.srem(left, right), llvm_var)
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
            case ModNode():
                left = self.node_to_llvm(node.children[0])
                right = self.node_to_llvm(node.children[1])
                return builder.srem(left, right)
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

        match node:
            case MainNode():
                function = ir.Function(
                    self.module, ir.FunctionType(ir.IntType(32), []), "main"
                )
                self.blocks.append(function.append_basic_block("main"))
                self.builders.append(ir.IRBuilder(self.blocks[-1]))

            case AssignNode():
                assignee = self.symbol_table.find_entry(node.children[0].value).llvm_var
                value = node.children[1]

                self.store_value(value, assignee)

            case NewVariableNode():
                builder = self.builders[-1]

                symbol_table_entry = self.symbol_table.find_entry(
                    node.children[0].value
                )

                var_type = node_to_llvmtype(node.children[1], self.symbol_table)
                var = builder.alloca(var_type, name=node.children[0].value)

                symbol_table_entry.llvm_var = var
                value = node.children[1]

                self.store_value(value, var)

            case ReturnNode():
                builder = self.builders[-1]

                match node.children[0]:
                    case IntNode():
                        builder.ret(
                            ir.Constant(ir.IntType(32), int(node.children[0].value))
                        )
                    case FloatNode():
                        builder.ret(
                            ir.Constant(ir.FloatType(), float(node.children[0].value))
                        )
                    case StringNode():
                        builder.ret(
                            ir.Constant(
                                ir.ArrayType(
                                    ir.IntType(8), len(node.children[0].value)
                                ),
                                bytearray(node.children[0].value.encode("utf-8")),
                            )
                        )
                    case IdNode():
                        builder.ret(
                            builder.load(
                                self.symbol_table.find_entry(
                                    node.children[0].value
                                ).llvm_var
                            )
                        )
                    case PlusNode():
                        builder.ret(self.addition(node.children[0]))
                    case MultNode():
                        builder.ret(self.multiplication(node.children[0]))
                    case DivNode():
                        builder.ret(self.division(node.children[0]))
                    case MinusNode():
                        builder.ret(self.subtraction(node.children[0]))
                    case _:
                        raise Exception(
                            f"Unknown type at Generation of return: {node.children[0]}"
                        )

        for child in node.children:
            self.convert(child)

    def return_llvm_code(self) -> str:
        return str(self.module)
