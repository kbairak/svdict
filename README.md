Self-validating dictionaries using [jsonschema](https://json-schema.org/).

To get started with jsonschema, read [here](https://json-schema.org/understanding-json-schema/).

## Why?

Some time ago, me and my team were building an API for a Django application.
Because we wanted to decouple the ORM from the JSON representation the API
returned, we wanted to have an intermediate representation of the objects
returned by the ORM. So to fetch data from the database, the API would invoke a
service function that would use the ORM to fetch data, transform it into this
intermediate representation and return it. It would then be the job of the API
to convert the intermediate representation to the JSON value that would
actually be returned by the API.

The idea was that such service functions would be used by other places of the
codebase, for example the views that compile a context for a Django template or
a task that creates a report to be sent via email. These service functions
should have to bother with neither the intricacies of the Django ORM, nor the
representation served by the API.

At that point I suggested that these intermediate representations be pure
JSON-serializable python objects, in order to reduce complexity. My team
rightfully retorted that this would be unsafe and error-prone because it would
be too easy for representations to end up inconsistent with each other. For
example, one service function might use `None` as a falsy value where another
service function would expect `False`, or an `id` may appear sometimes as an
`int` and sometimes as a string, etc. So we would need a mechanism that would
validate these representations against a predefined format.

This library is an attempt to get the best of both worlds. It gives us the
ability to create objects that behave exactly like pure python objects, but
after every mutation run validations against a predefined format. To specify
the format, we use [jsonschema](https://json-schema.org/) because it is
well-established and was created for this purpose.


## Usage

Usage, define your subclass like this:

```python
class User(SVDict):
    SCHEMA = {'type': "object",
              'required': ["id", "username"],
              'additionalProperties': False,
              'properties': {'id': {'type': "number"},
                             'username': {'type': "string"}}}
```

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

```python
class Project(SVDict):
    SCHEMA = {'type': "object",
              'required': ["id", "slug", "owner"],
              'additionalProperties': False,
              'properties': {'id': {'type': "number"},
                             'slug': {'type': "string"},
                             'owner': {'oneOf': [{'type': "null"},
                                                 User.SCHEMA]}}}
```

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

```python
class UserList(SVList):
    SCHEMA = {'type': "array", 'items': User.SCHEMA}
```


## Caveats

Refrain from using anything other than pure-python dicts/lists as the contents
of your SVDicts/SVLists as they will be converted upon assignment. If you use
a custom mapping or sequence implementation, you will lose all custom
functionality.

```python
class Foo(SVDict):
    SCHEMA = {'type': "object",
              'properties': {'dict': {'type': "object"},
                             'list': {'type': "array"}}}
class MyDict(collections.UserDict):
    def do_something_special(self):
        print("Special!!!")
class MyList(collections.UserList):
    def do_something_special(self):
        print("Special!!!")
my_dict = MyDict()
my_list = MyList()
foo = Foo({'dict': my_dict, 'list': my_list})
```

```
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
```

This conversion happens in order to trigger validation when a contained object
gets mutated. Otherwise, a call like:

```python
foo['dict']['a'] = "b"
```

would get translated to:

```python
foo.__getitem__('dict').__setitem__('a', "b")
```

and svdict would have no access to the child's mutating method in order to
trigger validation.


## Installation

    ➜  pip install -e .

or

    ➜  pip install .

or

    ➜  python setup.py install

If you want to be able to validate against string [formats](https://json-schema.org/understanding-json-schema/reference/string.html#format)
(eg `{'type': "string", 'format': "date-time"}`), install `jsonschema` using
the `format` or `format_nongpl` setuptools extra:

    ➜  pip install jsonschema[format]


## Tests

You can run the tests with pytest:

    ➜  pytest --cov=src
    =========================== test session starts ===========================
    platform linux -- Python 3.7.6, pytest-5.2.1, py-1.8.0, pluggy-0.13.0
    rootdir: /home/svdict/svdict
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
