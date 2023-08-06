
| |travisci| |version| |versions| |impls| |wheel| |coverage|

.. |travisci| image:: https://travis-ci.org/jonathaneunice/items.svg?branch=master
    :alt: Travis CI build status
    :target: https://travis-ci.org/jonathaneunice/items

.. |version| image:: http://img.shields.io/pypi/v/items.svg?style=flat
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/items

.. |versions| image:: https://img.shields.io/pypi/pyversions/items.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/items

.. |impls| image:: https://img.shields.io/pypi/implementation/items.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/items

.. |wheel| image:: https://img.shields.io/pypi/wheel/items.svg
    :alt: Wheel packaging support
    :target: https://pypi.python.org/pypi/items

.. |coverage| image:: https://img.shields.io/badge/test_coverage-100%25-6600CC.svg
    :alt: Test line coverage
    :target: https://pypi.python.org/pypi/items

Attribute-accessible dictonaries are the most convenient way to access
dictionaries and other mappings in many algorithms. ``item.name`` is more
readable and concise than ``item['name']``. Having attribute access often is
the difference between being able to easily de-reference a component of
``item`` directly and deciding to store that attribute in a completely
separate variable for clarity (``item_name = item['name']``).

In traversing data structures from XML, JSON, and other typically-nested data
sources, concise direct access can clean up code considerably.

Items
-----

``items`` therefore provides ``Item``, a convenient attribute-accessible ``dict`` subclass,
plus helper functions to make working with ``Item`` s.

``itemize``, for example, helps iterate of a list of dictionaries, as often found
in JSON processing: Each record is handed back as an ``Item`` rather than a Python
``dict``.

A typical progression would be from:

.. code-block:: python

    for item in data:
        item_name = item['name']
        # ...
        print(item_name)

to

.. code-block:: python

    from items import itemize

    for item in itemize(data):
        # ...
        print(item.name)

To process a list wholesale:

.. code-block:: python

    from items import itemize_all

    itemize_all(data)

``Item`` objects are subclasses of ``collections.OrderedDict``, so that keys
are ordered the same as when yoor program first encountered them. The
performance or ordered mappings is minimal in most development contexts,
especially in exploratory and data-cleanup tasks. Whatever overhead there is is
more than made up for by the programming and debugging clarity of not having
keys occur in random locations.

``Item`` s are also permissive, in a way that ``dict`` and its variants often
are not: If you access ``item.arbitary_attribute`` where the attribute does not
exist, you do not raise a ``KeyError`` as you might expect from normal Python
dictionaries. Instead you get back ``Empty``, a designated, false-y value
similar to, but distinct from, ``None``. This is convenient for processing data
which is not irregular and not uniformly filled-in, because you do not need the
constant "gaurd conditions"--either ``if`` statements or ``try``/``except
KeyError`` blocks--to protect against cases where this data value or that is
missing. Using ``Empty`` instead of ``None`` preserves your ability to use
``None`` in cases where it's semanticailly important. For example, in parsing
JSON, ``None`` is returned from JSON's ``null`` value.

``Empty`` objects are infinitely dereferenceable. No matter how many levels of
indirection, they always just hand back themselves--the same gentle "nothing
here, but no exceptions raised" behavior. You can also iterate over an
``Empty``--it will simply iterate zero times. This neatly avoids the common
``TypeError: 'NoneType' object is not iterable`` error messages in instances
where a value can be a list--or ``None`` if the list is not present.

.. code-block:: python

    e = Empty
    assert e[1].method().there[33][0].no.attributes[99].here is Empty
    for x in Empty:
        print('hey!')     # never prints, because no such iterations occur

For more on the background of ``Empty``, see the `nulltype <https://pypi.org/project/nulltype/>`_
module. A typical use would be:

.. code-block:: python

    for item in itemize(data):
        if item.name:
            process(item)

Items that lack names are simply not processed.

The more nested, complex, and irregular your data structures, the
more valueable this becomes.

Serialization and Deserialization
=================================

Be careful importing data from files. Popular Python modules for reading JSON,
YAML, and other formats do not believe mappings are ordered. Historically and
officially, they're not, no matter how ordered they look, no matter that other
languages such as JavaScript take a different approach, and no matter how many
Stack Overflow questions demonstrate that ordered import is stronly and broadly
desired. Therefore stock input/output modules can cause dislocation as data is
parsed. Take steps to return ordered mappings from them.

.. code-block:: python

    # YAML module that will load into OrderedDict instances, which can then
    # be easily converted to Item instances; based on default PyYAML
    import oyaml as yaml
    data = itemize_all(yaml.load(rawyaml))

    # modified call to json.load or json.loads to preserve order by instantiating
    # Item instances rather than dict
    import json
    data = json.loads(rawjson, object_pairs_hook=Item)

Cycles
======

Not currently organized for handling cyclic data structures. Those do not
appear in processing JSON, XML, and other common data formats, but still might
be a nice future extension.

Installation
============

To install or upgrade to the latest version::

    pip install -U items

Sometimes Python installations have different names for ``pip`` (e.g. ``pip``,
``pip2``, and ``pip3``), and on systems with multiple versions of Python, which
``pip`` goes with which Python interpreter can become confusing. In those
cases, try running ``pip`` as a module of the Python version you want to
install under. This can reduce conflects and confusion::

    python3.6 -m pip install -U items

(On Unix, Linux, and macOS you may need to prefix these with ``sudo`` to authorize
installation. In environments without super-user privileges, you may want to
use ``pip``'s ``--user`` option, to install only for a single user, rather
than system-wide.)

Testing
=======

If you wish to run the module tests locally, you'll need to install
``pytest`` and ``tox``.  For full testing, you will also need ``pytest-cov``
and ``coverage``. Then run one of these commands::

    tox                # normal run - speed optimized
    tox -e py27        # run for a specific version only (e.g. py27, py34)
    tox -c toxcov.ini  # run full coverage tests

