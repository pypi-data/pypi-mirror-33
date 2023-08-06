# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['coveragespace', 'coveragespace.tests']

package_data = \
{'': ['*']}

install_requires = \
['backports.shutil-get-terminal-size>=1.0,<2.0',
 'colorama>=0.3,<0.4',
 'coverage>=4.0,<5.0',
 'docopt>=0.6,<0.7',
 'requests>=2.0,<3.0']

entry_points = \
{'console_scripts': ['coveragespace = coveragespace.cli:main']}

setup_kwargs = {
    'name': 'coveragespace',
    'version': '2.0.0a1',
    'description': 'A place to track your code coverage metrics.',
    'long_description': 'Unix: [![Unix Build Status](http://img.shields.io/travis/jacebrowning/coverage-space-cli/develop.svg)](https://travis-ci.org/jacebrowning/coverage-space-cli) Windows: [![Windows Build Status](https://img.shields.io/appveyor/ci/jacebrowning/coverage-space-cli/develop.svg)](https://ci.appveyor.com/project/jacebrowning/coverage-space-cli)<br>Metrics: [![Coverage Status](http://img.shields.io/coveralls/jacebrowning/coverage-space-cli/develop.svg)](https://coveralls.io/r/jacebrowning/coverage-space-cli) [![Scrutinizer Code Quality](http://img.shields.io/scrutinizer/g/jacebrowning/coverage-space-cli.svg)](https://scrutinizer-ci.com/g/jacebrowning/coverage-space-cli/?branch=develop)<br>Usage: [![PyPI Version](http://img.shields.io/pypi/v/coveragespace.svg)](https://pypi.python.org/pypi/coveragespace)\n\n# Overview\n\nThe official command-line client for [The Coverage Space](http://coverage.space).\n\n# Setup\n\n## Requirements\n\n* Python 2.7+ or Python 3.3+\n\n## Installation\n\nThe client can be installed with pip:\n\n```sh\n$ pip install --upgrade coverage-space\n```\n\nor directly from the source code:\n\n```sh\n$ git clone https://github.com/jacebrowning/coverage-space-cli.git\n$ cd coverage-space-cli\n$ python setup.py install\n```\n\n# Usage\n\nTo update the value for a test coverage metric:\n\n```sh\n$ coveragespace <owner/repo> <metric>\n```\n\nFor example, after testing with code coverage enabled:\n\n```sh\n$ coveragespace owner/repo unit\n```\n\nwill attempt to extract the current coverage data from your working tree and compare that with the last known value. The coverage value can also be manually specified:\n\n```sh\n$ coveragespace <owner/repo> <metric> <value>\n```\n',
    'author': 'Jace Browning',
    'author_email': 'jacebrowning@gmail.com',
    'url': 'https://coverage.space/client/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*',
}


setup(**setup_kwargs)
