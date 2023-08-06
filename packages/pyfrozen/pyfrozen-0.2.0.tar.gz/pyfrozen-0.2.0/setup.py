# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pyfrozen']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pyfrozen',
    'version': '0.2.0',
    'description': 'Set of collections with ability to freeze their items',
    'long_description': '# pyfrozen [![Build Status](https://travis-ci.org/Gr1N/pyfrozen.svg?branch=master)](https://travis-ci.org/Gr1N/pyfrozen) [![codecov](https://codecov.io/gh/Gr1N/pyfrozen/branch/master/graph/badge.svg)](https://codecov.io/gh/Gr1N/pyfrozen) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\nSet of collections with ability to freeze their items.\n\n## Installation\n\n    $ pip install pyfrozen\n\n## Usage\n\n    >>> from pyfrozen import FrozenDict, FrozenList\n    >>>\n    >>> fd = FrozenDict()\n    >>> fd[\'key_1\'] = \'value_1\'\n    >>> fd\n    <FrozenDict(frozen=False, {\'key_1\': \'value_1\'})>\n    >>> fd.freeze()\n    >>> fd\n    <FrozenDict(frozen=True, {\'key_1\': \'value_1\'})>\n    >>> fd[\'key_1\'] = \'value_2\'\n    Traceback (most recent call last):\n    File "<stdin>", line 1, in <module>\n    File "/pyfrozen/pyfrozen/frozendict.py", line 23, in __setitem__\n        self.assert_frozen()\n    File "/pyfrozen/pyfrozen/frozendict.py", line 45, in assert_frozen\n        raise RuntimeError(\'Cannot modify frozen dict\')\n    RuntimeError: Cannot modify frozen dict\n    >>> fd\n    <FrozenDict(frozen=True, {\'key_1\': \'value_1\'})>\n    >>>\n    >>> fl = FrozenList()\n    >>> fl.extend([\'value_1\', \'value_2\'])\n    >>> fl\n    <FrozenList(frozen=False, [\'value_1\', \'value_2\'])>\n    >>> fl.freeze()\n    >>> fl.pop()\n    Traceback (most recent call last):\n    File "<stdin>", line 1, in <module>\n    File "/lib/python3.6/_collections_abc.py", line 997, in pop\n        del self[index]\n    File "/pyfrozen/pyfrozen/frozenlist.py", line 29, in __delitem__\n        self.assert_frozen()\n    File "/pyfrozen/pyfrozen/frozenlist.py", line 56, in assert_frozen\n        raise RuntimeError(\'Cannot modify frozen list\')\n    RuntimeError: Cannot modify frozen list\n    >>> fl\n    <FrozenList(frozen=True, [\'value_1\', \'value_2\'])>\n    >>>\n\n## Contributing\n\nTo work on the `pyfrozen` codebase, you\'ll want to clone the project locally and install the required dependencies via [poetry](https://poetry.eustace.io):\n\n    $ git clone git@github.com:Gr1N/pyfrozen.git\n    $ poetry install\n\nTo run tests and linters use command below:\n\n    $ poetry run tox\n\nIf you want to run only tests or linters you can explicitly specify which test environment you want to run, e.g.:\n\n    $ poetry run tox -e py37-tests\n\n## TODO\n\n- [ ] Implement all collections using [Cython](http://cython.org)\n\n## License\n\n`pyfrozen` is licensed under the MIT license. See the license file for details.\n',
    'author': 'Nikita Grishko',
    'author_email': 'gr1n@protonmail.com',
    'url': 'https://github.com/Gr1N/pyfrozen',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
