# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['airtable_schema']

package_data = \
{'': ['*']}

install_requires = \
['click>=6.7,<7.0']

extras_require = \
{'selenium': ['selenium>=3.13,<4.0']}

entry_points = \
{'console_scripts': ['airtable = airtable_schema.cli:main']}

setup_kwargs = {
    'name': 'airtable-schema',
    'version': '0.2.0',
    'description': 'Schema management for Airtable',
    'long_description': '# Airtable-schema\n\nSchema management for Airtable!\n',
    'author': 'David Buckley',
    'author_email': 'buckley.w.david@gmail.com',
    'url': 'https://github.com/buckley-w-david/airtable-schema',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
