from antlr4 import *
from src.parser.TreeNode import *
from antlr4.error.ErrorListener import ErrorListener, ConsoleErrorListener
from src.antlr_files.compilerLexer import compilerLexer as CLexer
from src.antlr_files.compilerParser import compilerParser as CParser, compilerParser
from src.antlr_files.compilerVisitor import compilerVisitor as CVisitor


class MyErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e) -> None:
        raise Exception(
            "Syntax error at line {0} column {1}: {2}".format(line, column, msg)
        )


class Parser:
    def __init__(self) -> None:
        pass

    """
    Parse the input file and return the CST
    :arg input_file: str
    :return tree: CParser.ProgContext
    """

    @staticmethod
    def parse(input_file: str, no_const_fold: bool, no_const_prop: bool) -> TreeNode:
        error_listener = MyErrorListener()
        lexer = CLexer(FileStream(input_file))
        lexer.removeErrorListener(ConsoleErrorListener.INSTANCE)
        lexer.addErrorListener(error_listener)

        stream: CommonTokenStream = CommonTokenStream(lexer)
        parser: CParser = CParser(stream)
        parser.removeErrorListener(ConsoleErrorListener.INSTANCE)
        parser.addErrorListener(error_listener)

        tree: CParser.ProgContext = parser.prog()

        ast = Parser.convert_to_ast(ASTVisitor().visit(tree))
        if not no_const_prop:
            pass  # TODO: implement constant propagation
        if not no_const_fold:
            ast = Parser.const_folding(ast)
        return ast

    @staticmethod
    def convert_to_ast(cst: TreeNode) -> TreeNode | None:
        if not cst.children:
            return

        for child in cst.children:
            Parser.convert_to_ast(child)

        # Remove all statements that have only one child except for some specific ones
        for child in cst.children:
            if len(child.children) == 1:
                new_child = child.children[0]
                if not isinstance(
                    child, (ProgNode, PointerNode, AddressNode, ReturnNode, NotNode)
                ):
                    idx = cst.children.index(child)
                    cst.children[idx] = new_child

        # Implicit conversions
        if isinstance(cst, NewVariableNode):
            type_node = cst.children[0]
            value_node = cst.children[2]
            constant = False
            if isinstance(type_node, ConstNode):
                constant = True
                type_node = cst.children[1]
                value_node = cst.children[3]
            if type_node.value == "int" and isinstance(value_node, FloatNode):
                print(
                    f"Warning: Conversion from type float to int on line {type_node.line_nr} may cause loss of information."
                )
                new_node = IntNode(
                    str(int(float(value_node.value))), value_node.children, value_node.line_nr
                )
                if constant:
                    cst.children[3] = new_node
                else:
                    cst.children[2] = new_node
            if type_node.value == "char":
                if isinstance(value_node, FloatNode):
                    print(
                        f"Warning: Conversion from type float to char on line {type_node.line_nr} may cause loss of information."
                    )
                    new_node = CharNode(
                        str(chr(int(float(value_node.value)))), value_node.children, value_node.line_nr
                    )
                    if constant:
                        cst.children[3] = new_node
                    else:
                        cst.children[2] = new_node
                elif isinstance(value_node, IntNode):
                    print(
                        f"Warning: Conversion from type int to char on line {type_node.line_nr} may cause loss of information."
                    )
                    new_node = CharNode(
                        str(chr(int(value_node.value))), value_node.children, value_node.line_nr
                    )
                    if constant:
                        cst.children[3] = new_node
                    else:
                        cst.children[2] = new_node

        return cst

    @staticmethod
    def const_folding(cst: TreeNode) -> TreeNode | None:
        if not cst.children:
            return

        for child in cst.children:
            Parser.const_folding(child)

        for child in cst.children:
            if (
                isinstance(child, PlusNode)
                and isinstance(child.children[0], IntNode)
                and isinstance(child.children[1], IntNode)
            ):
                new_child = IntNode(
                    str(int(child.children[0].value) + int(child.children[1].value)),
                    line_nr=child.line_nr,
                )
                idx = cst.children.index(child)
                cst.children[idx] = new_child

            elif (
                isinstance(child, MinusNode)
                and isinstance(child.children[0], IntNode)
                and isinstance(child.children[1], IntNode)
            ):
                new_child = IntNode(
                    str(int(child.children[0].value) - int(child.children[1].value)),
                    line_nr=child.line_nr,
                )
                idx = cst.children.index(child)
                cst.children[idx] = new_child

            elif (
                isinstance(child, MultNode)
                and isinstance(child.children[0], IntNode)
                and isinstance(child.children[1], IntNode)
            ):
                new_child = IntNode(
                    str(int(child.children[0].value) * int(child.children[1].value)),
                    line_nr=child.line_nr,
                )
                idx = cst.children.index(child)
                cst.children[idx] = new_child

            elif (
                isinstance(child, DivNode)
                and isinstance(child.children[0], IntNode)
                and isinstance(child.children[1], IntNode)
            ):
                new_child = IntNode(
                    str(int(child.children[0].value) // int(child.children[1].value)),
                    line_nr=child.line_nr,
                )
                idx = cst.children.index(child)
                cst.children[idx] = new_child

            elif (
                isinstance(child, ModNode)
                and isinstance(child.children[0], IntNode)
                and isinstance(child.children[1], IntNode)
            ):
                new_child = IntNode(
                    str(int(child.children[0].value) % int(child.children[1].value)),
                    line_nr=child.line_nr,
                )
                idx = cst.children.index(child)
                cst.children[idx] = new_child
        if len(cst.children) > 0:
            for child in cst.children:
                if len(child.children) == 1:
                    new_child = child.children[0]
                    if not isinstance(
                        child, (StatNode, ProgNode, MainNode, ReturnNode, NotNode)
                    ):
                        idx = cst.children.index(child)
                        cst.children[idx] = new_child

        return cst


operator_signs = {
    "+",
    "-",
    "*",
    "/",
    "<",
    ">",
    "==",
    "&&",
    "||",
    ">=",
    "<=",
    "!=",
    "%",
    ">>",
    "<<",
    "!",
}


class ASTVisitor(CVisitor):
    def visitProg(self, ctx: CParser.ProgContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        return ProgNode(line_nr=ctx.start.line, children=children)

    def visitMain(self, ctx: compilerParser.MainContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        return MainNode(line_nr=ctx.start.line, children=children)

    def visitStat(self, ctx: CParser.StatContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        return StatNode(line_nr=ctx.start.line, children=children)

    def visitExpr(self, ctx: CParser.ExprContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        # Check which expression
        if len(children) == 3:
            middle = children[1]
            if isinstance(middle, PlusNode):
                return PlusNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, MinusNode):
                return MinusNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, MultNode):
                return MultNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, DivNode):
                return DivNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, ModNode):
                return ModNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, LShiftNode):
                return LShiftNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, RShiftNode):
                return RShiftNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, AddressNode):
                return BitAndNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, BitOrNode):
                return BitOrNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, BitXorNode):
                return BitXorNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, BitNotNode):
                return BitNotNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, EqualNode):
                return EqualNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, NeqNode):
                return NeqNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, LtNode):
                return LtNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, GtNode):
                return GtNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, LeqNode):
                return LeqNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, GeqNode):
                return GeqNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, AndNode):
                return AndNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, OrNode):
                return OrNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
        if len(children) == 2:
            if isinstance(children[0], ReturnNode):
                return ReturnNode(line_nr=ctx.start.line, children=[children[1]])
            if isinstance(children[0], NotNode):
                return NotNode(line_nr=ctx.start.line, children=[children[1]])

        return ExprNode(line_nr=ctx.start.line, children=children)

    def visitVariable(self, ctx: CParser.VariableContext) -> VariableNode:
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        return VariableNode(line_nr=ctx.start.line, children=children)

    def visitNewVariable(self, ctx: CParser.NewVariableContext) -> NewVariableNode:
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        return NewVariableNode(line_nr=ctx.start.line, children=children)

    def visitPointer(self, ctx: CParser.PointerContext) -> PointerNode:
        children = []
        pointer_depth = 0
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            if isinstance(cstChild, MultNode):
                pointer_depth += 1
                continue
            children.append(cstChild)

        return PointerNode(pointer_depth, line_nr=ctx.start.line, children=children)

    def visitAddress(self, ctx: CParser.AddressContext) -> AddressNode:
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None or isinstance(cstChild, AddressNode):
                continue
            children.append(cstChild)

        return AddressNode(line_nr=ctx.start.line, children=children)

    def visitAssignment(self, ctx: CParser.AssignmentContext) -> AssignNode:
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        return AssignNode(line_nr=ctx.start.line, children=children)

    def visitLiteral(self, ctx: CParser.LiteralContext) -> LiteralNode:
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        return LiteralNode(line_nr=ctx.start.line, children=children)

    def visitTerminal(self, node: TerminalNode) -> TreeNode:
        text = node.getText()

        if text in operator_signs:
            match text:
                case "+":
                    return PlusNode(line_nr=node.symbol.line)
                case "-":
                    return MinusNode(line_nr=node.symbol.line)
                case "*":
                    return MultNode(line_nr=node.symbol.line)
                case "/":
                    return DivNode(line_nr=node.symbol.line)
                case "%":
                    return ModNode(line_nr=node.symbol.line)
                case ">>":
                    return RShiftNode(line_nr=node.symbol.line)
                case "<<":
                    return LShiftNode(line_nr=node.symbol.line)
                case "==":
                    return EqualNode(line_nr=node.symbol.line)
                case "!=":
                    return NeqNode(line_nr=node.symbol.line)
                case "<":
                    return LtNode(line_nr=node.symbol.line)
                case ">":
                    return GtNode(line_nr=node.symbol.line)
                case "<=":
                    return LeqNode(line_nr=node.symbol.line)
                case ">=":
                    return GeqNode(line_nr=node.symbol.line)
                case "&&":
                    return AndNode(line_nr=node.symbol.line)
                case "||":
                    return OrNode(line_nr=node.symbol.line)
                case "!":
                    return NotNode(line_nr=node.symbol.line)
                case "&":
                    return AddressNode(line_nr=node.symbol.line)
                case _:
                    raise Exception(f"Unknown operator: {text}")
                # TODO: Add more cases
        match node.symbol.type:
            case CParser.INT:
                return IntNode(text, line_nr=node.symbol.line)
            case CParser.FLOAT:
                return FloatNode(text, line_nr=node.symbol.line)
            case CParser.STRING:
                return StringNode(text, line_nr=node.symbol.line)
            case CParser.ID:
                if text in ("true", "false"):
                    return BoolNode(text, line_nr=node.symbol.line)
                return IdNode(text, line_nr=node.symbol.line)
            case CParser.POINTER:
                return PointerNode(text, line_nr=node.symbol.line)
            case CParser.AMPERSAND:
                return AddressNode(text, line_nr=node.symbol.line)
            case CParser.BITOR:
                return BitOrNode(text, line_nr=node.symbol.line)
            case CParser.BITXOR:
                return BitXorNode(text, line_nr=node.symbol.line)
            case CParser.BITNOT:
                return BitNotNode(text, line_nr=node.symbol.line)
            case CParser.RETURN:
                return ReturnNode(text, line_nr=node.symbol.line)
            case CParser.CONST:
                return ConstNode(line_nr=node.symbol.line)
            case CParser.CHAR:
                return CharNode(text, line_nr=node.symbol.line)
            case CParser.TYPE:
                return TypeNode(text, line_nr=node.symbol.line)
            case CParser.BOOL:
                return BoolNode(text, line_nr=node.symbol.line)
