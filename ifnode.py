from scopenode import ScopeNode

class IfNode(ScopeNode):
    def __init__(self, chunk):
        super(IfNode, self).__init__()
        self.cond_var = IfNode.get_conditional_var(chunk)
        self.else_block = ScopeNode()

    @staticmethod
    def get_conditional_var(chunk):
        cleaned = chunk.rstrip('%}').lstrip('{%').split()[-1]
        return cleaned

    def add_elsenode(self, elsenode):
        self.else_block = elsenode

    def render_if_block(self, ctx={}):
        buf = ''
        for i in self.nodes:
            buf += i.render(ctx)
        return buf

    def render_else_block(self, ctx={}):
        buf = ''
        for i in self.else_block.nodes:
            buf += i.render(ctx)
        return buf

    def render(self, ctx={}):
        buf = ''
        if ctx.get(self.cond_var):
            buf += self.render_if_block(ctx)
        else:
            buf += self.render_else_block(ctx)
        return buf

class ElseNode(ScopeNode):
    def __init__(self):
        super(ElseNode, self).__init__()