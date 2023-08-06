import ast

__version__ = '0.0.2'
__all__ = ('FailsChecker', )


class PluginVisitor(ast.NodeVisitor):
    def __init__(self):
        self.errors = []

    def visit_Index(self, node):
        # TODO fix if indexing in try:else: statement
        index_error_handler = False
        index_error = (
            node.value.lineno,
            node.value.col_offset,
            'PF101 Potential IndexError fail.',
            type(self)
        )

        parent = node
        while True:
            if getattr(parent, 'pf_parent', None):
                parent = parent.pf_parent
                if isinstance(parent, ast.Try):
                    for handler in parent.handlers:
                        if handler.type:
                            if handler.type.id == 'IndexError':
                                index_error_handler = True
                                break
                        else:
                            index_error_handler = True
                    break
            else:
                break

        if not index_error_handler:
            self.errors.append(index_error)

        self.generic_visit(node)

    def generic_visit(self, node):
        super().generic_visit(node)


class FailsChecker(object):
    name = 'flake8-prevent-fails'
    version = __version__

    def __init__(self, tree, filename, tokens):
        for statement in ast.walk(tree):
            for child in ast.iter_child_nodes(statement):
                child.pf_parent = statement

        self.tree = tree
        self.filename = filename
        self.tokens = tokens

    def check_tree(self):
        visitor = PluginVisitor()
        visitor.visit(self.tree)

        return visitor.errors

    def run(self):
        for error in self.check_tree():
            yield error
