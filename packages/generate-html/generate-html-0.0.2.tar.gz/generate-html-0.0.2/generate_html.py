from functools import partial
import html

from signature_altering import decorator

__version__ = '0.0.2'

VOID_ELEMENTS = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'keygen', 'link', 'menuitem', 'meta', 'param', 'source', 'track', 'wbr'}
RAW_TEXT_ELEMENTS = {'script', 'style'}
ESCAPABLE_RAW_TEXT_ELEMENTS = {'textarea', 'title'}

class InvalidHTML(Exception):
    pass

class RawHTML:
    '''Wrap a string to signal it is raw HTML that does not need to be escaped.'''
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f'RawHTML({self.value!r})'
    def __html__(self):
        return self.value

def escape(thing):
    return html.escape(str(thing))

def to_html(thing):
    '''Convert any object to a str containing HTML.'''
    if hasattr(thing, '__html__'):
        return thing.__html__()
    return escape(thing)

class Node:
    '''A node in the document tree, not necessarily an Element'''
    def __init__(self, *args, **kwargs):
        self.children = []
    def add(self, item):
        if isinstance(item, ElementCollection):
            self.children.extend(item.children)
        elif isinstance(item, ComponentContents):
            raise TypeError('cannot add ComponentContents to tree: make sure to yield h.insert_contents(...) directly')
        else:
            self.children.append(item)
    def _generate_html(self):
        for item in self.children:
            if isinstance(item, Node):
                yield from item._generate_html()
            else:
                yield to_html(item)
    def __html__(self):
        return ''.join(self._generate_html())

class Element(Node):
    '''Element(h, 'spam') -> <spam></spam>'''
    def __init__(self, context, tagname, *args, **kwargs):
        super().__init__(context, tagname, *args, **kwargs)
        self.context = context
        self.tagname = tagname
        if args and self.tagname in VOID_ELEMENTS:
            raise TypeError(f'<{self.tagname}> cannot have children')
        for arg in args:
            self.add(arg)
        self.kwargs = kwargs
    def add(self, item):
        if self.tagname in VOID_ELEMENTS:
            raise TypeError(f'<{self.tagname}> cannot have children')
        super().add(item)
    def __repr__(self):
        return f'<{self.tagname} {self.children}>'
    def __enter__(self):
        self.context.push(self)
    def __exit__(self, exc_type, exc_value, traceback):
        self.context.pop(self)
    def has_closing_tag(self):
        return self.tagname not in VOID_ELEMENTS
    def _generate_attribute(self, key, value):
        if value is False:
            return
        yield ' '
        yield key.replace('_', '-').rstrip('-')
        if value is True:
            return
        yield '="'
        yield escape(value)
        yield '"'
    def _generate_html(self):
        yield '<'
        yield self.tagname
        for key, value in self.kwargs.items():
            if isinstance(value, list):
                value = ' '.join(str(item) for item in value)
            yield from self._generate_attribute(key, value)
        yield '>'
        if self.tagname in RAW_TEXT_ELEMENTS:
            yield from self.children
        elif self.tagname not in VOID_ELEMENTS:
            yield from super()._generate_html()
        if self.has_closing_tag():
            yield '</'
            yield self.tagname
            yield '>'

class DocumentElement(Element):
    def __init__(self):
        super().__init__(None, '!doctype', html=True)
    def has_closing_tag(self):
        return False

class ElementCollection(Node):
    def __repr__(self):
        return f'<{self.children}>'

class CommentNode(Node):
    def __init__(self, comment_text):
        self.comment_text = comment_text
        super().__init__()
    def _generate_html(self):
        yield '<!-- '
        yield to_html(self.comment_text)
        yield ' -->'

class ComponentContents:
    def __init__(self, context, *args):
        self.context = context
        if len(args) == 1:
            self.args, = args
        else:
            self.args = args

class Context:
    def __init__(self, item):
        self._element_stack = [item]
    def push(self, item):
        self._element_stack.append(item)
    def pop(self, item):
        top = self._element_stack.pop()
        assert top == item
        self.add(top)
    def add(self, item):
        self._element_stack[-1].add(item)
    def __getattr__(self, attr):
        return partial(Element, self, attr)
    def collect(self):
        assert len(self._element_stack) == 1
        return self._element_stack[0]
    def insert_contents(self, *args):
        return ComponentContents(self, *args)
    def insert_comment(self, comment_text):
        return CommentNode(comment_text)

def _make_nodes(_f, _root, *args, **kwargs):
    h = Context(_root)
    for item in _f(h, *args, **kwargs):
        h.add(item)
    return h.collect()

class Component:
    def __init__(self, _f, h, *args, **kwargs):
        self.it = _f(h, *args, **kwargs)
        self.h = h
        self.args = args
        self.kwargs = kwargs
    def __iter__(self):
        for item in self.it:
            if isinstance(item, ComponentContents):
                yield item.args
            else:
                self.h.add(item)
    def __enter__(self):
        for item in self.it:
            if isinstance(item, ComponentContents):
                return item.args
            self.h.add(item)
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            return
        for item in self.it:
            if isinstance(item, ComponentContents):
                raise InvalidHTML('component invoked as as a context manager, but has multiple instances of h.insert_contents()')
            self.h.add(item)

@decorator(insert_args=1)
def fragment(_f, *args, **kwargs):
    return _make_nodes(_f, ElementCollection(), *args, **kwargs)

@decorator(insert_args=1)
def document(_f, *args, **kwargs):
    return _make_nodes(_f, DocumentElement(), *args, **kwargs)

@decorator
def component(_f, *args, **kwargs):
    return Component(_f, *args, **kwargs)
