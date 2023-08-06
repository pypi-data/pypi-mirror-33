# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['crunchy_api']

package_data = \
{'': ['*']}

extras_require = \
{'cli': ['click>=6.7,<7.0']}

entry_points = \
{'console_scripts': ['crunchy = crunchy_api.cli:main']}

setup_kwargs = {
    'name': 'crunchy-api',
    'version': '0.3.0',
    'description': 'Python wrapper for the Crunchyroll API',
    'long_description': '# crunchy-api\n\nAn API for crunchyroll\n',
    'author': 'David Buckley',
    'author_email': 'buckley.w.david@gmail.com',
    'url': 'https://github.com/buckley-w-david/crunchy-api',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
