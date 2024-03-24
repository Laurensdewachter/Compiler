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
    def analyze(ast: TreeNode, symbol_table: SymbolTable, errors=None) -> list[str]:
        if errors is None:
            errors = []

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

        # Check for incorrect type definitions at assignments of existing variables
        if isinstance(ast, AssignNode):
            id_node = ast.children[0]
            value_node = ast.children[1]
            table_entry = symbol_table.find_entry(id_node.value)
            if table_entry.type != node_to_symbolTableEntryType(
                value_node, symbol_table
            ):
                errors.append(
                    f"Assignment of '{id_node.value}' on line {id_node.line_nr} does not match type {table_entry.type.name} defined in line {table_entry.declaration_line}."
                )

        # Check for incompatible types in operations
        if isinstance(ast, (PlusNode, MinusNode, MultNode, DivNode, ModNode)):
            left_node = ast.children[0]
            right_node = ast.children[1]
            if isinstance(left_node, IdNode):
                left_type = symbol_table.find_entry(left_node.value).type
            else:
                left_type = match_type(left_node)
            if isinstance(right_node, IdNode):
                right_type = symbol_table.find_entry(right_node.value).type
            else:
                right_type = match_type(right_node)

            if left_type != right_type and not (
                left_type in (SymbolTableEntryType.Int, SymbolTableEntryType.Float)
                and right_type in (SymbolTableEntryType.Int, SymbolTableEntryType.Float)
            ):
                errors.append(
                    f"Operation between {left_type.name} and {right_type.name} at line {ast.line_nr} is not supported."
                )

        for child in ast.children:
            SemanticAnalyzer.analyze(child, symbol_table, errors)

        return errors
