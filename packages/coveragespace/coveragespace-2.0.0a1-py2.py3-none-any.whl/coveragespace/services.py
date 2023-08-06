"""Utilities to detect when this program is running on external services."""

import os


CONTINUOUS_INTEGRATION = [

    # General
    'CI',
    'CONTINUOUS_INTEGRATION',
    'DISABLE_COVERAGE',

    # Travis CI
    'TRAVIS',

    # Appveyor
    'APPVEYOR',

    # CircleCI
    'CIRCLECI',

    # Drone
    'DRONE',

]


def detected():
    return any(name in CONTINUOUS_INTEGRATION for name in os.environ)
