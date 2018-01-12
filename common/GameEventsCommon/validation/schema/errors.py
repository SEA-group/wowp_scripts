# Embedded file name: scripts/common/GameEventsCommon/validation/schema/errors.py
""" This module contains the error-related constants and classes. """
from __future__ import absolute_import
from collections import defaultdict, namedtuple, MutableMapping
from copy import copy, deepcopy
from functools import wraps
from pprint import pformat
from .utils import compare_paths_lt, quote_string
ErrorDefinition = namedtuple('schema_error', 'code, rule')
CUSTOM = ErrorDefinition(0, None)
DOCUMENT_MISSING = ErrorDefinition(1, None)
DOCUMENT_MISSING = 'document is missing'
REQUIRED_FIELD = ErrorDefinition(2, 'required')
UNKNOWN_FIELD = ErrorDefinition(3, None)
DEPENDENCIES_FIELD = ErrorDefinition(4, 'dependencies')
DEPENDENCIES_FIELD_VALUE = ErrorDefinition(5, 'dependencies')
EXCLUDES_FIELD = ErrorDefinition(6, 'excludes')
DOCUMENT_FORMAT = ErrorDefinition(33, None)
DOCUMENT_FORMAT = "'{0}' is not a document, must be a dict"
EMPTY_NOT_ALLOWED = ErrorDefinition(34, 'empty')
NOT_NULLABLE = ErrorDefinition(35, 'nullable')
BAD_TYPE = ErrorDefinition(36, 'type')
BAD_TYPE_FOR_SCHEMA = ErrorDefinition(37, 'schema')
ITEMS_LENGTH = ErrorDefinition(38, 'items')
MIN_LENGTH = ErrorDefinition(39, 'minlength')
MAX_LENGTH = ErrorDefinition(40, 'maxlength')
REGEX_MISMATCH = ErrorDefinition(65, 'regex')
MIN_VALUE = ErrorDefinition(66, 'min')
MAX_VALUE = ErrorDefinition(67, 'max')
UNALLOWED_VALUE = ErrorDefinition(68, 'allowed')
UNALLOWED_VALUES = ErrorDefinition(69, 'allowed')
FORBIDDEN_VALUE = ErrorDefinition(70, 'forbidden')
FORBIDDEN_VALUES = ErrorDefinition(71, 'forbidden')
NORMALIZATION = ErrorDefinition(96, None)
COERCION_FAILED = ErrorDefinition(97, 'coerce')
RENAMING_FAILED = ErrorDefinition(98, 'rename_handler')
READONLY_FIELD = ErrorDefinition(99, 'readonly')
SETTING_DEFAULT_FAILED = ErrorDefinition(100, 'default_setter')
ERROR_GROUP = ErrorDefinition(128, None)
MAPPING_SCHEMA = ErrorDefinition(129, 'schema')
SEQUENCE_SCHEMA = ErrorDefinition(130, 'schema')
KEYSCHEMA = ErrorDefinition(131, 'keyschema')
VALUESCHEMA = ErrorDefinition(132, 'valueschema')
BAD_ITEMS = ErrorDefinition(143, 'items')
LOGICAL = ErrorDefinition(144, None)
NONEOF = ErrorDefinition(145, 'noneof')
ONEOF = ErrorDefinition(146, 'oneof')
ANYOF = ErrorDefinition(147, 'anyof')
ALLOF = ErrorDefinition(148, 'allof')
SCHEMA_ERROR_DEFINITION_TYPE = "schema definition for field '{0}' must be a dict"
SCHEMA_ERROR_MISSING = 'validation schema missing'

class ValidationError(object):
    """ A simple class to store and query basic error information. """

    def __init__(self, document_path, schema_path, code, rule, constraint, value, info):
        self.document_path = document_path
        self.schema_path = schema_path
        self.code = code
        self.rule = rule
        self.constraint = constraint
        self.value = value
        self.info = info

    def __eq__(self, other):
        """ Assumes the errors relate to the same document and schema. """
        return hash(self) == hash(other)

    def __hash__(self):
        """ Expects that all other properties are transitively determined. """
        return hash(self.document_path) ^ hash(self.schema_path) ^ hash(self.code)

    def __lt__(self, other):
        if self.document_path != other.document_path:
            return compare_paths_lt(self.document_path, other.document_path)
        else:
            return compare_paths_lt(self.schema_path, other.schema_path)

    def __repr__(self):
        return '{class_name} @ {memptr} ( document_path={document_path},schema_path={schema_path},code={code},constraint={constraint},value={value},info={info} )'.format(class_name=self.__class__.__name__, memptr=hex(id(self)), document_path=self.document_path, schema_path=self.schema_path, code=hex(self.code), constraint=quote_string(self.constraint), value=quote_string(self.value), info=self.info)

    @property
    def child_errors(self):
        """
        A list that contains the individual errors of a bulk validation error.
        """
        if self.is_group_error:
            return self.info[0]
        else:
            return None

    @property
    def definitions_errors(self):
        """ Dictionary with errors of an *of-rule mapped to the index of the
        definition it occurred in. Returns :obj:`None` if not applicable.
        """
        if not self.is_logic_error:
            return None
        else:
            result = defaultdict(list)
            for error in self.child_errors:
                i = error.schema_path[len(self.schema_path)]
                result[i].append(error)

            return result

    @property
    def field(self):
        """ Field of the contextual mapping, possibly :obj:`None`. """
        if self.document_path:
            return self.document_path[-1]
        else:
            return None
            return None

    @property
    def is_group_error(self):
        """ ``True`` for errors of bulk validations. """
        return bool(self.code & ERROR_GROUP.code)

    @property
    def is_logic_error(self):
        """ ``True`` for validation errors against different schemas with
        *of-rules. """
        return bool(self.code & LOGICAL.code - ERROR_GROUP.code)

    @property
    def is_normalization_error(self):
        """ ``True`` for normalization errors. """
        return bool(self.code & NORMALIZATION.code)


class ErrorList(list):
    """ A list for :class:`~.errrors.ValidationError` instances that
    can be queried with the ``in`` keyword for a particular error code. """

    def __contains__(self, error_definition):
        for code in (x.code for x in self):
            if code == error_definition.code:
                return True

        return False


class ErrorTreeNode(MutableMapping):
    __slots__ = ('descendants', 'errors', 'parent_node', 'path', 'tree_root')

    def __init__(self, path, parent_node):
        self.parent_node = parent_node
        self.tree_root = self.parent_node.tree_root
        self.path = path[:self.parent_node.depth + 1]
        self.errors = ErrorList()
        self.descendants = {}

    def __add__(self, error):
        self.add(error)
        return self

    def __delitem__(self, key):
        del self.descendants[key]

    def __iter__(self):
        return iter(self.errors)

    def __getitem__(self, item):
        return self.descendants.get(item)

    def __len__(self):
        return len(self.errors)

    def __setitem__(self, key, value):
        self.descendants[key] = value

    def __str__(self):
        return str(self.errors) + ',' + str(self.descendants)

    @property
    def depth(self):
        return len(self.path)

    @property
    def tree_type(self):
        return self.tree_root.tree_type

    def add(self, error):
        error_path = self._path_of_(error)
        key = error_path[self.depth]
        if key not in self.descendants:
            self[key] = ErrorTreeNode(error_path, self)
        if len(error_path) == self.depth + 1:
            self[key].errors.append(error)
            self[key].errors.sort()
            if error.is_group_error:
                for child_error in error.child_errors:
                    self.tree_root += child_error

        else:
            self[key] += error

    def _path_of_(self, error):
        return getattr(error, self.tree_type + '_path')


class ErrorTree(ErrorTreeNode):
    """ Base class for :class:`~.errors.DocumentErrorTree` and
    :class:`~.errors.SchemaErrorTree`. """

    def __init__(self, errors = []):
        self.parent_node = None
        self.tree_root = self
        self.path = ()
        self.errors = ErrorList()
        self.descendants = {}
        for error in errors:
            self += error

        return

    def add(self, error):
        """ Add an error to the tree.
        
        :param error: :class:`~.errors.ValidationError`
        """
        if not self._path_of_(error):
            self.errors.append(error)
            self.errors.sort()
        else:
            super(ErrorTree, self).add(error)

    def fetch_errors_from(self, path):
        """ Returns all errors for a particular path.
        
        :param path: :class:`tuple` of :term:`hashable` s.
        :rtype: :class:`~.errors.ErrorList`
        """
        node = self.fetch_node_from(path)
        if node is not None:
            return node.errors
        else:
            return ErrorList()
            return

    def fetch_node_from(self, path):
        """ Returns a node for a path.
        
        :param path: Tuple of :term:`hashable` s.
        :rtype: :class:`~.errors.ErrorTreeNode` or :obj:`None`
        """
        context = self
        for key in path:
            context = context[key]
            if context is None:
                break

        return context


class DocumentErrorTree(ErrorTree):
    """ Implements a dict-like class to query errors by indexes following the
    structure of a validated document. """
    tree_type = 'document'


class SchemaErrorTree(ErrorTree):
    """ Implements a dict-like class to query errors by indexes following the
    structure of the used schema. """
    tree_type = 'schema'


class BaseErrorHandler(object):
    """ Base class for all error handlers.
    Subclasses are identified as error-handlers with an instance-test. """

    def __init__(self, *args, **kwargs):
        """ Optionally initialize a new instance. """
        pass

    def __call__(self, errors):
        """ Returns errors in a handler-specific format.
        
        :param errors: An object containing the errors.
        :type errors: :term:`iterable` of
                      :class:`~.errors.ValidationError` instances or a
                      :class:`~.Validator` instance
        """
        raise NotImplementedError

    def __iter__(self):
        """ Be a superhero and implement an iterator over errors. """
        raise NotImplementedError

    def add(self, error):
        """ Add an error to the errors' container object of a handler.
        
        :param error: The error to add.
        :type error: :class:`~.errors.ValidationError`
        """
        raise NotImplementedError

    def emit(self, error):
        """ Optionally emits an error in the handler's format to a stream.
            Or light a LED, or even shut down a power plant.
        
        :param error: The error to emit.
        :type error: :class:`~.errors.ValidationError`
        """
        pass

    def end(self, validator):
        """ Gets called when a validation ends.
        
        :param validator: The calling validator.
        :type validator: :class:`~.Validator` """
        pass

    def extend(self, errors):
        """ Adds all errors to the handler's container object.
        
        :param errors: The errors to add.
        :type errors: :term:`iterable` of
                      :class:`~.errors.ValidationError` instances
        """
        for error in errors:
            self.add(error)

    def start(self, validator):
        """ Gets called when a validation starts.
        
        :param validator: The calling validator.
        :type validator: :class:`~.Validator`
        """
        pass


class ToyErrorHandler(BaseErrorHandler):

    def __call__(self, *args, **kwargs):
        raise RuntimeError('This is not supposed to happen.')

    def clear(self):
        pass


def encode_unicode(f):
    """. error messages expect regular binary strings.
    If unicode is used in a ValidationError message can't be printed.
    
    This decorator ensures that if legacy Python is used unicode
    strings are encoded before passing to a function.
    """

    @wraps(f)
    def wrapped(obj, error):

        def _encode(value):
            """Helper encoding unicode strings into binary utf-8"""
            if isinstance(value, unicode):
                return value.encode('utf-8')
            return value

        error = copy(error)
        error.document_path = _encode(error.document_path)
        error.schema_path = _encode(error.schema_path)
        error.constraint = _encode(error.constraint)
        error.value = _encode(error.value)
        error.info = _encode(error.info)
        return f(obj, error)

    return wrapped


class BasicErrorHandler(BaseErrorHandler):
    """ Models .' legacy. Returns a :class:`dict`. """
    messages = {0: '{0}',
     1: 'document is missing',
     2: 'required field',
     3: 'unknown field',
     4: "field '{0}' is required",
     5: 'depends on these values: {constraint}',
     6: "{0} must not be present with '{field}'",
     33: "'{0}' is not a document, must be a dict",
     34: 'empty values not allowed',
     35: 'null value not allowed',
     36: 'must be of {constraint} type',
     37: 'must be of dict type',
     38: 'length of list should be {constraint}, it is {0}',
     39: 'min length is {constraint}',
     40: 'max length is {constraint}',
     65: "value does not match regex '{constraint}'",
     66: 'min value is {constraint}',
     67: 'max value is {constraint}',
     68: 'unallowed value {value}',
     69: 'unallowed values {0}',
     70: 'unallowed value {value}',
     71: 'unallowed values {0}',
     97: "field '{field}' cannot be coerced: {0}",
     98: "field '{field}' cannot be renamed: {0}",
     99: 'field is read-only',
     100: "default value for '{field}' cannot be set: {0}",
     129: "mapping doesn't validate subschema: {0}",
     130: "one or more sequence-items don't validate: {0}",
     131: "one or more keys of a mapping  don't validate: {0}",
     132: "one or more values in a mapping don't validate: {0}",
     133: "one or more sequence-items don't validate: {0}",
     145: 'one or more definitions validate',
     146: 'none or more than one rule validate',
     147: 'no definitions validate',
     148: "one or more definitions don't validate"}

    def __init__(self, tree = None):
        self.tree = {} if tree is None else tree
        return

    def __call__(self, errors = None):
        if errors is not None:
            self.clear()
            self.extend(errors)
        return self.pretty_tree

    def __str__(self):
        return pformat(self.pretty_tree)

    @encode_unicode
    def add(self, error):
        if error.is_logic_error:
            self.insert_logic_error(error)
        elif error.is_group_error:
            self.insert_group_error(error)
        elif error.code in self.messages:
            self.insert_error(error.document_path, self.format_message(error.field, error))

    def clear(self):
        self.tree = {}

    def format_message(self, field, error):
        return self.messages[error.code].format(constraint=error.constraint, field=field, value=error.value, *error.info)

    def insert_error(self, path, node):
        """ Adds an error or sub-tree to :attr:tree.
        
        :param path: Path to the error.
        :type path: Tuple of strings and integers.
        :param node: An error message or a sub-tree.
        :type node: String or dictionary.
        """
        field = path[0]
        if len(path) == 1:
            if field in self.tree:
                subtree = self.tree[field].pop()
                self.tree[field] += [node, subtree]
            else:
                self.tree[field] = [node, {}]
        elif len(path) >= 1:
            if field not in self.tree:
                self.tree[field] = [{}]
            subtree = self.tree[field][-1]
            if subtree:
                new = self.__class__(tree=copy(subtree))
            else:
                new = self.__class__()
            new.insert_error(path[1:], node)
            subtree.update(new.tree)

    def insert_group_error(self, error):
        for error in error.child_errors:
            if error.is_logic_error:
                self.insert_logic_error(error)
            elif error.is_group_error:
                self.insert_group_error(error)
            else:
                self.insert_error(error.document_path, self.format_message(error.field, error))

    def insert_logic_error(self, error):
        path = error.document_path + (error.rule,)
        field = error.field
        self.insert_error(path, self.format_message(field, error))
        for i in error.definitions_errors:
            child_errors = error.definitions_errors[i]
            if not child_errors:
                continue
            nodename = '%s definition %s' % (error.rule, i)
            for child_error in child_errors:
                if child_error.is_logic_error:
                    raise NotImplementedError
                elif child_error.is_group_error:
                    raise NotImplementedError
                else:
                    self.insert_error(path + (nodename,), self.format_message(field, child_error))

    @property
    def pretty_tree(self):
        pretty = deepcopy(self.tree)
        for field in pretty:
            self._purge_empty_dicts(pretty[field])

        return pretty

    def _purge_empty_dicts(self, error_list):
        subtree = error_list[-1]
        if not error_list[-1]:
            error_list.pop()
        else:
            for key in subtree:
                self._purge_empty_dicts(subtree[key])

    def start(self, validator):
        self.clear()


class SchemaErrorHandler(BasicErrorHandler):
    messages = BasicErrorHandler.messages.copy()
    messages[3] = 'unknown rule'