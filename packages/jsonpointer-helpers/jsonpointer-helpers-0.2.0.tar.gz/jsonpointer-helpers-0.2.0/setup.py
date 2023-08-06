# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['jsonpointer_helpers']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'jsonpointer-helpers',
    'version': '0.2.0',
    'description': 'JSON Pointer helpers',
    'long_description': "# jsonpointer-helpers [![Build Status](https://travis-ci.org/Gr1N/jsonpointer-helpers.svg?branch=master)](https://travis-ci.org/Gr1N/jsonpointer-helpers) [![codecov](https://codecov.io/gh/Gr1N/jsonpointer-helpers/branch/master/graph/badge.svg)](https://codecov.io/gh/Gr1N/jsonpointer-helpers) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\nHelpers for JSON pointers described by [RFC 6901](https://tools.ietf.org/html/rfc6901).\n\n## Installation\n\n    $ pip install jsonpointer-helpers\n\n## Usage\n\n    >>> import jsonpointer_helpers as jp\n    >>>\n    >>> jp.build({'foo': {'bar': 42}})\n    {'/foo/bar': 42}\n    >>>\n    >>> jp.build_pointer(['foo', 'bar'])\n    '/foo/bar'\n    >>>\n    >>> jp.parse_pointer('/foo/bar')\n    ['foo', 'bar']\n    >>>\n    >>> jp.escape_token('foo~bar')\n    'foo~0bar'\n    >>>\n    >>> jp.unescape_token('foo~0bar')\n    'foo~bar'\n    >>>\n\n## Testing and linting\n\n## Contributing\n\nTo work on the `jsonpointer-helpers` codebase, you'll want to clone the project locally and install the required dependencies via [poetry](https://poetry.eustace.io):\n\n    $ git clone git@github.com:Gr1N/jsonpointer-helpers.git\n    $ poetry install\n\nTo run tests and linters use command below:\n\n    $ poetry run tox\n\nIf you want to run only tests or linters you can explicitly specify which test environment you want to run, e.g.:\n\n    $ poetry run tox -e py37-tests\n\n## License\n\n`jsonpointer-helpers` is licensed under the MIT license. See the license file for details.\n",
    'author': 'Nikita Grishko',
    'author_email': 'gr1n@protonmail.com',
    'url': 'https://github.com/Gr1N/jsonpointer-helpers',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
