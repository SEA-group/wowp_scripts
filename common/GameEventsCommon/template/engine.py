# Embedded file name: scripts/common/GameEventsCommon/template/engine.py
from __future__ import absolute_import
from .builder import SourceBuilder
from .builder import builder_scan
from .comp import allocate_lock
from .compiler import Compiler
from .lexer import Lexer
from .lexer import lexer_scan
from .parser import Parser
from .parser import parser_scan

class Engine(object):
    """ The core component of template engine.
    """

    def __init__(self, loader, extensions, template_class = None):
        self.lock = allocate_lock()
        self.templates = {}
        self.renders = {}
        self.modules = {}
        self.global_vars = {'_r': self.render,
         '_i': self.import_name}
        self.loader = loader
        self.template_class = template_class or Template
        self.compiler = Compiler(self.global_vars, -2)
        self.lexer = Lexer(**lexer_scan(extensions))
        self.parser = Parser(**parser_scan(extensions))
        self.builder = SourceBuilder(**builder_scan(extensions))

    def get_template(self, name):
        """ Returns compiled template.
        """
        try:
            return self.templates[name]
        except KeyError:
            self.compile_template(name)
            return self.templates[name]

    def render(self, name, ctx, local_defs, super_defs):
        """ Renders template by name in given context.
        """
        try:
            return self.renders[name](ctx, local_defs, super_defs)
        except KeyError:
            self.compile_template(name)
            return self.renders[name](ctx, local_defs, super_defs)

    def remove(self, name):
        """ Removes given ``name`` from internal cache.
        """
        self.lock.acquire(1)
        try:
            if name in self.renders:
                del self.templates[name]
                del self.renders[name]
            if name in self.modules:
                del self.modules[name]
        finally:
            self.lock.release()

    def import_name(self, name):
        try:
            return self.modules[name]
        except KeyError:
            self.compile_import(name)
            return self.modules[name]

    def compile_template(self, name):
        self.lock.acquire(1)
        try:
            if name not in self.renders:
                template_source = self.loader.load(name)
                if template_source is None:
                    raise IOError('Template "%s" not found.' % name)
                tokens = self.lexer.tokenize(template_source)
                nodes = self.parser.parse(tokens)
                source = self.builder.build_render(nodes)
                render_template = self.compiler.compile_source(source, name)['render']
                self.renders[name] = render_template
                self.templates[name] = self.template_class(name, render_template)
        finally:
            self.lock.release()

        return

    def compile_import(self, name):
        self.lock.acquire(1)
        try:
            if name not in self.modules:
                template_source = self.loader.load(name)
                if template_source is None:
                    raise IOError('Import "%s" not found.' % name)
                tokens = self.lexer.tokenize(template_source)
                nodes = self.parser.parse(tokens)
                source = self.builder.build_module(nodes)
                self.modules[name] = self.compiler.compile_module(source, name)
        finally:
            self.lock.release()

        return

    def print_debug(self, name, tokens, nodes, source):
        print name.center(80, '-')
        from pprint import pprint
        pprint(nodes)
        from .utils import print_source
        print_source(source, -1)


class Template(object):
    """ Simple template class.
    """
    __slots__ = ('name', 'render_template')

    def __init__(self, name, render_template):
        self.name = name
        self.render_template = render_template

    def render(self, ctx):
        return self.render_template(ctx, {}, {})