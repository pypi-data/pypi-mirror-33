# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['worldcup18']

package_data = \
{'': ['*']}

install_requires = \
['click>=6.7,<7.0',
 'python-dateutil>=2.7,<3.0',
 'pytz>=2018.4,<2019.0',
 'requests>=2.19,<3.0',
 'tzlocal>=1.5,<2.0']

entry_points = \
{'console_scripts': ['worldcup = worldcup18.worldcup:cli']}

setup_kwargs = {
    'name': 'worldcup18',
    'version': '0.1.1',
    'description': 'A simple CLI to stay up to date with 2018 World Cup',
    'long_description': '# worldcup18\n\n[![Build Status](https://travis-ci.org/tadeoos/worldcup.svg?branch=master)](https://travis-ci.org/tadeoos/worldcup)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/Worldcup18.svg)](https://pypi.org/project/worldcup18/)\n\nA simple CLI to stay up to date with 2018 World Cup\n\n## installation\n\n```\npip install worldcup18\n```\n\n## demo\n\n```\n$ worldcup next\nMatch #5: 🇫🇷  France vs Australia 🇦🇺\nWhen: Saturday, 16. June 2018 12:00PM\nWhere: Kazan\n\n$ worldcup groups a\nGROUP A                    MP GF GA PTS\n---------------------------------------\nRussia                      1  5  0  3\nUruguay                     1  1  0  3\nEgypt                       1  0  1  0\nSaudi Arabia                1  0  5  0\n\n$ worldcup --help\nUsage: worldcup.py [OPTIONS] COMMAND [ARGS]...\n\n  CLI tool for being up to date with 2018 World Cup\n\nOptions:\n  --help  Show this message and exit.\n\nCommands:\n  groups  Show group info\n  next    Show nearest match info\n```\n\n## developement\n\n## acknowledgments\n\nWorld Cup data available thanks to json file from [lsv fifa-worldcup-2018](https://github.com/lsv/fifa-worldcup-2018)\n\nInspired by: [SkullCarverCoder](https://github.com/SkullCarverCoder/wc18-cli)\n',
    'author': 'Tadek Teleżyński',
    'author_email': 'tadekte@gmail.com',
    'url': 'https://github.com/tadeoos/worldcup',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
}


setup(**setup_kwargs)
