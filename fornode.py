from scopenode import ScopeNode

class ForNode(ScopeNode):
    def __init__(self, chunk):
        super(ForNode, self).__init__()
        self.iterable, self.iterator = ForNode.get_iter_items(chunk)

    @staticmethod
    def get_iter_items(chunk):
        cleaned = chunk.rstrip('%}').lstrip('{%').split()
        return cleaned[-1], cleaned[1]

    def render_children(self, ctx={}):
        buf = ''
        for i in self.nodes:
            buf += i.render(ctx)
        return buf

    def render(self, ctx={}):
        buf = ''
        for i in ctx.get(self.iterable):
            ctx.update({self.iterator: i})
            buf += self.render_children(ctx)
            buf += '\n'
        return buf