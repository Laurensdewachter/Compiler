import graphviz as gv


class DotExporter:
    def __init__(self):
        pass

    @staticmethod
    def export(tree, output_path: str):
        g = gv.Digraph(format="png")

        g.render(output_path, view=True)
