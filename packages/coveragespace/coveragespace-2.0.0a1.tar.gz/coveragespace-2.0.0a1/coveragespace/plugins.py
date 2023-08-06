"""Plugins to extract coverage data from various formats."""

import os
from abc import ABCMeta, abstractmethod
import time
import webbrowser
import logging

import coverage
from six import with_metaclass

from .cache import Cache


log = logging.getLogger(__name__)
cache = Cache()


class BasePlugin(with_metaclass(ABCMeta)):  # pragma: no cover (abstract class)
    """Base class for coverage plugins."""

    @abstractmethod
    def matches(self, cwd):
        """Determine if the current directory contains coverage data.

        :return bool: Indicates that the current directory should be processed.

        """

    @abstractmethod
    def get_coverage(self, cwd):
        """Extract the coverage data from the current directory.

        :return float: Percentage of lines covered.

        """

    @abstractmethod
    def get_report(self, cwd):
        """Get the path to the coverage report.

        :return str: Path to coverage report or `None` if not available.

        """


def get_coverage(cwd=None):
    """Extract the current coverage data."""
    cwd = cwd or os.getcwd()

    plugin = _find_plugin(cwd)
    percentage = plugin.get_coverage(cwd)

    return round(percentage, 1)


def launch_report(cwd=None):
    """Open the generated coverage report in a web browser."""
    cwd = cwd or os.getcwd()

    plugin = _find_plugin(cwd, allow_missing=True)

    if plugin:
        path = plugin.get_report(cwd)

        if path and not _launched_recently(path):
            log.info("Launching report: %s", path)
            webbrowser.open("file://" + path, new=2, autoraise=True)


def _find_plugin(cwd, allow_missing=False):
    """Find an return a matching coverage plugin."""
    for cls in BasePlugin.__subclasses__():  # pylint: disable=no-member
        plugin = cls()
        if plugin.matches(cwd):
            return plugin

    msg = "No coverage data found: {}".format(cwd)
    log.info(msg)

    if allow_missing:
        return None

    raise RuntimeError(msg + '.')


def _launched_recently(path):
    now = time.time()
    then = cache.get(path, default=0)
    elapsed = now - then
    log.debug("Last launched %s seconds ago", elapsed)
    cache.set(path, now)
    return elapsed < 60 * 60  # 1 hour


class CoveragePy(BasePlugin):
    """Coverage extractor for the coverage.py format."""

    def matches(self, cwd):
        return '.coverage' in os.listdir(cwd)

    def get_coverage(self, cwd):
        os.chdir(cwd)

        cov = coverage.Coverage()
        cov.load()

        with open(os.devnull, 'w') as ignore:
            total = cov.report(file=ignore)

        return total

    def get_report(self, cwd):
        path = os.path.join(cwd, 'htmlcov', 'index.html')

        if os.path.isfile(path):
            log.info("Found coverage report: %s", path)
            return path

        log.info("No coverage report found: %s", cwd)
        return None
