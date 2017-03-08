
class VarNode(object):
    def __init__(self, chunk):
        self.var = VarNode.extract_var(chunk)

    @staticmethod
    def extract_var(chunk):
        return chunk.lstrip('{{').rstrip('}}').strip()

    def render(self, ctx={}):
        if '.' in self.var:
            obj, attr = self.var.split('.')
            if obj and isinstance(obj, dict):
                obj = ctx.get(obj)
                return str(obj.get(attr))
            else:
                return str(getattr(ctx.get(obj), attr, None))

        return str(ctx.get(self.var))