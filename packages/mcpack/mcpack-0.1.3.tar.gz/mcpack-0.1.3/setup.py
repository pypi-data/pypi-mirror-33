# -*- coding: utf-8 -*-
from distutils.core import setup

install_requires = \
['nbtlib>=1.0,<2.0']

setup_kwargs = {
    'name': 'mcpack',
    'version': '0.1.3',
    'description': 'A python library for programmatically creating and editing Minecraft data packs',
    'long_description': '# mcpack\n\n[![PyPI](https://img.shields.io/pypi/v/mcpack.svg)](https://pypi.org/project/mcpack/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mcpack.svg)](https://pypi.org/project/mcpack/)\n\n> A python library for programmatically creating and editing [Minecraft data packs](https://minecraft.gamepedia.com/Data_pack). Requires python 3.7.\n\n:construction: Work in progress :construction:\n',
    'author': 'Valentin Berlier',
    'author_email': 'berlier.v@gmail.com',
    'url': 'https://github.com/vberlier/mcpack',
    'py_modules': 'mcpack',
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
