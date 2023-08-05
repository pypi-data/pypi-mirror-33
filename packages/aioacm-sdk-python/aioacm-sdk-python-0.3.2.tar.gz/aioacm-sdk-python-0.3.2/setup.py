# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['aioacm']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.3,<4.0',
 'aliyun-python-sdk-core-v3>=2.8,<3.0',
 'aliyun-python-sdk-kms>=2.5,<3.0']

setup_kwargs = {
    'name': 'aioacm-sdk-python',
    'version': '0.3.2',
    'description': 'Python client for ACM with asyncio support.',
    'long_description': None,
    'author': 'songww',
    'author_email': 'sww4718168@gmail.com',
    'url': 'https://github.com/ioimop/aioacm',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5',
}


setup(**setup_kwargs)
