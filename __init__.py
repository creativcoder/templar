"""
MIT License

Copyright (c) 2017 Rahul Sharma

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

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

class RawNode(object):
	def __init__(self, chunk):
		self.chunk = chunk

	def render(self, ctx={}):
		return str(self.chunk)

	def __repr__(self):
		return str('[{}]'.format(self.chunk))

class VarNode(object):
	def __init__(self, chunk):
		self.var = VarNode.extract_var(chunk)

	@staticmethod
	def extract_var(chunk):
		cleaned = chunk.lstrip('{{')
		cleaned = cleaned.rstrip('}}')
		return cleaned.strip()

	def render(self, ctx={}):
		return str(ctx.get(self.var))

	def __repr__(self):
		return str('[{}]'.format(self.var))

class ForNode(ScopeNode):
	def __init__(self, chunk):
		super(ForNode, self).__init__()
		self.iterable = ForNode.get_iterable_from_sanitized(chunk)
		self.iterator = ForNode.get_iterator_from_sanitized(chunk)

	@staticmethod
	def get_iterable_from_sanitized(chunk):
		cleaned = chunk.rstrip('%}')
		cleaned = cleaned.lstrip('{%')
		cleaned = cleaned.split()[-1]
		return cleaned

	@staticmethod
	def get_iterator_from_sanitized(chunk):
		cleaned = chunk.rstrip('%}')
		cleaned = cleaned.lstrip('{%')
		cleaned = cleaned.split()[1]
		return cleaned

	def render_whole_nodes(self, ctx={}):
		buf = ''
		for i in self.nodes:
			buf += i.render(ctx)
		return buf

	def __repr__(self):
		return str(self.nodes)

	def render(self, ctx={}):
		buf = ''
		for i in ctx.get(self.iterable):
			ctx.update({self.iterator:i})
			buf += self.render_whole_nodes(ctx)
			buf = buf + '\n'
		return buf

class Templar(object):
	def __init__(self):
		import re
		self.root_scope = ScopeNode()
		var_pat = r"({{.*?}}|{%.*?%})"
		self.regex = re.compile(var_pat)
		self.scope_stack = [self.root_scope]
		self.scope_idx = 0
		self.current_scope = self.scope_stack[self.scope_idx]

	# Allows templar to change the scope context
	# This is required for preserving the nested semantics in our template source files
	def enter_scope(self):
		self.scope_idx += 1
		self.current_scope = self.scope_stack[self.scope_idx]

	# Allows templar to exit the scope
	def exit_scope(self):
		self.scope_stack.pop()
		self.scope_idx -= 1
		self.current_scope = self.scope_stack[self.scope_idx]

	# During parsing, we maintain a scope level
	# at initial stage we have a scope level of root, i.e., the root_scope
	def compile(self, templ_src):
		frags = self.regex.split(templ_src)
		while len(frags):
			current_node = frags[0]
			frags = frags[1:]
			if '{%' in current_node:
				if 'endfor' in current_node:
					self.exit_scope()
				else:
					for_node = ForNode(current_node)
					self.current_scope.add_node(for_node)
					self.scope_stack.append(for_node)
					self.enter_scope()
			elif '{{' in current_node:
				var_node = VarNode(current_node)
				self.current_scope.add_node(var_node)
			else:
				raw_node = RawNode(current_node)
				self.current_scope.add_node(raw_node)

		# Sanity check to make sure be are back at the root scope
		# at least one root_scope node must remain
		if len(self.scope_stack) > 1:
			print('WARN: Nesting issues')
		return self

	def render(self, ctx={}):
		buf = ''
		for i in self.scope_stack:
			buf += i.render(ctx)
		return buf

# if __name__=='__main__':
# 	t = Templar()
# 	ast = t.compile("""Hello {% for i in something %}This is number {{i}}{% for name in users %}Hi {{name}} {% endfor %}{% endfor %}World""")
# 	print(ast.render(ctx={'something':[1,2], 'this':4, 'users':['Alice', 'Bob']}))