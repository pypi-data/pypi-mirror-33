from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution('coveragespace').version
except DistributionNotFound:
    __version__ = '(local)'

CLI = 'coveragespace'
API = 'https://api.coverage.space'

VERSION = "{0} v{1}".format(CLI, __version__)
