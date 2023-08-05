"""Set up the Passwordwall settings in Plone control panel."""
from zope.interface import implementedBy
from zope.interface import classImplementsOnly
from zope.interface import alsoProvides
from zope.interface import noLongerProvides
from zope.component import getGlobalSiteManager
from zope.component import getUtility
from zope.formlib.form import FormFields

from plone.app.controlpanel.security import SecurityControlPanel
from plone.app.controlpanel.security import SecurityControlPanelAdapter
from plone.app.controlpanel.security import ISecuritySchema
from plone.registry import Record, field
from plone.registry.interfaces import IRegistry

from .interfaces import IPasswordwall, IPasswordwallSchema
from .settings import PASSWORD_REGISTRY_KEY
from .utils import get_password as utils_get_password


# add accessors to adapter


def get_passwordwall(self):
    """Getter."""
    return IPasswordwall.providedBy(self.portal)


SecurityControlPanelAdapter.get_passwordwall = get_passwordwall


def set_passwordwall(self, value):
    """Setter."""
    operator = value and alsoProvides or noLongerProvides
    operator(self.portal, IPasswordwall)

SecurityControlPanelAdapter.set_passwordwall = set_passwordwall

SecurityControlPanelAdapter.passwordwall = property(
    SecurityControlPanelAdapter.get_passwordwall,
    SecurityControlPanelAdapter.set_passwordwall
)


def get_password(self):
    """Getter."""
    return utils_get_password()

SecurityControlPanelAdapter.get_password = get_password


def set_password(self, value):
    """Setter."""
    registry = getUtility(IRegistry)
    if PASSWORD_REGISTRY_KEY not in registry:
        password_field = field.TextLine(title=u"Password for passwordwall")
        password_record = Record(password_field, value=value)
        registry.records[PASSWORD_REGISTRY_KEY] = password_record
    else:
        registry[PASSWORD_REGISTRY_KEY] = value

SecurityControlPanelAdapter.set_password = set_password

SecurityControlPanelAdapter.password = property(
    SecurityControlPanelAdapter.get_password,
    SecurityControlPanelAdapter.set_password
)

# re-register adapter with new interface
_decl = implementedBy(SecurityControlPanelAdapter)
_decl -= ISecuritySchema
_decl += IPasswordwallSchema
classImplementsOnly(SecurityControlPanelAdapter, _decl.interfaces())
del _decl

getGlobalSiteManager().registerAdapter(SecurityControlPanelAdapter)

# re-instantiate form
SecurityControlPanel.form_fields = FormFields(IPasswordwallSchema)
