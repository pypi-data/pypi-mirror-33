import ast

__version__ = '0.0.1'
__all__ = ('FailsChecker', )


class PluginVisitor(ast.NodeVisitor):
    def __init__(self):
        self.errors = []

    def visit_Index(self, node):
        index_error_handler = False
        index_error = (
            node.value.lineno,
            node.value.col_offset,
            'PF101 Potential «IndexError: list index out of range» fail.',
            type(self)
        )
        depth = node.depth
        parent = node
        for i in range(depth):
            parent = parent.parent
            if isinstance(parent, ast.Try):
                for handler in parent.handlers:
                    if handler.type:
                        if handler.type.id == 'IndexError':
                            index_error_handler = True
                            break
                    else:
                        index_error_handler = True
                break

        if not index_error_handler:
            self.errors.append(index_error)


class FailsChecker(object):
    name = 'flake8-prevent-fails'
    version = __version__

    def __init__(self, tree):
        self.tree = tree
        self.messages = [
            (1, 0, 'PF101 Fancy header. Invalid.', type(self)),
        ]

    def check_tree(self):
        visitor = PluginVisitor()
        visitor.visit(self.tree)

        return visitor.errors

    def run(self):
        for error in self.check_tree():
            yield error
