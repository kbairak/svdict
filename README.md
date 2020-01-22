Self-validating dictionaries using [jsonschema](https://json-schema.org/).

To get started with jsonschema, read [here](https://json-schema.org/understanding-json-schema/).

## Usage

Usage, define your subclass like this:

    >>> class User(SVDict):
    ...     SCHEMA = {'type': "object",
    ...               'required': ["id", "username"],
    ...               'additionalProperties': False,
    ...               'properties': {'id': {'type': "number"},
    ...                              'username': {'type': "string"}}}

After that, you can treat User instances as dictionaries. If however, at any
point you leave the instance in a state that doesn't validate against SCHEMA,
you will get an exception:

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


## Caveats

Refrain from using anything other than pure-python dicts/lists as the contents
of your SVDicts/SVLists as they will be converted upon assignment. If you use
a custom mapping or sequence implementation, you will lose all custom
functionality.

    >>> class Foo(SVDict):
    ...     SCHEMA = {'type': "object",
    ...               'properties': {'dict': {'type': "object"},
    ...                              'list': {'type': "array"}}}
    >>> class MyDict(UserDict):
    ...     def do_something_special(self):
    ...         print("Special!!!")
    >>> class MyList(UserList):
    ...     def do_something_special(self):
    ...         print("Special!!!")
    >>> my_dict = MyDict()
    >>> my_list = MyList()
    >>> foo = Foo({'dict': my_dict, 'list': my_list})

    >>> type(foo)
    <<< __main__.Foo
    >>> type(my_dict), type(foo['dict'])
    <<< (__main__.MyDict, svdict.svdict.SVDict)
    >>> type(my_list), type(foo['list'])
    <<< (__main__.MyList, svdict.svdict.SVList)

    >>> my_dict.do_something_special()
    <<< Special!!!
    >>> foo['dict'].do_something_special()
    <<< AttributeError: ...
    >>> my_list.do_something_special()
    <<< Special!!!
    >>> foo['list'].do_something_special()
    <<< AttributeError: ...

This conversion happens in order to trigger validation when a contained object
gets mutated. Otherwise, a call like:

    foo['dict']['a'] = "b"

would get translated to:

    foo.__getitem__('dict').__setitem__('a', "b")

and svdict would have no access to the child's mutating method in order to
trigger validation.


## Installation

    ➜  pip install -e .

or

    ➜  pip install .

or

    ➜  python setup.py install


## Tests

You can run the tests with pytest:

    ➜  pytest --cov=src
    =========================== test session starts ===========================
    platform linux -- Python 3.7.6, pytest-5.2.1, py-1.8.0, pluggy-0.13.0
    rootdir: /home/kbairak/devel/repos/pet_projects/svdict
    plugins: cov-2.8.1
    collected 6 items

    src/svdict/test_svdict.py ......                                     [100%]

    ----------- coverage: platform linux, python 3.7.6-final-0 -----------
    Name                        Stmts   Miss  Cover
    -----------------------------------------------
    src/svdict/__init__.py          1      0   100%
    src/svdict/svdict.py           81      0   100%
    src/svdict/test_svdict.py     150      0   100%
    src/svdict/validators.py       11      0   100%
    -----------------------------------------------
    TOTAL                         243      0   100%


    ============================ 6 passed in 0.19s ============================
