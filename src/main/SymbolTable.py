from enum import Enum

from src.parser.TreeNode import *

class SymbolTableEntryType(Enum):
    Int = "int"
    Float = "float"
    Char = "char"
    String = "string"
    Bool = "bool"


class SymbolTableEntry:
    def __init__(self, name, type, offset):
        self.name: str = name
        self.type: SymbolTableEntryType = type
        self.offset: int = (
            offset  # is this necessary? Might be useful for memory allocation
        )


class Table:
    def __init__(self, parent_id: int = -1, offset: int = 0):
        self.table: list[SymbolTableEntry] = []
        self.parent_id: int = parent_id
        self.type: SymbolTableEntryType = type  # TreeNode type
        self.offset: int = offset  # is this necessary? Might be useful for memory allocation


class Table:
    def __init__(self):
        self.table: list[SymbolTableEntry] = []
        self.parent = None

    def add_entry(self, entry: SymbolTableEntry):
        self.table.append(entry)


class SymbolTable:
    def __init__(self):
        self.tables: list[Table] = [
            Table()
        ]  # Root table of program is always at index 0

    def build_symbol_table(self, tree: TreeNode):
        pass
        self.tables: list[Table] = [Table()]  # Root table of program is always at index 0


    def build_symbol_table(self, tree: TreeNode):
        pass