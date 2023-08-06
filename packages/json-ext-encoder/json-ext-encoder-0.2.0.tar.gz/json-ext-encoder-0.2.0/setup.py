# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['json_ext_encoder']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'json-ext-encoder',
    'version': '0.2.0',
    'description': 'Extended JSON encoder for Python data structures',
    'long_description': "# json-ext-encoder [![Build Status](https://travis-ci.org/Gr1N/json-ext-encoder.svg?branch=master)](https://travis-ci.org/Gr1N/json-ext-encoder) [![codecov](https://codecov.io/gh/Gr1N/json-ext-encoder/branch/master/graph/badge.svg)](https://codecov.io/gh/Gr1N/json-ext-encoder) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\nExtended JSON encoder for Python data structures.\n\nA subclass of [JSONEncoder](https://docs.python.org/3/library/json.html#json.JSONEncoder), it handles these additional types:\n\n- `datetime.datetime` — a string of the form `YYYY-MM-DDTHH:mm:ss.sssZ` or `YYYY-MM-DDTHH:mm:ss.sss+HH:MM` as defined in [ECMA-262](https://www.ecma-international.org/ecma-262/5.1/#sec-15.9.1.15).\n- `datetime.date` — a string of the form `YYYY-MM-DD` as defined in [ECMA-262](https://www.ecma-international.org/ecma-262/5.1/#sec-15.9.1.15).\n- `datetime.time` — a string of the form `HH:MM:ss.sss` as defined in [ECMA-262](https://www.ecma-international.org/ecma-262/5.1/#sec-15.9.1.15).\n- `datetime.timedelta` - a string representing a duration as defined in [ISO-8601](https://www.iso.org/iso-8601-date-and-time-format.html). For example, `timedelta(days=1, hours=2, seconds=3.4)` is represented as `P1DT02H00M03.400000S`.\n- `decimal.Decimal`, `uuid.UUID` — a string representation of the object.\n- `enum.Enum` — a `.value` property of enum member.\n\n## Installation\n\n    $ pip install json-ext-encoder\n\n## Usage\n\n    import json\n    from json_ext_encoder import JSONEncoder\n\n    json.dumps({...}, cls=JSONEncoder)\n\n## Contributing\n\nTo work on the `json-ext-encoder` codebase, you'll want to clone the project locally and install the required dependencies via [poetry](https://poetry.eustace.io):\n\n    $ git clone git@github.com:Gr1N/json-ext-encoder.git\n    $ poetry install\n\nTo run tests and linters use command below:\n\n    $ poetry run tox\n\nIf you want to run only tests or linters you can explicitly specify which test environment you want to run, e.g.:\n\n    $ poetry run tox -e py37-tests\n\n## License\n\n`json-ext-encoder` is licensed under the MIT license. See the license file for details.\n",
    'author': 'Nikita Grishko',
    'author_email': 'gr1n@protonmail.com',
    'url': 'https://github.com/Gr1N/json-ext-encoder',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
