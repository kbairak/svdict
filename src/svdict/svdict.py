from collections import UserDict, UserList
from collections.abc import MutableMapping, MutableSequence
from copy import deepcopy
from functools import wraps

from jsonschema import ValidationError

from .validators import SVValidator


# Handle mutating methods
def _mutator(func, argpos=None, kwargkey=None, many=False):
    """ Decorator for dict/list mutating methods. Decorated method:

        1. Triggers validation and restore
        2. Makes sure added items are converted to SVDict/SVList classes that
           trigger the parent's validation

        The class of the methods that are decorated must implement the
        `_backup`, `_validate` and `_restore` methods.

        Arguments:

            - func: the function to be decorated
            - argpos: the position of the added items in the mutating method's
                      arguments
            - kwargkey: the name of the kwarg of the added items in the
                        mutating method's arguments
            - many: wether the argument is an item or a sequence of items

        Usage:

            >>> class Foo(UserList):
            ...     def _backup(self):
            ...         print("Backing up")
            ...
            ...     def _validate(self):
            ...         print("Validating")
            ...
            ...     def _restore(self):
            ...         print("Restoring")
            ...
            ...     __setitem__ = _mutator(UserList.__setitem__, 1)
            ...     extend = _mutator(UserList.extend, 0, many=True)
    """

    @wraps(func)
    def decorated(self, *args, **kwargs):
        self._backup()
        value, found = None, None
        if kwargkey is not None:
            try:
                value = kwargs.pop(kwargkey)
            except KeyError:
                pass
            else:
                found = 'kwargs'
        if found is None and argpos is not None:
            args = list(args)
            value = args[argpos]
            found = 'args'

        if value is not None:
            if many:
                value = SVList((_mutate(item, self) for item in value),
                               _parent=self)
            else:
                value = _mutate(value, self)

        if found == "kwargs":
            kwargs[kwargkey] = value
        elif found == "args":
            args[argpos] = value

        result = func(self, *args, **kwargs)

        try:
            self._validate()
        except ValidationError:
            self._restore()
            raise
        else:
            return result
    return decorated


def _mutate(value, self):
    if isinstance(value, MutableMapping):
        value = SVDict(value, _parent=self)
    elif isinstance(value, MutableSequence):
        value = SVList(value, _parent=self)
    return value


# Actual classes
class _SVBase:
    SCHEMA = None

    def _backup(self):
        self._backup_data = deepcopy(self.data)

    def _validate(self):
        if self._initializing:
            return
        if self.SCHEMA is not None:
            self._validator.validate(self)
        if self._parent is not None:
            self._parent._validate()

    def __init__(self, *args, _parent=None, **kwargs):
        self._parent = _parent
        if self.SCHEMA is not None:
            self._validator = SVValidator(schema=self.SCHEMA)
        self._initializing = True
        super().__init__(*args, **kwargs)
        self._initializing = False
        self._validate()


class SVDict(_SVBase, UserDict):
    def _restore(self):
        self.data.clear()
        for key, value in self._backup_data.items():
            self.data[key] = value

    __setitem__ = _mutator(UserDict.__setitem__, 1, 'item')
    __delitem__ = _mutator(UserDict.__delitem__)


class SVList(_SVBase, UserList):
    def _restore(self):
        self.data.clear()
        self.data.extend(self._backup_data)

    __setitem__ = _mutator(UserList.__setitem__, 1, 'item')
    __delitem__ = _mutator(UserList.__delitem__)
    append = _mutator(UserList.append, 0, 'item')
    insert = _mutator(UserList.insert, 1, 'item')
    pop = _mutator(UserList.pop)
    remove = _mutator(UserList.remove)
    clear = _mutator(UserList.clear)

    extend = _mutator(UserList.extend, 0, 'other', many=True)
    __iadd__ = _mutator(UserList.__iadd__, 0, 'other', many=True)
