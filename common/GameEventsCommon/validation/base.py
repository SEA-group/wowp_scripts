# Embedded file name: scripts/common/GameEventsCommon/validation/base.py
from functools import wraps
from collections import OrderedDict

class ValidationError(Exception):
    """All kwargs passed to exception is seted to instance. Also using
    `DEFAULTS` param you can set default values if they not passed to
    exception class"""
    DEFAULTS = {}

    def __init__(self, message = '', **kwargs):
        super(ValidationError, self).__init__(message)
        params = self.DEFAULTS.copy()
        params.update(kwargs)
        self.params = params
        self.message = message


class StopValidation(ValidationError):
    """Used for stopping validation if we have some special data or case."""
    DEFAULTS = {'isValid': True}


class ValidationBase(object):
    """Base validation logic for any class, just add methods
    using 'register' or delete by 'unregister' decorators
    call `validate` and then all data will be processed
    """

    def __init__(self, validators = None, context = None, exceptionClass = ValidationError, chained = False, errorHandlers = None):
        self._errors = {}
        self._isValid = False
        self._context = context
        self._validators = OrderedDict()
        self._errorHandler = None
        self._exceptionClass = exceptionClass
        self._chained = chained
        self._stopValidation = False
        if validators:
            self.register(*validators)
        if errorHandlers:
            for errorHandler in errorHandlers:
                self.registerErrorHandler(errorHandler)

        return

    @property
    def errors(self):
        return self._errors

    @property
    def isValid(self):
        return self._isValid

    @property
    def validators(self):
        return self._validators

    def register(self, *validators):
        for validator in validators:
            name = None
            if isinstance(validator, (list, tuple)):
                validator, name = validator
            name = name or validator.__name__
            self._validators[name] = validator

        return

    def registerErrorHandler(self, f):
        self._errorHandler = f

    def addErrorMessage(self, name, message, context = None):
        self._errors[name] = self._exceptionClass(message)
        if self._errorHandler is not None and self._chained:
            self._errorHandler(error, context)
        return

    def validate(self, *validators, **settings):
        """Loop throught all validators and check if we have any invalid"""
        self._errors = {}
        self._isValid = True
        self._stopValidation = False
        context = self._context or settings.pop('context', {})
        validators = validators or self.validators.values()
        for validator in validators:
            if isinstance(validator, str):
                validator = self.validators.get(validator, None)
            if validator is None:
                self._isValid = False
                self._errors['_global'] = self._exceptionClass('Validator {} not found, please register it'.format(validator))
            else:
                self._isValid, newContext = self._process(validator, context, silent=settings.get('silent', False))
                if newContext:
                    context.update(newContext)
            if self._chained and not self._isValid or self._stopValidation:
                break

        if settings.get('returnContext', False):
            return (self._isValid, context)
        else:
            return self._isValid
            return

    def _process(self, validator, context, silent = False):
        """Runs validator and returns state with context vars setted"""
        isValid = True
        newContext = None
        self._stopValidation = False
        try:
            newContext = validator(**context)
        except (self._exceptionClass, StopValidation) as error:
            isValid = False
            if isinstance(error, StopValidation):
                self._stopValidation = True
                return (error.params['isValid'], None)
            self.errors[validator.__name__] = error
            if self._errorHandler is not None and not silent:
                self._errorHandler(error, context)

        return (isValid, newContext)


def checkIsValid(f):
    """Check instance function call, only if is_valid() called previously
    then we call it"""

    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if self.validator.isValid:
            return f(self, *args, **kwargs)
        else:
            error = self.validator._exceptionClass('Called: {} method before data validated'.format(f.__name__))
            self.validator._errors[f.__name__] = error
            if self.validator._errorHandler is not None:
                self.validator._errorHandler(error, self.getValidationContext())
            return

    return wrapper


def _createContext(instance, args, kwargs, settings):
    """Copies args and kwargs of function that will be called then
    added vars from self, for example if we have context in kwargs,
    context=('something',), kwargs will be updated by
    {'something': self.something}. ArgsToKwargs process args and adds key to it
    ArgsToKwargs=('one',) and in args (1,) dict will be {'one': 1}.
    """
    context = kwargs.copy()
    args = list(args)
    context.update({name:getattr(instance, name, None) for name in settings.get('context', [])})
    context.update({key:args.pop(0) for key in settings.get('argsTokwargs', [])})
    return context


def processIf(*filters, **settings):
    """Iterates over filters and only if they valid runs function"""

    def decorator(f):

        @wraps(f)
        def wrapper(self, *args, **kwargs):
            context = _createContext(self, args, kwargs, settings)
            for filter_ in filters:
                try:
                    newContext = filter_(**context)
                    if isinstance(newContext, dict):
                        context.update(newContext)
                except ValidationError:
                    return False

            return f(self, *args, **kwargs)

        return wrapper

    return decorator