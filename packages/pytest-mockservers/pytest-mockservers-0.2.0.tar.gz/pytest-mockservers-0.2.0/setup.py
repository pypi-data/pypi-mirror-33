# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pytest_mockservers']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.0.0,<4.0.0', 'pytest-asyncio<1.0.0', 'pytest>=3.0.0,<4.0.0']

entry_points = \
{'pytest11': ['http_server = pytest_mockservers.http_server',
              'udp_server = pytest_mockservers.udp_server']}

setup_kwargs = {
    'name': 'pytest-mockservers',
    'version': '0.2.0',
    'description': 'A set of fixtures to test your requests to HTTP/UDP servers',
    'long_description': "# pytest-mockservers [![Build Status](https://travis-ci.org/Gr1N/pytest-mockservers.svg?branch=master)](https://travis-ci.org/Gr1N/pytest-mockservers) [![Updates](https://pyup.io/repos/github/Gr1N/pytest-mockservers/shield.svg)](https://pyup.io/repos/github/Gr1N/pytest-mockservers/) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\n`pytest-mockservers` package provides a set of fixtures which can help you to test your code in cases when you need to check that requests which you sent to HTTP/UDP server are really sent.\n\nAvailable fixtures:\n\n* `http_server`\n* `http_server_factory`\n* `unused_udp_port`\n* `unused_udp_port_factory`\n* `udp_server_factory`\n\n## Installation\n\n    $ pip install pytest-mockservers\n\n## Usage\n\nLook into `tests/*` to find real examples of `pytest-mockserver` fixtures usage.\n\n## Contributing\n\nTo work on the `pytest-mockservers` codebase, you'll want to clone the project locally and install the required dependencies via [poetry](https://poetry.eustace.io):\n\n    $ git clone git@github.com:Gr1N/pytest-mockservers.git\n    $ poetry install\n\nTo run tests and linters use command below:\n\n    $ poetry run tox\n\nIf you want to run only tests or linters you can explicitly specify which test environment you want to run, e.g.:\n\n    $ poetry run tox -e py37-tests\n\n## License\n\n`pytest-mockservers` is licensed under the MIT license. See the license file for details.\n",
    'author': 'Nikita Grishko',
    'author_email': 'gr1n@protonmail.com',
    'url': 'https://github.com/Gr1N/pytest-mockservers',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
