"""Helper methods."""
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from .settings import PASSWORD_REGISTRY_KEY


def get_password():
    """Get passwordwall password from registry."""
    registry = getUtility(IRegistry)
    if PASSWORD_REGISTRY_KEY not in registry:
        return ''
    return registry[PASSWORD_REGISTRY_KEY]
