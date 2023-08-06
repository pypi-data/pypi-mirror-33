from txdocumint._client import create_session, get_session


__all__ = ['create_session', 'get_session']

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
