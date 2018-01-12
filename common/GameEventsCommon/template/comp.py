# Embedded file name: scripts/common/GameEventsCommon/template/comp.py
import sys
PY3 = sys.version_info[0] >= 3
if PY3:
    from _thread import allocate_lock
else:
    from thread import allocate_lock
try:
    import ast

    def adjust_source_lineno(source, name, lineno):
        source = compile(source, name, 'exec', ast.PyCF_ONLY_AST)
        ast.increment_lineno(source, lineno)
        return source


except ImportError:

    def adjust_source_lineno(source, name, lineno):
        return source