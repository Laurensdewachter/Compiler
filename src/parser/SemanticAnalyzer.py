from src.parser.TreeNode import *
from src.parser.SymbolTable import (
    SymbolTable,
    node_to_symbolTableEntryType,
    SymbolTableEntryType,
)


def match_type(node: TreeNode) -> SymbolTableEntryType:
    if isinstance(node, IntNode):
        return SymbolTableEntryType.Int
    elif isinstance(node, FloatNode):
        return SymbolTableEntryType.Float
    elif isinstance(node, CharNode):
        return SymbolTableEntryType.Char
    elif isinstance(node, BoolNode):
        return SymbolTableEntryType.Bool


class SemanticAnalyzer:
    def __init__(self):
        pass

    @staticmethod
    def analyze(
        ast: TreeNode, symbol_table: SymbolTable, errors=None, warnings=None
    ) -> (list[str], list[str]):
        if errors is None:
            errors = []
        if warnings is None:
            warnings = []

        # Check for undeclared variable
        if not isinstance(ast, NewVariableNode):
            for child in ast.children:
                if (
                    isinstance(child, IdNode)
                    and symbol_table.find_entry(child.value) is None
                ):
                    errors.append(
                        f"Variable '{child.value}' on line {child.line_nr} is not defined."
                    )

        # Check for incorrect type definitions at new assignments
        if isinstance(ast, NewVariableNode):
            type_node = ast.children[0]
            id_node = ast.children[1]
            value_node = ast.children[2]
            if isinstance(type_node, ConstNode):
                type_node = ast.children[1]
                id_node = ast.children[2]
                value_node = ast.children[3]

            if isinstance(value_node, (IntNode, FloatNode, CharNode, BoolNode)):
                match type_node.value:
                    case "int":
                        if not isinstance(value_node, (FloatNode, IntNode, CharNode)):
                            errors.append(
                                f"Variable '{id_node.value}' on line {id_node.line_nr} was declared as an int, but used as {match_type(value_node).name}."
                            )
                    case "float":
                        if not isinstance(value_node, (FloatNode, IntNode, CharNode)):
                            errors.append(
                                f"Variable '{id_node.value}' on line {id_node.line_nr} was declared as a float but used as a {match_type(value_node).name}."
                            )
                    case "char":
                        if not isinstance(value_node, (FloatNode, IntNode, CharNode)):
                            errors.append(
                                f"Variable '{id_node.value}' on line {id_node.line_nr} was declared as a char but used as a {match_type(value_node).name}."
                            )
                    case "bool":
                        if not isinstance(value_node, BoolNode):
                            errors.append(
                                f"Variable '{id_node.value}' on line {id_node.line_nr} was declared as a bool but used as a {match_type(value_node).name}."
                            )

        if isinstance(ast, AssignNode):
            id_node = ast.children[0]
            table_entry = symbol_table.find_entry(id_node.value)
            if table_entry is not None and table_entry.const:
                errors.append(
                    f"Reassignment of constant variable '{id_node.value}' on line {id_node.line_nr}."
                )

        # Implicit conversions
        # New variables
        if isinstance(ast, NewVariableNode):
            type_node = ast.children[0]
            value_node = ast.children[2]
            constant = False
            if isinstance(type_node, ConstNode):
                constant = True
                type_node = ast.children[1]
                value_node = ast.children[3]
            if type_node.value == "int" and isinstance(value_node, FloatNode):
                warnings.append(
                    f"Warning: Conversion from type float to int on line {type_node.line_nr} may cause loss of information."
                )
                new_node = IntNode(
                    str(int(float(value_node.value))),
                    value_node.children,
                    value_node.line_nr,
                )
                if constant:
                    ast.children[3] = new_node
                else:
                    ast.children[2] = new_node
            if type_node.value == "char":
                if isinstance(value_node, FloatNode):
                    warnings.append(
                        f"Warning: Conversion from type float to char on line {type_node.line_nr} may cause loss of information."
                    )
                    new_node = CharNode(
                        str(chr(int(float(value_node.value)))),
                        value_node.children,
                        value_node.line_nr,
                    )
                    if constant:
                        ast.children[3] = new_node
                    else:
                        ast.children[2] = new_node
                elif isinstance(value_node, IntNode):
                    warnings.append(
                        f"Warning: Conversion from type int to char on line {type_node.line_nr} may cause loss of information."
                    )
                    new_node = CharNode(
                        str(chr(int(value_node.value))),
                        value_node.children,
                        value_node.line_nr,
                    )
                    if constant:
                        ast.children[3] = new_node
                    else:
                        ast.children[2] = new_node

        # Implicit conversions
        # Assignments
        elif isinstance(ast, AssignNode):
            left_node = ast.children[0]
            right_node = ast.children[1]
            lvalue_entry = symbol_table.find_entry(left_node.value)
            lvalue_type = lvalue_entry.type
            rvalue_type = None
            # Rvalue is an id
            if isinstance(ast.children[1], IdNode):
                rvalue_entry = symbol_table.find_entry(right_node.value)
                rvalue_type = rvalue_entry.type
            # Rvalue is a literal
            elif isinstance(ast.children[1], (IntNode, FloatNode, CharNode, BoolNode)):
                rvalue_type = match_type(right_node)
            # Types are different
            if rvalue_type is not None and lvalue_type != rvalue_type:
                # Lvalue float, rvalue int or char
                if lvalue_type == SymbolTableEntryType.Float and (
                    rvalue_type == SymbolTableEntryType.Int
                    or rvalue_type == SymbolTableEntryType.Bool
                ):
                    new_node = FloatNode(
                        str(float(int(right_node.value))),
                        right_node.children,
                        right_node.line_nr,
                    )
                    ast.children[1] = new_node
                # Lvalue int, rvalue float
                elif (
                    lvalue_type == SymbolTableEntryType.Int
                    and rvalue_type == SymbolTableEntryType.Float
                ):
                    warnings.append(
                        f"Warning: Conversion from type float to int on line {left_node.line_nr} may cause loss of information."
                    )
                    new_node = IntNode(
                        str(int(float(right_node.value))),
                        right_node.children,
                        right_node.line_nr,
                    )
                    ast.children[1] = new_node
                # Lvalue int, rvalue char
                elif (
                    lvalue_type == SymbolTableEntryType.Int
                    and rvalue_type == SymbolTableEntryType.Char
                ):
                    new_node = IntNode(
                        str(int(right_node.value)),
                        right_node.children,
                        right_node.line_nr,
                    )
                    ast.children[1] = new_node
                # Lvalue char, rvalue float or int
                elif lvalue_type == SymbolTableEntryType.Char and (
                    rvalue_type == SymbolTableEntryType.Float
                    or rvalue_type == SymbolTableEntryType.Int
                ):
                    warnings.append(
                        f"Warning: Conversion from type {rvalue_type.name} to int on line {left_node.line_nr} may cause loss of information."
                    )
                    new_node = IntNode(
                        str(chr(int(float(right_node.value)))),
                        right_node.children,
                        right_node.line_nr,
                    )
                    ast.children[1] = new_node
                # Lvalue bool, rvalue not bool
                elif lvalue_type != rvalue_type:
                    errors.append(
                        f"Assignment of '{left_node.value}' on line {left_node.line_nr} does not match type {lvalue_type.name} defined in line {lvalue_entry.declaration_line}."
                    )

        for child in ast.children:
            SemanticAnalyzer.analyze(child, symbol_table, errors, warnings)

        return errors, warnings
