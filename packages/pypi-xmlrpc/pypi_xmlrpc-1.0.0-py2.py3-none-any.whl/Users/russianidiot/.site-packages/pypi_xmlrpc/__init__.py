#!/usr/bin/env python
try:
    from xmlrpclib import ServerProxy  # python2
except ImportError:
    from xmlrpc.client import ServerProxy  # python3
from public import public

pypi = ServerProxy('https://pypi.org/pypi', allow_none=True)


@public
def list_packages():
    return pypi.list_packages()


@public
def user_packages(user):
    return pypi.user_packages(user)


@public
def release_urls(name, version):
    return pypi.release_urls(name, version)


@public
def package_roles(name):
    return pypi.package_roles(name)


@public
def package_releases(name, show_hidden=True):
    return pypi.package_releases(name, show_hidden)


@public
def release_data(name, version=True):
    return pypi.release_data(name, version)
