class TreeNode:
    def __init__(self, value: str, line_nr: int = None, children=None):
        self.value = value
        self.children = children if children is not None else []
        self.line_nr = line_nr


class ProgNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__("Prog", children=children, line_nr=line_nr)


class StatNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__("Stat", children=children, line_nr=line_nr)


class ExprNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__("Expr", children=children, line_nr=line_nr)


class LiteralNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__("Literal", children=children, line_nr=line_nr)


class VariableNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__("Var", children=children, line_nr=line_nr)


class AssignNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__("Assignment", children=children, line_nr=line_nr)


class NewVariableNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__("NewVar", children=children, line_nr=line_nr)


class PlusNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__("+", children=children, line_nr=line_nr)


class GtNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__(">", children=children, line_nr=line_nr)


class LtNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__("<", children=children, line_nr=line_nr)


class EqNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__("=", children=children, line_nr=line_nr)


class GeqNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__(">=", children=children, line_nr=line_nr)


class LeqNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__("<=", children=children, line_nr=line_nr)


class AndNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__("&&", children=children, line_nr=line_nr)


class OrNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__("||", children=children, line_nr=line_nr)


class ModNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__("%", children=children, line_nr=line_nr)


class LShiftNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__("<<", children=children, line_nr=line_nr)


class RShiftNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__(">>", children=children, line_nr=line_nr)


class BitAndNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__("&", children=children, line_nr=line_nr)


class BitOrNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__("|", children=children, line_nr=line_nr)


class BitXorNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__("^", children=children, line_nr=line_nr)


class BitNotNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__("~", children=children, line_nr=line_nr)


class MinusNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__("-", children=children, line_nr=line_nr)


class MultNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__("*", children=children, line_nr=line_nr)


class DivNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__("/", children=children, line_nr=line_nr)


class IntNode(TreeNode):
    def __init__(self, value: str, children=None, line_nr: int = None):
        super().__init__(value, children=children, line_nr=line_nr)


class FloatNode(TreeNode):
    def __init__(self, value: str, children=None, line_nr: int = None):
        super().__init__(value, children=children, line_nr=line_nr)


class StringNode(TreeNode):
    def __init__(self, value: str, children=None, line_nr: int = None):
        super().__init__(value, children=children, line_nr=line_nr)


class IdNode(TreeNode):
    def __init__(self, value: str, children=None, line_nr: int = None):
        super().__init__(value, children=children, line_nr=line_nr)


class PointerNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__("Pointer", children=children, line_nr=line_nr)


class AddressNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__("Address", children=children, line_nr=line_nr)
