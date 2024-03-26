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
        declaration_line: int = -1,
        llvm_var: ir.Value = None,
    ) -> None:
        self.name: str = name
        self.type: SymbolTableEntryType = type
        self.const: bool = const
        self.declaration_line: int = declaration_line
        self.llvm_var: ir.Value = llvm_var


class Table:
    def __init__(self, parent_id: int = -1):
        self.table: list[SymbolTableEntry] = []
        self.parent_id: int = parent_id
        self.type: SymbolTableEntryType = type  # TreeNode type

    def __repr__(self) -> str:
        string: str = ""
        for entry in self.table:
            string += (
                f"id: {entry.name}, type: {entry.type.name}, constant: {entry.const}\n"
            )
        return string

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
    if isinstance(node, CharNode):
        return SymbolTableEntryType.Char
    if isinstance(node, (PlusNode, MultNode, DivNode, MinusNode)):
        return node_to_symbolTableEntryType(node.children[0], symbol_table)
    if isinstance(node, IdNode):
        return symbol_table.find_entry(node.value).type
    if isinstance(node, EqualNode):
        return SymbolTableEntryType.Bool
    if isinstance(node, NeqNode):
        return SymbolTableEntryType.Bool
    if isinstance(node, LtNode):
        return SymbolTableEntryType.Bool
    if isinstance(node, GtNode):
        return SymbolTableEntryType.Bool
    if isinstance(node, LeqNode):
        return SymbolTableEntryType.Bool
    if isinstance(node, GeqNode):
        return SymbolTableEntryType.Bool
    if isinstance(node, ModNode):
        return SymbolTableEntryType.Int
    if isinstance(node, AndNode):
        return SymbolTableEntryType.Bool
    if isinstance(node, OrNode):
        return SymbolTableEntryType.Bool
    if isinstance(node, NotNode):
        return SymbolTableEntryType.Bool
    if isinstance(node, CharNode):
        return SymbolTableEntryType.Char
    if isinstance(node, BoolNode):
        return SymbolTableEntryType.Bool
    if isinstance(node, AddressNode):
        return node_to_symbolTableEntryType(node.children[0], symbol_table)

    raise ValueError(f"Invalid node type: {node.__class__.__name__}")


class SymbolTable:
    def __init__(self) -> None:
        self.tables: list[Table] = [
            Table()
        ]  # Root table of program is always at index 0
        self.current_idx: int = 0

    def __str__(self):
        starting_index = self.current_idx
        self.current_idx = 0
        string: str = ""
        for table in self.tables:
            string += f"index: {self.current_idx}\n"
            string += (
                f"------------------------------------------------------------------\n"
            )
            string += str(table) + "\n"
            self.current_idx += 1
        self.current_idx = starting_index
        return string

    def build_symbol_table(self, tree: TreeNode) -> None:
        if isinstance(tree, MainNode):
            self.tables.append(Table(parent_id=self.current_idx))
            self.current_idx = len(self.tables) - 1

        if isinstance(tree, NewVariableNode):
            # Check for constant
            type_node_idx = 0
            if len(tree.children) == 4:
                type_node_idx = 1

            # Check for pointer
            id_node = tree.children[type_node_idx + 1]
            if isinstance(
                tree.children[type_node_idx + 1],
                (IntPointerNode, FloatPointerNode, CharPointerNode, BoolPointerNode),
            ):
                id_node = id_node.children[0]

            # Check for existing entry
            if self.find_entry_in_current_scope(id_node.value):
                raise ValueError(f"error: redefinition of '{id_node.value}'")
            # Create new entry
            self.tables[self.current_idx].add_entry(
                SymbolTableEntry(
                    id_node.value,
                    node_to_symbolTableEntryType(
                        tree.children[type_node_idx + 2], self
                    ),
                    len(tree.children) == 4,
                    id_node.line_nr,
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
