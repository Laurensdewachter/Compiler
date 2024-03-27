import copy

from antlr4 import *
from src.parser.TreeNode import *
from src.parser.SymbolTable import *
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
    def parse(input_file: str) -> TreeNode:
        error_listener = MyErrorListener()
        lexer = CLexer(FileStream(input_file))
        lexer.removeErrorListener(ConsoleErrorListener.INSTANCE)
        lexer.addErrorListener(error_listener)

        stream: CommonTokenStream = CommonTokenStream(lexer)
        parser: CParser = CParser(stream)
        parser.removeErrorListener(ConsoleErrorListener.INSTANCE)
        parser.addErrorListener(error_listener)

        tree: CParser.ProgContext = parser.prog()

        return Parser.convert_to_ast(ASTVisitor().visit(tree))

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
                    child,
                    (
                        ProgNode,
                        AddressNode,
                        ReturnNode,
                        NotNode,
                        PointerNode,
                        IntPointerNode,
                        FloatPointerNode,
                        CharPointerNode,
                        BoolPointerNode,
                        PrintfNode,
                    ),
                ):
                    idx = cst.children.index(child)
                    cst.children[idx] = new_child

        return cst

    @staticmethod
    def const_folding(ast: TreeNode, changed=False) -> bool | None:
        if not ast.children:
            return

        for child in ast.children:
            Parser.const_folding(child, changed)

        for child in ast.children:
            if (
                child.children is not None
                and len(child.children) >= 2
                and (
                    not isinstance(child.children[0], IntNode)
                    or not isinstance(child.children[1], IntNode)
                )
            ):
                continue
            new_child = None
            if isinstance(child, PlusNode) and len(child.children) == 2:
                new_child = IntNode(
                    str(int(child.children[0].value) + int(child.children[1].value)),
                    line_nr=child.line_nr,
                )
            elif isinstance(child, MinusNode) and len(child.children) == 2:
                new_child = IntNode(
                    str(int(child.children[0].value) - int(child.children[1].value)),
                    line_nr=child.line_nr,
                )
            elif isinstance(child, MultNode):
                new_child = IntNode(
                    str(int(child.children[0].value) * int(child.children[1].value)),
                    line_nr=child.line_nr,
                )
            elif isinstance(child, DivNode):
                new_child = IntNode(
                    str(int(child.children[0].value) // int(child.children[1].value)),
                    line_nr=child.line_nr,
                )
            elif isinstance(child, ModNode):
                new_child = IntNode(
                    str(int(child.children[0].value) % int(child.children[1].value)),
                    line_nr=child.line_nr,
                )
            elif isinstance(child, OrNode):
                new_child = IntNode(
                    str(int(child.children[0].value) or int(child.children[1].value)),
                    line_nr=child.line_nr,
                )
            elif isinstance(child, AndNode):
                new_child = IntNode(
                    str(int(child.children[0].value) and int(child.children[1].value)),
                    line_nr=child.line_nr,
                )
            elif isinstance(child, NotNode):
                new_child = IntNode(
                    str(int(not int(child.children[0].value))),
                    line_nr=child.line_nr,
                )
            elif isinstance(child, GtNode):
                new_child = IntNode(
                    str(
                        int(int(child.children[0].value) > int(child.children[1].value))
                    ),
                    line_nr=child.line_nr,
                )
            elif isinstance(child, LtNode):
                new_child = IntNode(
                    str(
                        int(int(child.children[0].value) < int(child.children[1].value))
                    ),
                    line_nr=child.line_nr,
                )
            elif isinstance(child, GeqNode):
                new_child = IntNode(
                    str(
                        int(
                            int(child.children[0].value) <= int(child.children[1].value)
                        )
                    ),
                    line_nr=child.line_nr,
                )
            elif isinstance(child, LeqNode):
                new_child = IntNode(
                    str(
                        int(
                            int(child.children[0].value) <= int(child.children[1].value)
                        )
                    ),
                    line_nr=child.line_nr,
                )
            elif isinstance(child, NeqNode):
                new_child = IntNode(
                    str(
                        int(
                            int(child.children[0].value) != int(child.children[1].value)
                        )
                    ),
                    line_nr=child.line_nr,
                )
            elif isinstance(child, LShiftNode):
                if int(child.children[1].value) >= 0:
                    new_child = IntNode(
                        str(
                            int(
                                int(child.children[0].value)
                                << int(child.children[1].value)
                            )
                        ),
                        line_nr=child.line_nr,
                    )
                else:
                    new_child = IntNode(
                        str(
                            int(
                                int(child.children[0].value)
                                >> -int(child.children[1].value)
                            )
                        ),
                        line_nr=child.line_nr,
                    )
            elif isinstance(child, RShiftNode):
                if int(child.children[1].value) >= 0:
                    new_child = IntNode(
                        str(
                            int(
                                int(child.children[0].value)
                                >> int(child.children[1].value)
                            )
                        ),
                        line_nr=child.line_nr,
                    )
                else:
                    new_child = IntNode(
                        str(
                            int(
                                int(child.children[0].value)
                                << -int(child.children[1].value)
                            )
                        ),
                        line_nr=child.line_nr,
                    )
            elif isinstance(child, BitXorNode):
                new_child = IntNode(
                    str(
                        int(int(child.children[0].value) ^ int(child.children[1].value))
                    ),
                    line_nr=child.line_nr,
                )
            elif isinstance(child, BitAndNode):
                new_child = IntNode(
                    str(
                        int(int(child.children[0].value) & int(child.children[1].value))
                    ),
                    line_nr=child.line_nr,
                )
            elif isinstance(child, BitOrNode):
                new_child = IntNode(
                    str(
                        int(int(child.children[0].value) & int(child.children[1].value))
                    ),
                    line_nr=child.line_nr,
                )

            if new_child is not None:
                idx = ast.children.index(child)
                ast.children[idx] = new_child
                changed = True

        return changed

    @staticmethod
    def const_prop(
        ast: TreeNode,
        symbol_table: SymbolTable,
    ) -> bool | None:
        class ValueEntry:
            def __init__(self, id: str, value: str):
                self.id: str = id
                self.value: str = value

        const_values: [ValueEntry] = []

        def get_const_value(id: str) -> str | None:
            for entry in const_values:
                if entry.id == id:
                    return entry.value
            return None

        def const_prop_recur(ast: TreeNode, changed=False) -> bool | None:
            if ast.children is None:
                return

            for child in ast.children:
                const_prop_recur(child)

            # Store new constant variables
            if (
                isinstance(ast, NewVariableNode)
                and isinstance(ast.children[0], ConstNode)
                and isinstance(
                    ast.children[-1], (IntNode, FloatNode, CharNode, BoolNode)
                )
            ):
                const_values.append(
                    ValueEntry(ast.children[-2].value, ast.children[-1].value)
                )

            # Check if right id is constant at new assignments
            if (
                isinstance(ast, (NewVariableNode, AssignNode))
                and isinstance(ast.children[-1], IdNode)
                and symbol_table.find_entry(ast.children[-1].value).const
            ):
                const_value = get_const_value(ast.children[-1].value)
                if const_value is not None:
                    match symbol_table.find_entry(ast.children[-1].value).type:
                        case SymbolTableEntryType.Int:
                            new_node = IntNode(const_value)
                        case SymbolTableEntryType.Float:
                            new_node = FloatNode(const_value)
                        case SymbolTableEntryType.Char:
                            new_node = CharNode(const_value)
                        case SymbolTableEntryType.Bool:
                            new_node = BoolNode(const_value)
                    new_node.line_nr = ast.line_nr
                    ast.children[-1] = new_node
                    changed = True

            if not isinstance(ast, (NewVariableNode, AssignNode, AddressNode)):
                for child in ast.children:
                    if (
                        isinstance(child, IdNode)
                        and symbol_table.find_entry(child.value).const
                    ):
                        const_value = get_const_value(ast.children[-1].value)
                        if const_value is not None:
                            match symbol_table.find_entry(ast.children[-1].value).type:
                                case SymbolTableEntryType.Int:
                                    new_node = IntNode(const_value)
                                case SymbolTableEntryType.Float:
                                    new_node = FloatNode(const_value)
                                case SymbolTableEntryType.Char:
                                    new_node = CharNode(const_value)
                                case SymbolTableEntryType.Bool:
                                    new_node = BoolNode(const_value)
                            new_node.line_nr = ast.line_nr
                            ast.children[-1] = new_node
                            changed = True
            return changed

        return const_prop_recur(ast)


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

    def __init__(self) -> None:
        self.typedefs = {}
        self.visited_main = False

    def visitProg(self, ctx: CParser.ProgContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        return ProgNode(line_nr=ctx.start.line, children=children)

    def visitTypedef(self, ctx: compilerParser.TypedefContext):
        c_type = ctx.children[1].getText()
        new_type = ctx.children[2].getText()
        if new_type in ["int", "float", "char"]:
            raise Exception(
                f"Type {new_type} is a reserved keyword and cannot be used as a typedef."
            )
        self.typedefs[new_type] = c_type

    def visitMain(self, ctx: compilerParser.MainContext):
        children = []
        self.visited_main = True
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

    def visitPrintf(self, ctx: compilerParser.PrintfContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        return PrintfNode(line_nr=ctx.start.line, children=children)

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
            if isinstance(children[0], PlusNode):
                return children[1]
            if isinstance(children[0], MinusNode) and children[0].children == []:
                try:
                    if isinstance(children[1].children[0].children[0], IntNode):
                        return IntNode(
                            "-" + children[1].children[0].children[0].value,
                            line_nr=children[1].line_nr,
                        )
                    if isinstance(children[1].children[0].children[0], FloatNode):
                        return FloatNode(
                            "-" + children[1].children[0].children[0].value,
                            line_nr=children[1].line_nr,
                        )
                except:
                    pass

        return ExprNode(line_nr=ctx.start.line, children=children)

    def visitVariable(self, ctx: CParser.VariableContext) -> VariableNode:
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        return VariableNode(line_nr=ctx.start.line, children=children)

    def visitUnaryplusplus(self, ctx: CParser.UnaryplusplusContext) -> AssignNode:
        if ctx.children[0].getText() == "++":
            var = self.visit(ctx.children[1])
        else:
            var = self.visit(ctx.children[0])

        return AssignNode(
            line_nr=ctx.start.line,
            children=[
                var,
                PlusNode(
                    [copy.deepcopy(var), IntNode("1", line_nr=ctx.start.line)],
                    line_nr=ctx.start.line,
                ),
            ],
        )

    def visitUnaryminusminus(self, ctx: CParser.UnaryminusminusContext) -> AssignNode:
        if ctx.children[0].getText() == "--":
            var = self.visit(ctx.children[1])
        else:
            var = self.visit(ctx.children[0])

        return AssignNode(
            line_nr=ctx.start.line,
            children=[
                var,
                MinusNode(
                    [copy.deepcopy(var), IntNode("1", line_nr=ctx.start.line)],
                    line_nr=ctx.start.line,
                ),
            ],
        )

    def visitNewVariable(self, ctx: CParser.NewVariableContext) -> NewVariableNode:
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)
        const_node = isinstance(children[0], ConstNode)
        explicit_conversion = isinstance(children[2 + const_node], TypeNode)
        type_node = children[0 + const_node]
        pointer_node = children[1 + const_node]
        pointer_idx = 1 + const_node
        if self.typedefs.get(type_node.value):
            type = self.typedefs.get(type_node.value)
            children[0 + const_node] = TypeNode(type, line_nr=type_node.line_nr)
        if isinstance(pointer_node, PointerNode):
            match type_node.value:
                case "int":
                    children[pointer_idx] = IntPointerNode(
                        pointer_node.depth, pointer_node.children, pointer_node.line_nr
                    )
                    type_node.value = "int*"
                case "float":
                    children[pointer_idx] = FloatPointerNode(
                        pointer_node.depth, pointer_node.children, pointer_node.line_nr
                    )
                    type_node.value = "float*"
                case "char":
                    children[pointer_idx] = CharPointerNode(
                        pointer_node.depth, pointer_node.children, pointer_node.line_nr
                    )
                    type_node.value = "char*"
                case "bool":
                    children[pointer_idx] = BoolPointerNode(
                        pointer_node.depth, pointer_node.children, pointer_node.line_nr
                    )
                    type_node.value = "bool*"

        if explicit_conversion:
            type = children[2 + const_node]
            children.pop(2 + const_node)
            children[2 + const_node] = ConvertNode(
                children=[type, children[2 + const_node]], line_nr=type.line_nr
            )
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
            case CParser.POINTER:
                return PointerNode(text, line_nr=node.symbol.line)
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
            case CParser.LINE_COMMENT:
                return CommentNode(text, line_nr=node.symbol.line)
            case CParser.COMMENT:
                return CommentNode(text, line_nr=node.symbol.line)
            case CParser.PLUSPLUS:
                return UnaryPlusNode(text, line_nr=node.symbol.line)
            case CParser.MINUSMINUS:
                return UnaryMinusNode(text, line_nr=node.symbol.line)
