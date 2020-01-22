""" Self-validating dictionaries using jsonschema.

    Usage, define your subclass like this:

        >>> class User(SVDict):
        ...     SCHEMA = {'type': "object",
        ...               'required': ["id", "username"],
        ...               'additionalProperties': False,
        ...               'properties': {'id': {'type': "number"},
        ...                              'username': {'type': "string"}}}

    After that, you can treat User instances as dictionaries. If however, at
    any point you leave the instance in a state that doesn't validate against
    SCHEMA, you will get an exception:

        >>> u = User()
        <<< ValidationError: ...
        >>> u = User({'id': 1, 'username': "foo"})
        >>> u = User(id=1, username="foo")
        >>> u['id'] = 2
        >>> u['id'] = "2"
        <<< ValidationError: ...

    After a ValidationError, the dictionary is restored to its previous, valid
    state:

        >>> u = User(id=1, username="foo")
        >>> u['id'] = None
        <<< ValidationError: ...
        >>> u
        <<< {'id': 1, 'username': "foo"}

    You can easily combine SCHEMAs by accessing the SCHEMA attribute of other
    SVDicts.

        >>> class Project(SVDict):
        ...     SCHEMA = {'type': "object",
        ...               'required': ["id", "slug", "owner"],
        ...               'additionalProperties': False,
        ...               'properties': {'id': {'type': "number"},
        ...                              'slug': {'type': "string"},
        ...                              'owner': {'oneOf': [{'type': "null"},
        ...                                                  User.SCHEMA]}}}

    Validations are performed on nested fields too:

        >>> p = Project(id=1, slug="foo", owner={'id': 2, 'username': "bar"})
        >>> p['owner']['username'] = None
        <<< ValidationError: ...
        >>> p
        <<< {'id': 1, 'slug': "foo", 'owner': {'id': 2, 'username': "bar"}}
        >>> p['owner'] = None
        >>> p
        <<< {'id': 1, 'slug': "foo", 'owner': None}

    Lists are also supported:

        >>> class UserList(SVList):
        ...     SCHEMA = {'type': "array", 'items': User.SCHEMA}
"""


from .svdict import SVDict, SVList, ValidationError  # noqa
