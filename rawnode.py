
class RawNode(object):
    def __init__(self, chunk):
        self.chunk = chunk

    def render(self, ctx={}):
        return str(self.chunk)