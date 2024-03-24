from src.parser.TreeNode import *
from src.parser.SymbolTable import SymbolTable, node_to_symbolTableEntryType


def match_type(node: TreeNode) -> str:
    if isinstance(node, IntNode):
        return "int"
    elif isinstance(node, FloatNode):
        return "float"
    elif isinstance(node, CharNode):
        return "char"
    elif isinstance(node, BoolNode):
        return "bool"
    else:
        return "undefined"


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
                            f"Variable '{id_node.value}' on line {id_node.line_nr} was declared as an int, but used as {match_type(value_node)}."
                        )
                case "float":
                    if not isinstance(value_node, (FloatNode, IntNode, CharNode)):
                        errors.append(
                            f"Variable '{id_node.value}' on line {id_node.line_nr} was declared as a float but used as a {match_type(value_node)}."
                        )
                case "char":
                    if not isinstance(value_node, (FloatNode, IntNode, CharNode)):
                        errors.append(
                            f"Variable '{id_node.value}' on line {id_node.line_nr} was declared as a char but used as a {match_type(value_node)}."
                        )
                case "bool":
                    if not isinstance(value_node, BoolNode):
                        errors.append(
                            f"Variable '{id_node.value}' on line {id_node.line_nr} was declared as a char but used as a {match_type(value_node)}."
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

        for child in ast.children:
            SemanticAnalyzer.analyze(child, symbol_table, errors)

        return errors
