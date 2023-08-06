# -*- coding: utf-8 -*-

from collections import OrderedDict
import json
import os
import sys
import pytest

from items import *


_PY2 = sys.version_info < (3, 0)
_PY36 = sys.version_info >= (3, 6)


def test_empty():
    it = Item()
    assert list(it.keys()) == []
    assert list(it.values()) == []
    assert list(it.items()) == []
    assert isinstance(it, dict)
    assert isinstance(it, OrderedDict)


def test_simple():
    it = Item(a=1, c=22, b=99, r=4.4, d='this')
    keys = 'a c b r d'.split()
    values =  [1, 22, 99, 4.4, 'this']
    if _PY36:
        assert list(it.keys()) == keys
    else:
        assert set(it.keys()) == set(keys)
    if _PY36:
        assert list(it.values()) == values
    else:
        assert set(it.values()) == set(values)
    assert isinstance(it, dict)
    assert isinstance(it, OrderedDict)


def test_from_dict():
    d = {'this': 99, 'that': 'friends'}
    it = Item(d)
    assert it.this == d['this']
    assert it['this'] == d['this']
    assert it.that == d['that']
    assert it['that'] == d['that']


def test_missing():
    it = Item(a=1, b=2)
    assert it.c is Empty
    assert it['c'] is Empty

def test_repr():
    it = Item(a=1, b=2, c='something')
    if _PY36:
        assert repr(it) == "Item(a=1, b=2, c='something')"
    else:
        r = repr(it)
        assert r.startswith('Item(')
        assert r.endswith(')')
        assert 'a=1' in r
        assert 'b=2' in r
        assert "c='something'" in r


def test_Empty():
    e = Empty
    assert e.more.f.d is Empty
    assert e[1].method().there[33][0].no.attributes[99].here is Empty

    assert list(Empty) == []
    for x in Empty:
        assert False   # should/must never execute


def test_from_tuples():
    it = Item([('name', 'Susie'),
               ('age', 12),
               ('hobby', 'science'),
               ('friends', ['Dell', 'Bill'])])
    assert it.name == 'Susie'
    assert it.age == 12
    assert it.hobby == 'science'
    assert it.friends == ['Dell', 'Bill']
    assert len(it) == 4


    with pytest.raises(ValueError):
        it2 = Item([('name', 'Susie'),
                    ('age', 12, 33),        # unbalanced
                    ('hobby', 'science'),
                    ('friends', ['Dell', 'Bill'])])
        Item(it2)


def test_attr_assign():
    it = Item()
    it.a = 12
    it.b = 44
    assert it.a == 12
    assert it.b == 44
    assert it['a'] == 12
    assert it['b'] == 44
    assert list(it.keys()) == ['a', 'b']
    assert list(it.values()) == [12, 44]


def test_attr_del():
    it = Item(a=12, b=44)
    del it.b
    assert it.a == 12
    assert it.b == Empty
    assert len(it) == 1
    del it.a
    assert it.a == Empty
    assert len(it) == 0
    del it.a
    assert len(it) == 0


def test_itemize():
    things = [ {'a': 1}, {'a': 7} ]
    for t in itemize(things):
        assert isinstance(t, Item)
        assert t.a == 1 or t.a == 7


def test_itemize_all():
    things = [ {'a': 1}, {'a': 7} ]
    t_all = itemize_all(things)
    assert isinstance(t_all, list)
    assert len(t_all) == 2
    assert t_all[0].a == 1
    assert t_all[1].a == 7
    assert t_all[1].other is Empty


def test_composite_1():
    """
    Read a JSON file, and ensure it has the same structure as Items as it
    does in a native, non-attribute-accessible structure using OrderedDict
    """
    datadir, _ = os.path.split(__file__)
    datapath = os.path.join(datadir, 'testdata', 'data1.json')
    with open(datapath) as f:
        rawjson = f.read()
        data_i = json.loads(rawjson, object_pairs_hook=Item)
        data_o = json.loads(rawjson, object_pairs_hook=OrderedDict)
    for x, y in zip(data_i, data_o):
        assert list(x.keys()) == list(y.keys())
        assert list(x.values()) == list(y.values())


