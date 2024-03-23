from enum import Enum
from src.parser.TreeNode import *
from llvmlite import ir


class SymbolTableEntryType(Enum):
    Int = "int"
    Float = "float"
    Char = "char"
    String = "string"
    Bool = "bool"


class SymbolTableEntry:
    def __init__(
        self,
        name: str,
        type: SymbolTableEntryType,
        const: bool = False,
        llvm_var=None,
    ) -> None:
        self.name: str = name
        self.type: SymbolTableEntryType = type
        self.llvm_var = llvm_var
        self.const: bool = const


class Table:
    def __init__(self, parent_id: int = -1):
        self.table: list[SymbolTableEntry] = []
        self.parent_id: int = parent_id
        self.type: SymbolTableEntryType = type  # TreeNode type

    def add_entry(self, entry: SymbolTableEntry):
        self.table.append(entry)


class SymbolTable:
    pass


def node_to_symbolTableEntryType(
    node: TreeNode, symbol_table: SymbolTable
) -> SymbolTableEntryType:
    """
    Returns the SymbolTableEntryType of a given node
    :param node: Node to find the type of
    :param symbol_table: The symboltable to look up the type of an id
    :return:
    """
    if isinstance(node, IntNode):
        return SymbolTableEntryType.Int
    if isinstance(node, FloatNode):
        return SymbolTableEntryType.Float
    if isinstance(node, StringNode):
        return SymbolTableEntryType.String
    if isinstance(node, (PlusNode, MultNode, DivNode, MinusNode)):
        return node_to_symbolTableEntryType(node.children[0], symbol_table)
    if isinstance(node, IdNode):
        return symbol_table.find_entry(node.value).type
    if isinstance(node, EqualNode):
        return SymbolTableEntryType.Bool
    raise ValueError(f"Invalid node type: {node.__class__.__name__}")


class SymbolTable:
    def __init__(self) -> None:
        self.tables: list[Table] = [
            Table()
        ]  # Root table of program is always at index 0
        self.current_idx: int = 0

    def build_symbol_table(self, tree: TreeNode) -> None:
        if isinstance(tree, MainNode):
            self.tables.append(Table(parent_id=self.current_idx))
            self.current_idx = len(self.tables) - 1

        if isinstance(tree, NewVariableNode):
            if self.find_entry_in_current_scope(tree.children[0].value):
                raise ValueError(f"error: redefinition of '{tree.children[0].value}'")
            self.tables[self.current_idx].add_entry(
                SymbolTableEntry(
                    tree.children[0].value,
                    node_to_symbolTableEntryType(tree.children[1], self),
                )
            )
        for child in tree.children:
            self.build_symbol_table(child)

    def find_entry(self, name: str) -> SymbolTableEntry | None:
        table_idx = self.current_idx
        while table_idx != -1:
            table = self.tables[table_idx].table
            for entry in table:
                if entry.name == name:
                    return entry
            table_idx = self.tables[table_idx].parent_id
        return None

    def find_entry_in_current_scope(self, name: str) -> SymbolTableEntry | None:
        table = self.tables[self.current_idx].table
        for entry in table:
            if entry.name == name:
                return entry
        return None
