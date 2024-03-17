import graphviz as gv # type: ignore
from src.parser.TreeNode import TreeNode


class DotExporter:
    def __init__(self):
        pass

    @staticmethod
    def export(tree: TreeNode, output_path: str):
        g = gv.Digraph(format="png")
        DotExporter._export(g, tree)
        g.render(output_path.replace(".dot", ""), view=True)

    @staticmethod
    def _export(g: gv.Digraph, tree: TreeNode):
        g.node(str(id(tree)), tree.value)
        for child in tree.children:
            DotExporter._export(g, child)
            g.edge(str(id(tree)), str(id(child)))
