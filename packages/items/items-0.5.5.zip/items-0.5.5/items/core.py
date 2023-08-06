import sys
from collections import OrderedDict
from nulltype import Empty

__all__ = 'Empty Item itemize itemize_all'.split()

_PY2 = sys.version_info[0] == 2


def _item(data):
    """
    Private factory function for Item values, especially second and subsequent
    levels beneath the top-level mapping. Here because recursive initializers
    in Python aren't really feasible, since some recursions would yield lists
    or other data types, rather than Item instances.
    """
    # data is-a mapping / dict => return an Item instead
    if hasattr(data, 'items'):
        it = Item()
        for k, v in data.items():
            it[k] = _item(v)
        return it

    # data is-a list or tuple => return exactly that type
    if isinstance(data, (list, tuple)):
        return type(data)(_item(x) for x in data)

    # otherwise, data type is "simple" with respect to Item creation,
    # be it int, float, complex, str, bytes, or some other type
    return data


class Item(OrderedDict):

    "Ordered, attribute-accessible dictionary/mapping class."

    def __init__(self, a_dict=None, **kwargs):
        super(Item, self).__init__()
        if a_dict:
            items = a_dict if isinstance(a_dict, list) else a_dict.items()
            for k, v in items:
                self[k] = _item(v)
        if kwargs:
            self.update(_item(kwargs))

    def __getattr__(self, name):
        try:
            return super(Item, self).__getitem__(name)
        except KeyError:
            return Empty

    def __setattr__(self, name, value):
        """
        Setting attrs becomes equivalent to setting items.
        """
        self[name] = value

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            # pass on KeyError for same reason __getattr__ returns Empty if not there:
            # to be permissive in case of missing attributes / keys
            pass

    def __getitem__(self, key):
        try:
            return super(Item, self).__getitem__(key)
        except KeyError:
            return Empty
            # NB explicit action instead of object.__missing__(self, key) method

    def __repr__(self):
        clsname = self.__class__.__name__
        kwstr = ', '.join('{0}={1!r}'.format(k, v) for k, v in self.items())
        return '{0}({1})'.format(clsname, kwstr)

    # depends on OrderedDict for __delitem__, __setitem__


def itemize(iterator):
    """
    Given a collection of dict-like records, create and
    return an Item out of each record.
    """
    for item in iterator:
        yield Item(item)


def itemize_all(iterator):
    """
    Given a collection of dict-like records, create and
    return an list of Item objects comprising all the records.
    """
    return list(itemize(iterator))
