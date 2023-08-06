# pyfrozen [![Build Status](https://travis-ci.org/Gr1N/pyfrozen.svg?branch=master)](https://travis-ci.org/Gr1N/pyfrozen) [![codecov](https://codecov.io/gh/Gr1N/pyfrozen/branch/master/graph/badge.svg)](https://codecov.io/gh/Gr1N/pyfrozen) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Set of collections with ability to freeze their items.

## Installation

    $ pip install pyfrozen

## Usage

    >>> from pyfrozen import FrozenDict, FrozenList
    >>>
    >>> fd = FrozenDict()
    >>> fd['key_1'] = 'value_1'
    >>> fd
    <FrozenDict(frozen=False, {'key_1': 'value_1'})>
    >>> fd.freeze()
    >>> fd
    <FrozenDict(frozen=True, {'key_1': 'value_1'})>
    >>> fd['key_1'] = 'value_2'
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "/pyfrozen/pyfrozen/frozendict.py", line 23, in __setitem__
        self.assert_frozen()
    File "/pyfrozen/pyfrozen/frozendict.py", line 45, in assert_frozen
        raise RuntimeError('Cannot modify frozen dict')
    RuntimeError: Cannot modify frozen dict
    >>> fd
    <FrozenDict(frozen=True, {'key_1': 'value_1'})>
    >>>
    >>> fl = FrozenList()
    >>> fl.extend(['value_1', 'value_2'])
    >>> fl
    <FrozenList(frozen=False, ['value_1', 'value_2'])>
    >>> fl.freeze()
    >>> fl.pop()
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "/lib/python3.6/_collections_abc.py", line 997, in pop
        del self[index]
    File "/pyfrozen/pyfrozen/frozenlist.py", line 29, in __delitem__
        self.assert_frozen()
    File "/pyfrozen/pyfrozen/frozenlist.py", line 56, in assert_frozen
        raise RuntimeError('Cannot modify frozen list')
    RuntimeError: Cannot modify frozen list
    >>> fl
    <FrozenList(frozen=True, ['value_1', 'value_2'])>
    >>>

## Contributing

To work on the `pyfrozen` codebase, you'll want to clone the project locally and install the required dependencies via [poetry](https://poetry.eustace.io):

    $ git clone git@github.com:Gr1N/pyfrozen.git
    $ poetry install

To run tests and linters use command below:

    $ poetry run tox

If you want to run only tests or linters you can explicitly specify which test environment you want to run, e.g.:

    $ poetry run tox -e py37-tests

## TODO

- [ ] Implement all collections using [Cython](http://cython.org)

## License

`pyfrozen` is licensed under the MIT license. See the license file for details.
