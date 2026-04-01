from plone import api
from dummy import __version__


def foo_bar():
    return api.portal.get().title + " " + __version__
