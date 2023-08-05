from cytoolz import first
from cytoolz import second
from merlin import cfg
from merlin import functions as f
import numpy as np
import pytest
import test


def test_extract():
    inputs = [1, (2, 3, (4, 5)), 6]
    assert f.extract(inputs, [0]) == 1
    assert f.extract(inputs, [1]) == (2, 3, (4, 5))
    assert f.extract(inputs, [1, 0]) == 2
    assert f.extract(inputs, [1, 1]) == 3
    assert f.extract(inputs, [1, 2]) == (4, 5)
    assert f.extract(inputs, [1, 2, 0]) == 4


def test_flatten():
    result = [1, 2, 3, 4, 5, [6, 7]]
    assert list(f.flatten([[1, 2], [3, 4], [5, [6, 7]]])) == result


def test_intersection():
    items = [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
    assert f.intersection(items) == {3}


def test_sha256():
    assert type(f.sha256('kowalski')) is str


def test_md5():
    assert type(f.md5('kowalski')) is str


def test_sort():
    assert f.sort([2, 1, 3]) == [1, 2, 3]


def test_rsort():
    assert f.rsort([2, 1, 3]) == [3, 2, 1]


def test_serialization():

    def serialize_deserialize(t):
        assert f.deserialize(second(f.serialize(t))) == t

    targets = ['farva', 1, 2.0, True, None]

    all(map(serialize_deserialize, targets))


def test_flip_keys():
    dods = {'a': {1: 'a1', 2: 'a2'},
            'b': {1: 'b1', 2: 'b2'},
            'c': {1: 'c1', 2: 'c2'}}

    result = {1: {'a': 'a1', 'b': 'b1', 'c': 'c1'},
              2: {'a': 'a2', 'b': 'b2', 'c': 'c2'}}

    assert f.flip_keys(dods) == result


def test_cqlstr():
    assert f.cqlstr('-:.') == '___'


def test_represent():

    def ramrod():
        pass

    assert f.represent(ramrod) == "'ramrod'"
    assert f.represent('ramrod') == "'ramrod'"
    assert f.represent(1) == '1'
    assert f.represent(None) == 'None'


def test_isnumeric():
    good = ['1', '-1', '0', '1.0', '-1.0']
    assert all(map(f.isnumeric, good))

    bad = ['a', 'a1', '1a']
    assert not any(map(f.isnumeric, bad))


def test_seqeq():
    assert f.seqeq([1, 2, 3], [2, 3, 1]) is True
    assert f.seqeq({1, 2, 3}, [2, 3, 1]) is True
    assert f.seqeq(tuple([3, 2, 1]), [1, 2, 3]) is True
    assert f.seqeq([1,], [1, 2, 3]) is False
    assert f.seqeq([1, 2, 3], [1,]) is False


def test_issubset():
    assert f.issubset([1, 2], [3, 1, 2]) is True
    assert f.issubset(tuple([2, 1]), [3, 2, 1]) is True
    assert f.issubset({'a': 1, 'b': 2}, {'a': 1, 'c': 3, 'b': 2}) is True
    assert f.issubset([3, 2, 1], [3, 2]) is False


def test_difference():
    a = [1, 2, 3]
    b = [1, 2]
    assert f.difference(a, b) == {3}
    assert f.difference(b, a) == set()


def test_chexists():

    # simple check function that will return the first list
    def check_fn(dictionary):
        return dictionary[first(dictionary)]

    # simulate assymetric list values, telling chexists 'c' is supposed to be
    # bigger.
    d = {'a': [1, 2, 3], 'b': [1, 2, 3], 'c': [1, 2, 3, 4, 5]}
    assert f.chexists(d, ['c'], check_fn) == d['a']

    # make sure we throw an exception if c does not contain all values from
    # check_fn
    with pytest.raises(Exception):
        d = {'a': [1, 2, 3], 'b': [1, 2, 3], 'c': [1, 2, 4, 5]}
        assert f.chexists(d, ['c'], check_fn) == d['a']


def test_insert_into_every():
    dod = {1: {1: 'one'},
           2: {1: 'one'}}

    result = f.insert_into_every(dod, key='newkey', value='newval')

    #assert all(['newkey' in dod.get(key) for key in dod.keys()])
    assert all([dod.get(key).get('newkey') is 'newval' for key in dod.keys()])


def test_denumpify():
    bools = [np.bool_, np.bool8, bool]
    
    ints = [np.intc, np.intp, np.int8, np.int16, np.int32, np.int64,
            np.uint8, np.uint16, np.uint32, np.uint64, int]

    floats = [np.float64, np.float32, np.float16, float]

    complexes = [np.complex_, np.complex64, np.complex128, complex]

    assert all([type(f.denumpify(_b(10))) == bool for _b in bools])
    assert all([type(f.denumpify(_i(10))) == int for _i in ints])
    assert all([type(f.denumpify(_f(10))) == float for _f in floats])
    assert all([type(f.denumpify(_c(10))) == complex for _c in complexes])
    assert type(f.denumpify(np.ndarray([1, 2, 3])) == list)

    assert f.denumpify(None) is None
    assert type(f.denumpify(set([1, 2, 3]))) == set
    assert type(f.denumpify([1, 2, 3])) == list
    assert type(f.denumpify(dict(a=1))) == dict
    assert type(f.denumpify(tuple([1, 2, 3]))) == tuple

    # make sure it's converting subelement correctly
    l = f.denumpify([np.int16(1), np.int16(20), np.int16(3)])
    assert all([type(ll) == int for ll in l])                    
