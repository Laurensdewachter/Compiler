from llvmlite import ir, binding
from src.parser.SymbolTable import SymbolTable, SymbolTableEntryType
import subprocess
from src.parser.TreeNode import *


def node_to_llvmtype(node: TreeNode, symbol_table: SymbolTable) -> ir.Type:
    """
    Check type of a TreeNode to a llvmlite ir.Type
    :param node: TreeNode to check the type of
    :param symbol_table: symbol table of the compiler
    :return: ir.Type : The type of the TreeNode
    """
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
        case AddressNode():
            child = node.children[0]
            symbol_table_type = symbol_table.find_entry(child.value).type
            match symbol_table_type:
                case SymbolTableEntryType.Int:
                    return ir.IntType(32)
                case SymbolTableEntryType.Float:
                    return ir.FloatType()
                case SymbolTableEntryType.String:
                    return ir.ArrayType(ir.IntType(8), 0)
                case SymbolTableEntryType.Bool:
                    return ir.IntType(1)
                case SymbolTableEntryType.Char:
                    return ir.IntType(8)
                case _:
                    raise Exception(f"Unknown type: {symbol_table_type}")
        case PointerNode():
            # dereference!
            return node_to_llvmtype(node.children[0], symbol_table)
        case FloatPointerNode():
            type = ir.FloatType().as_pointer()
            for _ in range(node.depth - 1):
                type = type.as_pointer()
            return ir.FloatType()
        case IntPointerNode():
            type = ir.IntType(32).as_pointer()
            for _ in range(node.depth - 1):
                type = type.as_pointer()
            return ir.IntType(32)
        case CharPointerNode():
            type = ir.IntType(8).as_pointer()
            for _ in range(node.depth - 1):
                type = type.as_pointer()
            return ir.IntType(8)
        case BoolPointerNode():
            type = ir.IntType(1).as_pointer()
            for _ in range(node.depth - 1):
                type = type.as_pointer()
            return ir.IntType(1)
        case LShiftNode():
            return ir.IntType(32)
        case AssignNode():
            return node_to_llvmtype(node.children[1], symbol_table)
        case RShiftNode():
            return ir.IntType(32)
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
        case AndNode():
            return ir.IntType(1)
        case OrNode():
            return ir.IntType(1)
        case NotNode():
            return ir.IntType(1)
        case ModNode():
            return ir.IntType(32)
        case CharNode():
            return ir.IntType(8)
        case IdNode():
            symbol_table_type = symbol_table.find_entry(node.value).type
            match symbol_table_type:
                case SymbolTableEntryType.Int:
                    return ir.IntType(32)
                case SymbolTableEntryType.Float:
                    return ir.FloatType()
                case SymbolTableEntryType.String:
                    return ir.ArrayType(ir.IntType(8), 0)
                case SymbolTableEntryType.Bool:
                    return ir.IntType(1)
                case SymbolTableEntryType.Char:
                    return ir.IntType(8)
                case _:
                    raise Exception(f"Unknown type: {symbol_table_type}")
        case ConvertNode():
            match node.children[0].value:
                case "int":
                    return ir.IntType(32)
                case "float":
                    return ir.FloatType()
                case "char":
                    return ir.IntType(8)
                case "bool":
                    return ir.IntType(1)
                case _:
                    raise ValueError(f"Invalid type: {node.children[0].value}")
        case _:
            raise Exception(f"Unknown type: {node}")


class LlvmConverter:
    def __init__(self, symbol_table: SymbolTable, input_file_path: str):
        self.blocks = []
        self.builders = []

        # Get the target triple using llvm-config
        try:
            target_triple = (
                subprocess.check_output(["llvm-config", "--host-target"])
                .decode()
                .strip()
            )
        except:
            target_triple = ""
        self.module = ir.Module("module")
        self.module.triple = target_triple
        self.input_file_lines = open(input_file_path).readlines()

        self.commented_lines = {}

        voidptr_ty = ir.IntType(8).as_pointer()
        printf_ty = ir.FunctionType(ir.IntType(32), [voidptr_ty], var_arg=True)
        printf = ir.Function(self.module, printf_ty, name="printf")

        self.symbol_table = symbol_table

    def add_statement_comment(self, node: TreeNode) -> None:
        if node.line_nr is None:
            return
        if node.line_nr in self.commented_lines:
            return
        self.commented_lines[node.line_nr] = True
        try:
            builder = self.builders[-1]
        except:
            return
        # get line from input file
        line = self.input_file_lines[node.line_nr - 1].strip()
        builder.comment(f"Line {node.line_nr}: {line}")

    def store_value(self, value: TreeNode, llvm_var: ir.Value, depth: int = 0) -> None:
        """
        Store the value of a node in a llvm variable
        :param value: TreeNode to store
        :param llvm_var: llvmlite variable to store the value in
        :return: None
        """
        builder = self.builders[-1]

        match value:
            case IntNode():
                pointer_depth = llvm_var.type.intrinsic_name.count("p0")
                if pointer_depth <= 1:
                    builder.store(
                        ir.Constant(ir.IntType(32), int(value.value)), llvm_var
                    )
                else:
                    builder.gep(
                        llvm_var, [ir.Constant(ir.IntType(32), int(value.value))]
                    )
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
            case CharNode():
                if len(value.value) == 4:
                    # escape character e.g. '\\n'
                    value.value = value.value.encode("utf-8").decode("unicode_escape")

                builder.store(
                    ir.Constant(ir.IntType(8), ord(value.value[1:-1])), llvm_var
                )
            case IdNode():
                if depth != 0:
                    # find variable depth
                    variable_depth = llvm_var.type.intrinsic_name.count("p0")
                    # find value depth
                    value_depth = self.symbol_table.find_entry(
                        value.value
                    ).llvm_var.type.intrinsic_name.count("p0")
                    var = self.symbol_table.find_entry(value.value).llvm_var
                    for _ in range(variable_depth - value_depth + 1):
                        var = builder.load(var)
                    builder.store(var, llvm_var)
                    return
                builder.store(
                    builder.load(self.symbol_table.find_entry(value.value).llvm_var),
                    llvm_var,
                )
            case AddressNode():
                child = value.children[0]
                # check for pointer depth
                pointer_depth = depth

                symbol_table_entry = self.symbol_table.find_entry(child.value)
                symbol_table_llvm_var = symbol_table_entry.llvm_var
                var = symbol_table_llvm_var
                builder.store(var, llvm_var)
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
            case LShiftNode():
                left = self.node_to_llvm(value.children[0])
                right = self.node_to_llvm(value.children[1])
                builder.store(builder.shl(left, right), llvm_var)
            case RShiftNode():
                left = self.node_to_llvm(value.children[0])
                right = self.node_to_llvm(value.children[1])
                builder.store(builder.ashr(left, right), llvm_var)
            case NeqNode():
                left = self.node_to_llvm(value.children[0])
                right = self.node_to_llvm(value.children[1])
                try:
                    type = self.symbol_table.find_entry(value.children[0].value).type
                except:
                    # address node
                    address_to = self.symbol_table.find_entry(
                        value.children[0].children[0].value
                    )
                    addres_to_llvm_var = address_to.llvm_var

                    builder.store(
                        builder.icmp_signed("!=", addres_to_llvm_var, right), llvm_var
                    )
                    return

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
            case AndNode():
                left = self.node_to_llvm(value.children[0])
                right = self.node_to_llvm(value.children[1])
                builder.store(builder.and_(left, right), llvm_var)
            case OrNode():
                left = self.node_to_llvm(value.children[0])
                right = self.node_to_llvm(value.children[1])
                builder.store(builder.or_(left, right), llvm_var)
            case NotNode():
                child = self.node_to_llvm(value.children[0])
                builder.store(builder.not_(child), llvm_var)
            case PointerNode():
                # dereference
                pointer_depth = value.depth
                pointer_loc = self.symbol_table.find_entry(
                    value.children[0].value
                ).llvm_var
                pointee = builder.load(pointer_loc)
                for _ in range(pointer_depth - 1):
                    pointee = builder.load(pointee)
                builder.store(builder.load(pointee), llvm_var)

            case AssignNode():
                # e.g. int a = number++;
                value = value.children[1]
                self.store_value(value, llvm_var)

            case ConvertNode():
                to_type: str = value.children[0].value
                from_type = None
                match value.children[1]:
                    case IdNode():
                        from_type = self.symbol_table.find_entry(
                            value.children[1].value
                        ).type
                        match from_type:
                            case SymbolTableEntryType.Int:
                                from_type = ir.IntType(32)
                            case SymbolTableEntryType.Float:
                                from_type = ir.FloatType()
                            case SymbolTableEntryType.Char:
                                from_type = ir.IntType(8)
                            case SymbolTableEntryType.Bool:
                                from_type = ir.IntType(1)
                    case PlusNode():
                        from_type = node_to_llvmtype(
                            value.children[1], self.symbol_table
                        )
                    case MultNode():
                        from_type = node_to_llvmtype(
                            value.children[1], self.symbol_table
                        )
                    case DivNode():
                        from_type = node_to_llvmtype(
                            value.children[1], self.symbol_table
                        )
                    case MinusNode():
                        from_type = node_to_llvmtype(
                            value.children[1], self.symbol_table
                        )

                    case _:
                        raise Exception(f"from type?? : {value.children[1]}")

                if to_type == "int":
                    match from_type:
                        case ir.IntType(32):
                            builder.store(
                                builder.zext(
                                    self.node_to_llvm(value.children[1]), ir.IntType(32)
                                ),
                                llvm_var,
                            )
                        case ir.FloatType():
                            builder.store(
                                builder.fptosi(
                                    self.node_to_llvm(value.children[1]), ir.IntType(32)
                                ),
                                llvm_var,
                            )
                        case ir.IntType(8):
                            builder.store(
                                builder.zext(
                                    self.node_to_llvm(value.children[1]), ir.IntType(32)
                                ),
                                llvm_var,
                            )
                        case ir.IntType(1):
                            builder.store(
                                builder.zext(
                                    self.node_to_llvm(value.children[1]), ir.IntType(32)
                                ),
                                llvm_var,
                            )
                if to_type == "float":
                    match from_type:
                        case ir.IntType():
                            builder.store(
                                builder.sitofp(
                                    self.node_to_llvm(value.children[1]), ir.FloatType()
                                ),
                                llvm_var,
                            )
                        case ir.FloatType():
                            builder.store(
                                self.node_to_llvm(value.children[1]),
                                llvm_var,
                            )
                        case ir.IntType(8):
                            builder.store(
                                builder.sitofp(
                                    self.node_to_llvm(value.children[1]), ir.FloatType()
                                ),
                                llvm_var,
                            )
                        case ir.IntType(1):
                            builder.store(
                                builder.sitofp(
                                    self.node_to_llvm(value.children[1]), ir.FloatType()
                                ),
                                llvm_var,
                            )
                if to_type == "char":
                    match from_type:
                        case ir.IntType(32):
                            builder.store(
                                builder.trunc(
                                    self.node_to_llvm(value.children[1]), ir.IntType(8)
                                ),
                                llvm_var,
                            )
                        case ir.FloatType():
                            builder.store(
                                builder.trunc(
                                    self.node_to_llvm(value.children[1]), ir.IntType(8)
                                ),
                                llvm_var,
                            )
                        case ir.IntType(8):
                            builder.store(
                                self.node_to_llvm(value.children[1]),
                                llvm_var,
                            )
                        case ir.IntType(1):
                            builder.store(
                                builder.trunc(
                                    self.node_to_llvm(value.children[1]), ir.IntType(8)
                                ),
                                llvm_var,
                            )
                if to_type == "bool":
                    match from_type:
                        case ir.IntType(32):
                            builder.store(
                                builder.trunc(
                                    self.node_to_llvm(value.children[1]), ir.IntType(1)
                                ),
                                llvm_var,
                            )
                        case ir.FloatType():
                            builder.store(
                                builder.trunc(
                                    self.node_to_llvm(value.children[1]), ir.IntType(1)
                                ),
                                llvm_var,
                            )
                        case ir.IntType(8):
                            builder.store(
                                builder.trunc(
                                    self.node_to_llvm(value.children[1]), ir.IntType(1)
                                ),
                                llvm_var,
                            )
                        case ir.IntType(1):
                            builder.store(
                                self.node_to_llvm(value.children[1]),
                                llvm_var,
                            )

            case _:
                raise Exception(f"Unknown type at Generation of assignment: {value}")

    def node_to_llvm(self, node: TreeNode, load: bool = True) -> ir.Value:
        """
        Convert a TreeNode to a llvmlite ir.Value
        The value is also immediately saved in the llvm code
        :param node: Treenode to convert
        :return: ir.Value : The converted node
        """
        builder = self.builders[-1]
        match node:
            case IntNode():
                return ir.Constant(ir.IntType(32), int(node.value))
            case FloatNode():
                return ir.Constant(ir.FloatType(), float(node.value))
            case IdNode():
                if load:
                    return builder.load(
                        self.symbol_table.find_entry(node.value).llvm_var
                    )
                return self.symbol_table.find_entry(node.value).llvm_var
            case PointerNode():
                # dereference, check pointer depth!
                pointer_depth = node.depth
                pointer_loc = self.symbol_table.find_entry(
                    node.children[0].value
                ).llvm_var
                pointee = builder.load(pointer_loc)
                for _ in range(pointer_depth - 1):
                    pointee = builder.load(pointee)
                return builder.load(pointee)
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
            case LShiftNode():
                left = self.node_to_llvm(node.children[0])
                right = self.node_to_llvm(node.children[1])
                return builder.shl(left, right)
            case RShiftNode():
                left = self.node_to_llvm(node.children[0])
                right = self.node_to_llvm(node.children[1])
                return builder.ashr(left, right)
            case EqualNode():
                left = self.node_to_llvm(node.children[0])
                right = self.node_to_llvm(node.children[1])
                type = self.symbol_table.find_entry(node.children[0].value).type
                if type == SymbolTableEntryType.Int:
                    return builder.icmp_signed("==", left, right)
                elif type == SymbolTableEntryType.Float:
                    return builder.fcmp_ordered("==", left, right)
                else:
                    raise Exception(f"Unknown type: {type}")
            case GtNode():
                left = self.node_to_llvm(node.children[0])
                right = self.node_to_llvm(node.children[1])
                type = self.symbol_table.find_entry(node.children[0].value).type
                if type == SymbolTableEntryType.Int:
                    return builder.icmp_signed(">", left, right)
                elif type == SymbolTableEntryType.Float:
                    return builder.fcmp_ordered(">", left, right)
                else:
                    raise Exception(f"Unknown type: {type}")
            case LtNode():
                left = self.node_to_llvm(node.children[0])
                right = self.node_to_llvm(node.children[1])
                type = self.symbol_table.find_entry(node.children[0].value).type
                if type == SymbolTableEntryType.Int:
                    return builder.icmp_signed("<", left, right)
                elif type == SymbolTableEntryType.Float:
                    return builder.fcmp_ordered("<", left, right)
                else:
                    raise Exception(f"Unknown type: {type}")
            case GeqNode():
                left = self.node_to_llvm(node.children[0])
                right = self.node_to_llvm(node.children[1])
                type = self.symbol_table.find_entry(node.children[0].value).type
                if type == SymbolTableEntryType.Int:
                    return builder.icmp_signed(">=", left, right)
                elif type == SymbolTableEntryType.Float:
                    return builder.fcmp_ordered(">=", left, right)
                else:
                    raise Exception(f"Unknown type: {type}")
            case LeqNode():
                left = self.node_to_llvm(node.children[0])
                right = self.node_to_llvm(node.children[1])
                type = self.symbol_table.find_entry(node.children[0].value).type
                if type == SymbolTableEntryType.Int:
                    return builder.icmp_signed("<=", left, right)
                elif type == SymbolTableEntryType.Float:
                    return builder.fcmp_ordered("<=", left, right)
                else:
                    raise Exception(f"Unknown type: {type}")
            case AndNode():
                left = self.node_to_llvm(node.children[0])
                right = self.node_to_llvm(node.children[1])
                return builder.and_(left, right)
            case OrNode():
                left = self.node_to_llvm(node.children[0])
                right = self.node_to_llvm(node.children[1])
                return builder.or_(left, right)
            case NotNode():
                child = self.node_to_llvm(node.children[0])
                return builder.not_(child)
            case CharNode():
                return ir.Constant(ir.IntType(8), ord(node.value[1:-1]))
            case AddressNode():
                child = node.children[0]
                symbol_table_entry = self.symbol_table.find_entry(child.value)
                return symbol_table_entry.llvm_var
            case AssignNode():
                left = node.children[0]
                right = node.children[1]
                left_llvm = self.node_to_llvm(left, load=False)
                right_llvm = self.node_to_llvm(right)
                builder.store(right_llvm, left_llvm)
                return right_llvm
            case _:
                raise Exception(f"Unknown type: {node}")

    def addition(self, node: TreeNode) -> ir.Value:
        """
        Convert a PlusNode to a llvmlite ir.Value
        :param node: PlusNode to convert
        :return: ir.Value : The converted node
        """
        builder = self.builders[-1]
        left = node.children[0]
        right = node.children[1]

        left_llvm = self.node_to_llvm(left)
        right_llvm = self.node_to_llvm(right)

        if left_llvm.type.intrinsic_name.count("p0") != 0:
            var = builder.gep(left_llvm, [right_llvm])
            return var

        if (
            left_llvm.type.intrinsic_name == "f32"
            or right_llvm.type.intrinsic_name == "f32"
        ):
            var = builder.fadd(left_llvm, right_llvm)
            return var

        var = builder.add(left_llvm, right_llvm)

        return var

    def multiplication(self, node: TreeNode) -> ir.Value:
        """
        Convert a MultNode to a llvmlite ir.Value
        :param node: MultNode to convert
        :return: ir.Value : The converted node
        """
        builder = self.builders[-1]
        left = node.children[0]
        right = node.children[1]

        left_llvm = self.node_to_llvm(left)
        right_llvm = self.node_to_llvm(right)

        if (
            left_llvm.type.intrinsic_name == "f32"
            or right_llvm.type.intrinsic_name == "f32"
        ):
            var = builder.fmul(left_llvm, right_llvm)
            return var

        var = builder.mul(left_llvm, right_llvm)
        return var

    def division(self, node: TreeNode) -> ir.Value:
        """
        Convert a DivNode to a llvmlite ir.Value
        :param node: DivNode to convert
        :return: ir.Value : The converted node
        """
        builder = self.builders[-1]
        left = node.children[0]
        right = node.children[1]

        left_llvm = self.node_to_llvm(left)
        right_llvm = self.node_to_llvm(right)

        if (
            left_llvm.type.intrinsic_name == "f32"
            or right_llvm.type.intrinsic_name == "f32"
        ):
            var = builder.fdiv(left_llvm, right_llvm)
            return var

        var = builder.udiv(left_llvm, right_llvm)

        return var

    def subtraction(self, node: TreeNode) -> ir.Value:
        """
        Convert a MinusNode to a llvmlite ir.Value
        :param node: MinusNode: to convert
        :return: Ir.Value : The converted node
        """
        builder = self.builders[-1]
        left = node.children[0]
        right = node.children[1]

        left_llvm = self.node_to_llvm(left)

        # check for pointers
        if left_llvm.type.intrinsic_name.count("p0") != 0:
            right.value = str(-int(right.value))
            right_llvm = self.node_to_llvm(right)
            var = builder.gep(left_llvm, [right_llvm])
            return var
        right_llvm = self.node_to_llvm(right)

        if (
            left_llvm.type.intrinsic_name == "f32"
            or right_llvm.type.intrinsic_name == "f32"
        ):
            var = builder.fsub(left_llvm, right_llvm)
            return var

        var = builder.sub(left_llvm, right_llvm)

        return var

    def convert(self, node: TreeNode) -> None:
        """
        Convert the AST to llvm code, always give the root of the AST to this function
        Llvm code can be retrieved by calling return_llvm_code() afterwards
        :param node: The root of the AST
        :return: None
        """
        match node:
            case MainNode():
                function = ir.Function(
                    self.module, ir.FunctionType(ir.IntType(32), []), "main"
                )
                self.blocks.append(function.append_basic_block("main"))
                self.builders.append(ir.IRBuilder(self.blocks[-1]))

            case AssignNode():
                if node.converted:
                    return
                if isinstance(node.children[0], PointerNode):
                    # dereference pointer
                    pointer_depth = node.children[0].depth
                    pointee = self.symbol_table.find_entry(
                        node.children[0].children[0].value
                    ).llvm_var
                    for _ in range(pointer_depth - 1):
                        pointee = self.builders[-1].load(pointee)
                    assignee = self.builders[-1].load(pointee)
                else:
                    assignee = self.symbol_table.find_entry(
                        node.children[0].value
                    ).llvm_var
                value = node.children[1]

                # make sure we dont do assignment twice when doing something like int a = number++;
                node.converted = True
                if isinstance(value, AssignNode):
                    value.converted = True

                self.store_value(value, assignee)

            case NewVariableNode():
                const_var: bool = len(node.children) == 4
                pointer_depth = 0
                if const_var:
                    if isinstance(
                        node.children[2],
                        (
                            IntPointerNode,
                            FloatPointerNode,
                            CharPointerNode,
                            BoolPointerNode,
                        ),
                    ):
                        # take pointer depth in accoun
                        var_node = node.children[2]
                        pointer_depth = var_node.depth
                        var_name = var_node.children[0].value
                    else:
                        var_name = node.children[2].value
                else:
                    if isinstance(
                        node.children[1],
                        (
                            IntPointerNode,
                            FloatPointerNode,
                            CharPointerNode,
                            BoolPointerNode,
                        ),
                    ):
                        var_node = node.children[1]
                        pointer_depth = var_node.depth
                        var_name = var_node.children[0].value
                    else:
                        var_name = node.children[1].value

                try:
                    builder = self.builders[-1]
                except:
                    # global variable
                    var = ir.GlobalVariable(
                        self.module,
                        node_to_llvmtype(node.children[2], self.symbol_table),
                        var_name,
                    )
                    value_ast = node.children[3] if const_var else node.children[2]
                    match value_ast:
                        case IntNode():
                            value = ir.Constant(ir.IntType(32), int(value_ast.value))
                        case FloatNode():
                            value = ir.Constant(ir.FloatType(), float(value_ast.value))
                        case CharNode():
                            value = ir.Constant(
                                ir.ArrayType(ir.IntType(8), 1),
                                bytearray(value_ast.value.encode("utf-8")),
                            )
                        case _:
                            raise Exception("Converter.py:433")
                    var.initializer = value
                    return

                symbol_table_entry = self.symbol_table.find_entry(var_name)
                var_type = node_to_llvmtype(node.children[2], self.symbol_table)

                for _ in range(pointer_depth):
                    var_type = var_type.as_pointer()

                var = builder.alloca(var_type, name=var_name)

                symbol_table_entry.llvm_var = var
                value = node.children[3] if const_var else node.children[2]

                # check if value is a pointer
                try:
                    self.store_value(value, var, depth=pointer_depth)
                except:
                    # and with integers
                    var = builder.alloca(ir.IntType(32), name=var_name)
                    symbol_table_entry.llvm_var = var
                    self.store_value(value, var, depth=pointer_depth)

            case PrintfNode():
                builder = self.builders[-1]
                printf_str = node.children[0].value[1:-1]
                printf_str = printf_str.replace("\\n", "\x0A")
                printf_str += "\00"

                fmt_str = ir.GlobalVariable(
                    self.module,
                    ir.ArrayType(ir.IntType(8), len(printf_str)),
                    name=f".str{id(node)}",
                )

                fmt_str.initializer = ir.Constant(
                    ir.ArrayType(ir.IntType(8), len(printf_str)),
                    bytearray(printf_str.encode("utf-8")),
                )

                fmt_str_pointer = builder.bitcast(
                    fmt_str, ir.PointerType(ir.IntType(8), 0), name="fmt_str"
                )

                vars = [child for child in node.children[1:]]
                llvm_vars = []
                for var in vars:
                    llvm_vars.append(self.node_to_llvm(var))

                args = [fmt_str_pointer] + llvm_vars

                builder.call(
                    self.module.get_global("printf"),
                    args,
                )

            case CommentNode():
                comment_value = node.value[2:]
                # split comment into multiple lines
                comment_lines = comment_value.split("\n")
                try:
                    builder = self.builders[-1]
                except:
                    return
                for comment_line in comment_lines:
                    if comment_line.strip() == "*/" or comment_line == "":
                        continue
                    builder.comment(comment_line)

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
        self.add_statement_comment(node)

        for child in node.children:
            self.convert(child)

    def return_llvm_code(self) -> str:
        """
        Return the generated llvm code
        :return: str : The generated llvm code
        """
        return str(self.module)
