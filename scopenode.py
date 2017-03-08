
class ScopeNode(object):
    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)

    def render(self, ctx={}):
        buf = ''
        for i in self.nodes:
            buf += i.render(ctx)
        return buf