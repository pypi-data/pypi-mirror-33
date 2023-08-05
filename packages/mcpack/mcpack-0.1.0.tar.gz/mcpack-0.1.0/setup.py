# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['mcpack']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'mcpack',
    'version': '0.1.0',
    'description': 'A python library for programmatically creating and editing minecraft datapacks',
    'long_description': '# mcpack\n\n> A python library for programmatically creating and editing minecraft datapacks. Requires python 3.6.\n',
    'author': 'Valentin Berlier',
    'author_email': 'berlier.v@gmail.com',
    'url': 'https://github.com/vberlier/mcpack',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
