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

import re

from ifnode import IfNode
from scopenode import ScopeNode
from varnode import VarNode
from fornode import ForNode
from rawnode import RawNode

from error import ScopeErr

class Templar(object):
    def __init__(self):
        self.scope_stack = [ScopeNode()]
        var_pat = r"({{.*?}}|{%.*?%})"
        self.regex = re.compile(var_pat)
        self.current_scope = self.scope_stack[-1]

    # Allows templar to change the scope context
    # This allows for the nested semantics in our template source files
    def enter_scope(self, new_scope):
        self.scope_stack.append(new_scope)        
        self.current_scope = self.scope_stack[-1]

    # Allows templar to exit the scope
    def exit_scope(self):
        self.scope_stack.pop()
        if not len(self.scope_stack):
            raise ScopeErr('Unexpected end of a Scope')
        self.current_scope = self.scope_stack[-1]

    # During parsing, we maintain a scope level
    # at initial stage we have a scope level of root, i.e., the root_scope
    def compile(self, templ_src='', file=None):
        try:
            templ_src = ''.join((open(file).readline()))
        except:
            pass
        for c in self.regex.split(templ_src):
            if '{%' in c:
                if 'else' in c:
                    else_node = ScopeNode()
                    self.current_scope.add_elsenode(else_node)
                    # Exit the if scope
                    self.exit_scope()
                    # Enter the else scope
                    self.enter_scope(else_node)
                elif 'endif' in c:
                    self.exit_scope()
                elif 'endfor' in c:
                    self.exit_scope()
                elif 'if' in c:
                    ifnode = IfNode(c)
                    self.current_scope.add_node(ifnode)
                    self.enter_scope(ifnode)
                else:
                    for_node = ForNode(c)
                    self.current_scope.add_node(for_node)
                    self.enter_scope(for_node)
            elif '{{' in c:
                var_node = VarNode(c)
                self.current_scope.add_node(var_node)
            else:
                raw_node = RawNode(c)
                self.current_scope.add_node(raw_node)

        # Sanity check to make sure be are back at the root scope
        # at least one root_scope node must remain
        if len(self.scope_stack) > 1:
            raise ScopeErr('Unterminated Scope')
        return self

    def render(self, ctx={}):
        buf = ''
        for i in self.scope_stack:
            buf += i.render(ctx)
        return buf

if __name__=='__main__':
    t = Templar()
    t.compile(file='test_template.md')
    print(t.render({'truth_val':False, 'which': 'if', 'other':'not', 'books':['A', 'B', 'C', 'D']}))