import pytest
from svdict import SVDict, SVList, ValidationError


class Simple(SVDict):
    SCHEMA = {'type': "object", 'properties': {'a': {'type': "string"}}}


def test_simple():
    Simple()
    Simple(a="b")
    Simple({'a': "b"})
    with pytest.raises(ValidationError):
        Simple({'a': 1})
    s = Simple({'a': "b"})
    s['c'] = "d"
    assert s == {'a': "b", 'c': "d"}
    with pytest.raises(ValidationError):
        s['a'] = 1
    assert s == {'a': "b", 'c': "d"}


class Nested(SVDict):
    SCHEMA = {'type': "object",
              'properties': {'a': {'type': "object",
                                   'properties': {'b': {'type': "number"}}}}}


def test_nested():
    n = Nested({'a': {'b': 3}})
    n['a']['b'] = 4
    assert n == {'a': {'b': 4}}
    with pytest.raises(ValidationError):
        n['a']['b'] = "4"
    assert n == {'a': {'b': 4}}


class NestedList(SVDict):
    SCHEMA = {'type': "object",
              'properties': {'a': {'type': "array",
                                   'items': {'type': "number"}}}}


def test_nested_list():
    n = NestedList({'a': [1]})
    n['a'].append(2)
    assert n == {'a': [1, 2]}
    with pytest.raises(ValidationError):
        n['a'].append('3')
    assert n == {'a': [1, 2]}


class Required(SVDict):
    SCHEMA = {'type': "object",
              'required': ['a'],
              'properties': {'a': {'type': "string"}}}


def test_dict_methods():
    # __setitem__
    r = Required({'a': "b"})
    r['c'] = "d"
    assert r == {'a': "b", 'c': "d"}
    with pytest.raises(ValidationError):
        r['a'] = 1
    assert r == {'a': "b", 'c': "d"}

    # __delitem__
    del r['c']
    assert r == {'a': "b"}
    with pytest.raises(ValidationError):
        del r['a']
    assert r == {'a': "b"}

    # pop
    r['c'] = "d"
    assert r.pop('c') == "d"
    assert r == {'a': "b"}
    with pytest.raises(ValidationError):
        r.pop('a')
    assert r == {'a': "b"}

    # popitem
    with pytest.raises(ValidationError):
        r.popitem()
    assert r == {'a': "b"}

    # clear
    with pytest.raises(ValidationError):
        r.clear()
    assert r == {'a': "b"}

    # update
    r.update({'c': "d"})
    assert r == {'a': "b", 'c': "d"}
    with pytest.raises(ValidationError):
        r.update({'a': 2})
    assert r == {'a': "b", 'c': "d"}

    # setdefault
    s = Simple()
    s.setdefault('a', "b")
    assert s == {'a': "b"}
    s.setdefault('a', 3)
    assert s == {'a': "b"}
    s = Simple()
    with pytest.raises(ValidationError):
        s.setdefault('a', 3)
    assert s == {}


class RequiredList(SVDict):
    SCHEMA = {'type': "object",
              'properties': {'a': {'type': "array",
                                   'minItems': 1,
                                   'items': {'type': "string"}}}}


def test_list_methods():
    r = RequiredList({'a': ["b"]})

    # append
    r['a'].append("c")
    with pytest.raises(ValidationError):
        r['a'].append(4)
    assert r == {'a': ["b", "c"]}
    del r['a'][1]

    # append-kwarg
    r['a'].append(item="c")
    assert r == {'a': ["b", "c"]}
    with pytest.raises(ValidationError):
        r['a'].append(item=4)
    assert r == {'a': ["b", "c"]}

    # __setitem__
    r['a'][1] = "d"
    with pytest.raises(ValidationError):
        r['a'][1] = 4
    assert r == {'a': ["b", "d"]}

    # __delitem__
    del r['a'][1]
    with pytest.raises(ValidationError):
        del r['a'][0]
    assert r == {'a': ["b"]}

    # insert
    r['a'].insert(0, "c")
    with pytest.raises(ValidationError):
        r['a'].insert(0, 5)
    assert r == {'a': ["c", "b"]}

    # insert-kwarg
    del r['a'][0]
    r['a'].insert(0, item="c")
    with pytest.raises(ValidationError):
        r['a'].insert(0, item=5)
    assert r == {'a': ["c", "b"]}

    # pop
    assert r['a'].pop() == "b"
    with pytest.raises(ValidationError):
        r['a'].pop()
    assert r == {'a': ["c"]}

    r['a'] = ["b", "c"]
    # remove
    r['a'].remove("c")
    with pytest.raises(ValidationError):
        r['a'].remove("b")
    assert r == {'a': ["b"]}

    # clear
    with pytest.raises(ValidationError):
        r['a'].clear()
    assert r == {'a': ["b"]}

    # extend
    r['a'].extend(["c"])
    with pytest.raises(ValidationError):
        r['a'].extend([4])
    assert r == {'a': ["b", "c"]}

    # extend-kwarg
    del r['a'][1]
    r['a'].extend(other=["c"])
    with pytest.raises(ValidationError):
        r['a'].extend(other=[4])
    assert r == {'a': ["b", "c"]}

    # __iadd__
    r['a'] += ["d"]
    with pytest.raises(ValidationError):
        r['a'] += [5]
    assert r == {'a': ["b", "c", "d"]}


class List(SVList):
    SCHEMA = {'type': "array", 'items': {'type': "number"}}


def test_SVList():
    List()
    List((1, 2))
    List([1, 2])
    List(range(3))
    with pytest.raises(ValidationError):
        List(['a', 'b'])
    ll = List([1, 2])
    ll.append(3)
    assert ll == [1, 2, 3]
    with pytest.raises(ValidationError):
        ll.append('4')
    assert ll == [1, 2, 3]
    ll[2] = 4
    assert ll == [1, 2, 4]
    with pytest.raises(ValidationError):
        ll[2] = '4'
    assert ll == [1, 2, 4]
