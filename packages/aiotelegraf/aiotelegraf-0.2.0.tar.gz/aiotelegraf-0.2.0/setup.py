# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['aiotelegraf']

package_data = \
{'': ['*']}

install_requires = \
['pytelegraf<1.0.0']

setup_kwargs = {
    'name': 'aiotelegraf',
    'version': '0.2.0',
    'description': 'AsyncIO Python client for sending metrics to Telegraf',
    'long_description': "# aiotelegraf [![Build Status](https://travis-ci.org/Gr1N/aiotelegraf.svg?branch=master)](https://travis-ci.org/Gr1N/aiotelegraf) [![codecov](https://codecov.io/gh/Gr1N/aiotelegraf/branch/master/graph/badge.svg)](https://codecov.io/gh/Gr1N/aiotelegraf) [![Updates](https://pyup.io/repos/github/Gr1N/aiotelegraf/shield.svg)](https://pyup.io/repos/github/Gr1N/aiotelegraf/) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\nAn asyncio-base client for sending metrics to [Telegraf](https://www.influxdata.com/time-series-platform/telegraf/).\n\nImplementation based on [pytelegraf](https://github.com/paksu/pytelegraf) package.\n\n## Installation\n\n    $ pip install aiotelegraf\n\n## Usage\n\n    import asyncio\n    import aiotelegraf\n\n    loop = asyncio.get_event_loop()\n    r = loop.run_until_complete\n\n    client = aiotelegraf.Client(\n        host='0.0.0.0',\n        port=8089,\n        tags={\n            'my_global_tag_1': 'value_1',\n            'my_global_tag_2': 'value_2',\n        }\n    )\n    r(client.connect())\n\n    client.metric('my_metric_1', 'value_1', tags={\n        'my_tag_1': 'value_1',\n    })\n    r(client.close())\n\n## Contributing\n\nTo work on the `aiotelegraf` codebase, you'll want to clone the project locally and install the required dependencies via [poetry](https://poetry.eustace.io):\n\n    $ git clone git@github.com:Gr1N/aiotelegraf.git\n    $ poetry install\n\nTo run tests and linters use command below:\n\n    $ poetry run tox\n\nIf you want to run only tests or linters you can explicitly specify which test environment you want to run, e.g.:\n\n    $ poetry run tox -e py37-tests\n\n## License\n\n`aiotelegraf` is licensed under the MIT license. See the license file for details.\n",
    'author': 'Nikita Grishko',
    'author_email': 'gr1n@protonmail.com',
    'url': 'https://github.com/Gr1N/aiotelegraf',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
