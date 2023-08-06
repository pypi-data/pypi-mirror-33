# jsonpointer-helpers [![Build Status](https://travis-ci.org/Gr1N/jsonpointer-helpers.svg?branch=master)](https://travis-ci.org/Gr1N/jsonpointer-helpers) [![codecov](https://codecov.io/gh/Gr1N/jsonpointer-helpers/branch/master/graph/badge.svg)](https://codecov.io/gh/Gr1N/jsonpointer-helpers) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Helpers for JSON pointers described by [RFC 6901](https://tools.ietf.org/html/rfc6901).

## Installation

    $ pip install jsonpointer-helpers

## Usage

    >>> import jsonpointer_helpers as jp
    >>>
    >>> jp.build({'foo': {'bar': 42}})
    {'/foo/bar': 42}
    >>>
    >>> jp.build_pointer(['foo', 'bar'])
    '/foo/bar'
    >>>
    >>> jp.parse_pointer('/foo/bar')
    ['foo', 'bar']
    >>>
    >>> jp.escape_token('foo~bar')
    'foo~0bar'
    >>>
    >>> jp.unescape_token('foo~0bar')
    'foo~bar'
    >>>

## Testing and linting

## Contributing

To work on the `jsonpointer-helpers` codebase, you'll want to clone the project locally and install the required dependencies via [poetry](https://poetry.eustace.io):

    $ git clone git@github.com:Gr1N/jsonpointer-helpers.git
    $ poetry install

To run tests and linters use command below:

    $ poetry run tox

If you want to run only tests or linters you can explicitly specify which test environment you want to run, e.g.:

    $ poetry run tox -e py37-tests

## License

`jsonpointer-helpers` is licensed under the MIT license. See the license file for details.
