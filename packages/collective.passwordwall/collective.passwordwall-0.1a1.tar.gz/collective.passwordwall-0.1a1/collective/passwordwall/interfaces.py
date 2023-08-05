"""Passwordwall interfaces."""
from plone.app.controlpanel.security import ISecuritySchema
from zope.interface import Interface
from zope.schema import Bool, TextLine


class IPasswordwall(Interface):
    """Marker for sites behind passwordwall."""


class IPasswordwallSchema(ISecuritySchema):
    """Schema for passwordwall settings."""

    passwordwall = Bool(
        title=u'Site behind password',
        description=u"Users must enter credentials to view the site, "
        u"even Anonymous users",
        default=False,
        required=False,
    )

    password = TextLine(
        title=u'Site password',
        description=u"Users must enter this password to view the site. ",
        default=u'',
        required=False,
    )
