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
    'version': '0.0.2',
    'description': 'An experimental web framework for Python 3.6+.',
    'long_description': None,
    'author': 'Bogdan Popa',
    'author_email': 'bogdan@cleartype.io',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
