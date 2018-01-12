# Embedded file name: scripts/common/GameEventsCommon/validation/mixin.py
from __future__ import absolute_import
from functools import wraps
from types import ClassType
from .base import ValidationError, ValidationBase

def getOrCreateValidator(f):
    """Create per class VALIDATOR instance before calling function and if
    we have subclasses then create own subclass instance of VALIDATOR_CLASS"""

    @wraps(f)
    def wrapper(selfOrClass, *args, **kwargs):
        if not isinstance(selfOrClass, (type, ClassType)):
            cls = selfOrClass.__class__
        else:
            cls = selfOrClass
        if cls.VALIDATOR_INSTANCE is None or cls.VALIDATOR_INSTANCE._class != cls.__name__:
            cls.VALIDATOR_INSTANCE = cls.VALIDATOR_CLASS(cls.VALIDATORS, exceptionClass=cls.VALIDATOR_EXCEPTION, chained=cls.VALIDATOR_CHAINED, errorHandlers=cls.VALIDATOR_ERROR_HANDLERS)
            cls.VALIDATOR_INSTANCE._class = cls.__name__
        return f(selfOrClass, *args, **kwargs)

    return wrapper


class ValidationMixin(object):
    """Provides simple validation integration to any class
    with class methods `validate` and `isValid`
    """
    VALIDATOR_CLASS = ValidationBase
    VALIDATOR_EXCEPTION = ValidationError
    VALIDATOR_CHAINED = True
    VALIDATOR_INSTANCE = None
    VALIDATOR_ERROR_HANDLERS = ()
    VALIDATORS = None

    @property
    @getOrCreateValidator
    def validator(self):
        return self.__class__.VALIDATOR_INSTANCE

    @getOrCreateValidator
    def validate(self, *validators, **settings):
        settings.setdefault('context', self.getValidationContext())
        settings.setdefault('returnContext', True)
        isValid, resultContext = self.validator.validate(*validators, **settings)
        self.afterValidation(resultContext)
        return isValid

    @property
    @getOrCreateValidator
    def isValid(self):
        return self.validator.isValid

    @property
    @getOrCreateValidator
    def validationErrors(self):
        return self.validator.errors

    @property
    @getOrCreateValidator
    def validationError(self):
        return self.validator.errors.values()[0]

    @classmethod
    @getOrCreateValidator
    def registerValidator(cls, *validators):
        cls.VALIDATOR_INSTANCE.register(*validators)

    @classmethod
    @getOrCreateValidator
    def registerValidatorErrorHandler(cls, f):
        cls.VALIDATOR_INSTANCE.registerErrorHandler(f)

    def getValidationContext(self):
        raise NotImplementedError('Must return a dict of vars for validation')

    def afterValidation(self, context):
        pass