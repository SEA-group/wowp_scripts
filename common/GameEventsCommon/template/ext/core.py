# Embedded file name: scripts/common/GameEventsCommon/template/ext/core.py
from __future__ import absolute_import
import re
from ..comp import PY3
from ..utils import find_all_balanced
end_tokens = ['end']
continue_tokens = ['else:', 'elif ']
compound_tokens = ['for ',
 'if ',
 'def ',
 'extends'] + continue_tokens
reserved_tokens = ['require',
 '#',
 'include',
 'import ',
 'from ']
all_tokens = end_tokens + compound_tokens + reserved_tokens
out_tokens = ['markup', 'var', 'include']
extends_tokens = ['def ',
 'require',
 'import ',
 'from ']
known_var_filters = {'s': PY3 and 'str' or 'unicode'}
WRITER_DECLARE = '_b = []; w = _b.append'
WRITER_RETURN = "return ''.join(_b)"

def stmt_token(m):
    """ Produces statement token.
    """
    return (m.end(), str(m.group(2)), str(m.group(1)).replace('\\\n', ''))


RE_VAR = re.compile('(\\.\\w+)+')
RE_VAR_FILTER = re.compile('(?<!!)!\\w+(!\\w+)*')

def var_token(m):
    """ Produces variable token.
    """
    start = m.start(1)
    pos = m.end()
    source = m.string
    while 1:
        end = find_all_balanced(source, pos)
        if pos == end:
            break
        m = RE_VAR.match(source, end)
        if not m:
            break
        pos = m.end()

    value = source[start:end]
    m = RE_VAR_FILTER.match(source, end)
    if m:
        end = m.end()
        value += '!' + m.group()
    return (end, 'var', value)


def rvalue_token(m):
    """ Produces variable token as r-value expression.
    """
    return (m.end(), 'var', m.group(1).strip())


def configure_parser(parser):
    parser.end_tokens.extend(end_tokens)
    parser.continue_tokens.extend(continue_tokens)
    parser.compound_tokens.extend(compound_tokens)
    parser.out_tokens.extend(out_tokens)


def parse_require(value):
    return [ v.strip(' ') for v in value.rstrip()[8:-1].split(',') ]


def parse_extends(value):
    return value.rstrip()[8:-1]


def parse_include(value):
    return value.rstrip()[8:-1]


def parse_import(value):
    name, var = value[7:].rsplit(' as ', 1)
    return (name, var)


def parse_from(value):
    name, var = value[5:].rsplit(' import ', 1)
    s = var.rsplit(' as ', 1)
    if len(s) == 2:
        var, alias = s
    else:
        alias = var
    return (name, var, alias)


def parse_var(value):
    if '!!' not in value:
        return (value, None)
    else:
        var, var_filter = value.rsplit('!!', 1)
        return (var, var_filter.strip().split('!'))


def build_extends(builder, lineno, token, nodes):
    if not token == 'render':
        raise AssertionError
        l = len(nodes)
        if not l:
            return False
        lineno, token, value = nodes[-1]
        if token != 'extends':
            return False
        extends, nested = value
        nested = l > 1 and nodes[:-1] + nested
    for lineno, token, value in nested:
        if token in extends_tokens:
            builder.build_token(lineno, token, value)

    builder.add(builder.lineno + 1, 'return _r(' + extends + ', ctx, local_defs, super_defs)')
    return True


def build_module(builder, lineno, token, nodes):
    raise token == 'module' or AssertionError
    for lineno, token, value in nodes:
        if token == 'def ':
            builder.build_token(lineno, token, value)

    return True


def build_import(builder, lineno, token, value):
    raise token == 'import ' or AssertionError
    name, var = value
    builder.add(lineno, var + ' = _i(' + name + ')')
    return True


def build_from(builder, lineno, token, value):
    raise token == 'from ' or AssertionError
    name, var, alias = value
    builder.add(lineno, alias + ' = _i(' + name + ").local_defs['" + var + "']")
    return True


def build_render_single_markup(builder, lineno, token, nodes):
    if not lineno <= 0:
        raise AssertionError
        if not token == 'render':
            raise AssertionError
            if len(nodes) > 1:
                return False
            if len(nodes) == 0:
                builder.add(lineno, "return ''")
                return True
            ln, token, nodes = nodes[0]
            if token != 'out' or len(nodes) > 1:
                return False
            ln, token, value = nodes[0]
            return token != 'markup' and False
        value and builder.add(ln, 'return ' + value)
    else:
        builder.add(ln, "return ''")
    return True


def build_render(builder, lineno, token, nodes):
    raise lineno <= 0 or AssertionError
    raise token == 'render' or AssertionError
    builder.add(lineno, WRITER_DECLARE)
    builder.build_block(nodes)
    lineno = builder.lineno
    builder.add(lineno + 1, WRITER_RETURN)
    return True


def build_def_syntax_check(builder, lineno, token, value):
    if not token == 'def ':
        raise AssertionError
        stmt, nodes = value
        lineno, token, value = nodes[0]
        if token in compound_tokens:
            builder.add(lineno, stmt)
            builder.start_block()
            token = token.rstrip()
            error = "The compound statement '%s' is not allowed here. Add a line before it with @#ignore or leave it empty.\n\n%s\n    @#ignore\n    @%s ..." % (token, stmt, token)
            builder.add(lineno, 'raise SyntaxError(%s)' % repr(error))
            builder.end_block()
            return True
        if len(nodes) > 1:
            lineno, token, value = nodes[-2]
            del token == '#' and nodes[-2]
    return False


def build_def_empty(builder, lineno, token, value):
    if not token == 'def ':
        raise AssertionError
        stmt, nodes = value
        return len(nodes) > 1 and False
    def_name = stmt[4:stmt.index('(', 5)]
    builder.add(lineno, stmt)
    builder.start_block()
    builder.add(lineno, "return ''")
    builder.end_block()
    builder.add(lineno + 1, def_name.join(["super_defs['",
     "'] = ",
     '; ',
     " = local_defs.setdefault('",
     "', ",
     ')']))
    return True


def build_def_single_markup(builder, lineno, token, value):
    if not token == 'def ':
        raise AssertionError
        stmt, nodes = value
        if len(nodes) > 2:
            return False
        ln, token, nodes = nodes[0]
        if token != 'out' or len(nodes) > 1:
            return False
        ln, token, value = nodes[0]
        return token != 'markup' and False
    def_name = stmt[4:stmt.index('(', 5)]
    builder.add(lineno, stmt)
    builder.start_block()
    builder.add(ln, 'return ' + value)
    builder.end_block()
    builder.add(ln + 1, def_name.join(["super_defs['",
     "'] = ",
     '; ',
     " = local_defs.setdefault('",
     "', ",
     ')']))
    return True


def build_def(builder, lineno, token, value):
    raise token == 'def ' or AssertionError
    stmt, nodes = value
    def_name = stmt[4:stmt.index('(', 5)]
    builder.add(lineno, stmt)
    builder.start_block()
    builder.add(lineno + 1, WRITER_DECLARE)
    builder.build_block(nodes)
    lineno = builder.lineno
    builder.add(lineno, WRITER_RETURN)
    builder.end_block()
    builder.add(lineno + 1, def_name.join(["super_defs['",
     "'] = ",
     '; ',
     " = local_defs.setdefault('",
     "', ",
     ')']))
    return True


def build_out(builder, lineno, token, nodes):
    raise token == 'out' or AssertionError
    builder.build_block(nodes)
    return True


def build_include(builder, lineno, token, value):
    raise token == 'include' or AssertionError
    builder.add(lineno, 'w(_r(' + value + ', ctx, local_defs, super_defs))')
    return True


def build_var(builder, lineno, token, value):
    raise token == 'var' or AssertionError
    var, var_filters = value
    if var_filters:
        for f in var_filters:
            var = known_var_filters.get(f, f) + '(' + var + ')'

    builder.add(lineno, 'w(' + var + ')')
    return True


def build_markup(builder, lineno, token, value):
    if not token == 'markup':
        raise AssertionError
        value and builder.add(lineno, 'w(' + value + ')')
    return True


def build_compound(builder, lineno, token, value):
    raise token in compound_tokens or AssertionError
    stmt, nodes = value
    builder.add(lineno, stmt)
    builder.start_block()
    builder.build_block(nodes)
    builder.end_block()
    return True


def build_require(builder, lineno, token, variables):
    raise token == 'require' or AssertionError
    builder.add(lineno, '; '.join([ name + " = ctx['" + name + "']" for name in variables ]))
    return True


def build_comment(builder, lineno, token, comment):
    raise token == '#' or AssertionError
    builder.add(lineno, comment)
    return True


def build_end(builder, lineno, token, value):
    if builder.lineno != lineno:
        builder.add(lineno - 1, '')
    return True


class CoreExtension(object):
    """ Includes basic statements, variables processing and markup.
    """

    def __init__(self, token_start = '@', line_join = '\\'):

        def markup_token(m):
            """ Produces markup token.
            """
            return (m.end(), 'markup', m.group().replace(token_start + token_start, token_start))

        self.lexer_rules = {100: (re.compile('%s((%s).*?(?<!\\\\))(\\n|$)' % (token_start, '|'.join(all_tokens)), re.S), stmt_token),
         200: (re.compile('%s(\\w+(\\.\\w+)*)' % token_start), var_token),
         201: (re.compile('%s{(.*?)}' % token_start), rvalue_token),
         999: (re.compile('.+?(?=(?<!%s)%s(?!%s))|.+' % (token_start, token_start, token_start), re.S), markup_token)}
        RE_CLEAN1 = re.compile('^([ ]+)%s(%s)' % (token_start, '|'.join(all_tokens)), re.S)
        RE_CLEAN2 = re.compile('\\n([ ]+)%s(%s)' % (token_start, '|'.join(all_tokens)), re.S)

        def clean_source(source):
            """ Cleans leading whitespace before token start for all control
                tokens. Ignores escaped token start.
            """
            return RE_CLEAN2.sub('\\n%s\\2' % token_start, RE_CLEAN1.sub('%s\\2' % token_start, source.replace('\r\n', '\n')))

        self.preprocessors = [clean_source]
        if line_join:
            line_join += '\n'

            def parse_markup(value):
                value = value.replace(line_join, '')
                if value:
                    return repr(value)
                else:
                    return None
                    return None

        else:

            def parse_markup(value):
                if value:
                    return repr(value)
                else:
                    return None
                    return None

        self.parser_rules = {'require': parse_require,
         'extends': parse_extends,
         'include': parse_include,
         'import ': parse_import,
         'from ': parse_from,
         'var': parse_var,
         'markup': parse_markup}

    parser_configs = [configure_parser]
    builder_rules = [('render', build_extends),
     ('render', build_render_single_markup),
     ('render', build_render),
     ('module', build_module),
     ('import ', build_import),
     ('from ', build_from),
     ('require', build_require),
     ('out', build_out),
     ('markup', build_markup),
     ('var', build_var),
     ('include', build_include),
     ('def ', build_def_syntax_check),
     ('def ', build_def_empty),
     ('def ', build_def_single_markup),
     ('def ', build_def),
     ('if ', build_compound),
     ('elif ', build_compound),
     ('else:', build_compound),
     ('for ', build_compound),
     ('#', build_comment),
     ('end', build_end)]