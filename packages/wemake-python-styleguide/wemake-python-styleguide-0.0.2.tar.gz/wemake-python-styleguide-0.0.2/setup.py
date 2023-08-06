# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['wemake_python_styleguide',
 'wemake_python_styleguide.helpers',
 'wemake_python_styleguide.visitors',
 'wemake_python_styleguide.visitors.base']

package_data = \
{'': ['*']}

install_requires = \
['flake8>=3.5,<4.0']

entry_points = \
{'flake8.extension': ['WPS = wemake_python_styleguide.checker:Checker']}

setup_kwargs = {
    'name': 'wemake-python-styleguide',
    'version': '0.0.2',
    'description': 'Opinionated styleguide that we use in wemake.services',
    'long_description': "# wemake-python-styleguide\n\n[![wemake.services](https://img.shields.io/badge/style-wemake.services-green.svg?label=&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC%2FxhBQAAAAFzUkdCAK7OHOkAAAAbUExURQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP%2F%2F%2F5TvxDIAAAAIdFJOUwAjRA8xXANAL%2Bv0SAAAADNJREFUGNNjYCAIOJjRBdBFWMkVQeGzcHAwksJnAPPZGOGAASzPzAEHEGVsLExQwE7YswCb7AFZSF3bbAAAAABJRU5ErkJggg%3D%3D)](http://wemake.services)\n[![Build Status](https://travis-ci.org/wemake-services/wemake-python-styleguide.svg?branch=master)](https://travis-ci.org/wemake-services/wemake-python-styleguide)\n[![Coverage](https://coveralls.io/repos/github/wemake-services/wemake-python-styleguide/badge.svg?branch=master)](https://coveralls.io/github/wemake-services/wemake-python-styleguide?branch=master)\n[![PyPI version](https://badge.fury.io/py/wemake-python-styleguide.svg)](https://badge.fury.io/py/wemake-python-styleguide)\n[![Documentation Status](https://readthedocs.org/projects/wemake-python-styleguide/badge/?version=latest)](https://wemake-python-styleguide.readthedocs.io/en/latest/?badge=latest)\n\n\nWelcome to the most opinionated linter ever.\n\n\n## Installation\n\n```bash\npip install wemake-python-styleguide\n```\n\n## Project status\n\nWe are in early alpha.\nUse it on your own risk.\n\n\n## Running tests\n\nClone the repository, install `poetry`, then do from within the project folder:\n\n```bash\n# Installing dependencies (only required to be run once):\npoetry install\npoetry develop\n\n# Running tests:\npoetry run pytest\npoetry run mypy wemake_python_styleguide\npoetry run doc8 -q docs\n```\n\nIt's OK if some tests are skipped.\n",
    'author': 'Nikita Sobolev',
    'author_email': 'mail@sobolevn.me',
    'url': 'https://github.com/wemake-services/wemake-python-styleguide',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
