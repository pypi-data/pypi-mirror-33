# pylint: disable=missing-docstring,unused-variable,unused-argument,expression-not-assigned,singleton-comparison
import time
from mock import patch, Mock

import pytest
from expecter import expect

from coveragespace.plugins import get_coverage, cache, _launched_recently


class MockCoverage(Mock):

    @staticmethod
    def report(*args, **kwargs):
        return 42.456


def describe_get_coverage():

    @pytest.fixture
    def coveragepy_data(tmpdir):
        cwd = tmpdir.chdir()
        with open("foobar.py", 'w') as stream:
            pass
        with open(".coverage", 'w') as stream:
            stream.write("""
            !coverage.py: This is a private format, don\'t read it directly!
            {"arcs":{"foobar.py": [[-1, 3]]}}
            """.strip())

    @patch('coverage.Coverage', MockCoverage)
    def it_supports_coveragepy(coveragepy_data):
        expect(get_coverage()) == 42.5


def describe_launched_recently():

    def when_never_launched():
        cache.set('mock/path', 0)
        expect(_launched_recently('mock/path')) == False

    def when_just_launched():
        cache.set('mock/path', time.time())
        expect(_launched_recently('mock/path')) == True

    def when_launched_59_minutes_ago():
        cache.set('mock/path', time.time() - 60 * 59)
        expect(_launched_recently('mock/path')) == True

    def when_launched_61_minutes_ago():
        cache.set('mock/path', time.time() - 60 * 61)
        expect(_launched_recently('mock/path')) == False
