# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['molten', 'molten.http', 'molten.testing', 'molten.validation']

package_data = \
{'': ['*'], 'molten': ['contrib/*']}

install_requires = \
['typing-extensions>=3.6,<4.0']

setup_kwargs = {
    'name': 'molten',
    'version': '0.1.0',
    'description': 'An experimental web framework for Python 3.6+.',
    'long_description': "# molten\n\n[![Build Status](https://travis-ci.org/Bogdanp/molten.svg?branch=master)](https://travis-ci.org/Bogdanp/molten)\n[![Maintainability](https://api.codeclimate.com/v1/badges/f7ab5fdd188fda33c3e1/maintainability)](https://codeclimate.com/github/Bogdanp/molten/maintainability)\n[![Test Coverage](https://api.codeclimate.com/v1/badges/f7ab5fdd188fda33c3e1/test_coverage)](https://codeclimate.com/github/Bogdanp/molten/test_coverage)\n[![PyPI version](https://badge.fury.io/py/molten.svg)](https://badge.fury.io/py/molten)\n[![Documentation](https://img.shields.io/badge/doc-latest-brightgreen.svg)](https://moltenframework.com)\n\n**molten** is an experimental web framework for Python 3.6+.  It's\nmeant to be minimal, extensible, fast and productive.  Check out the\n[examples] for a taste or start reading the [user guide]!\n\n\n## Installation\n\n    pip install molten\n\n\n## License\n\nmolten is licensed under the LGPL.  Please see [COPYING] and\n[COPYING.LESSER] for licensing details.\n\n[COPYING.LESSER]: https://github.com/Bogdanp/molten/blob/master/COPYING.LESSER\n[COPYING]: https://github.com/Bogdanp/molten/blob/master/COPYING\n[examples]: https://github.com/Bogdanp/molten/blob/master/examples\n[user guide]: https://moltenframework.com/guide.html\n",
    'author': 'Bogdan Popa',
    'author_email': 'bogdan@cleartype.io',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
