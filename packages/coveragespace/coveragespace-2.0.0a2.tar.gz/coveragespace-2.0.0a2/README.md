Unix: [![Unix Build Status](http://img.shields.io/travis/jacebrowning/coverage-space-cli/develop.svg)](https://travis-ci.org/jacebrowning/coverage-space-cli) Windows: [![Windows Build Status](https://img.shields.io/appveyor/ci/jacebrowning/coverage-space-cli/develop.svg)](https://ci.appveyor.com/project/jacebrowning/coverage-space-cli)<br>Metrics: [![Coverage Status](http://img.shields.io/coveralls/jacebrowning/coverage-space-cli/develop.svg)](https://coveralls.io/r/jacebrowning/coverage-space-cli) [![Scrutinizer Code Quality](http://img.shields.io/scrutinizer/g/jacebrowning/coverage-space-cli.svg)](https://scrutinizer-ci.com/g/jacebrowning/coverage-space-cli/?branch=develop)<br>Usage: [![PyPI Version](http://img.shields.io/pypi/v/coveragespace.svg)](https://pypi.python.org/pypi/coveragespace)

# Overview

The official command-line client for [The Coverage Space](http://coverage.space).

# Setup

## Requirements

* Python 2.7+ or Python 3.3+

## Installation

The client can be installed with pip:

```sh
$ pip install --upgrade coveragespace
```

or directly from the source code:

```sh
$ git clone https://github.com/jacebrowning/coverage-space-cli.git
$ cd coverage-space-cli
$ python setup.py install
```

# Usage

To update the value for a test coverage metric:

```sh
$ coveragespace <owner/repo> <metric>
```

For example, after testing with code coverage enabled:

```sh
$ coveragespace owner/repo unit
```

will attempt to extract the current coverage data from your working tree and compare that with the last known value. The coverage value can also be manually specified:

```sh
$ coveragespace <owner/repo> <metric> <value>
```
