"""Initalize Passwordwall."""
import hashlib

from AccessControl import getSecurityManager

from .settings import COOKIE_NAME, PASSWORDWALL_VIEW_NAME
from .utils import get_password


def is_anonymous_user():
    """Return False if user is logged in."""
    u = getSecurityManager().getUser()
    return (u is None or u.getUserName() == 'Anonymous User')


def setBody(self, *args, **kw):  # NOQA
    """Do not set response body, overriding the ZServerHTTPResponse method.

    The hook that redirects to the password from will set the 302 redirect
    status, but after that the Publisher will still render it. Browsers will
    not show this content, but you can still see it with curl/wget, and bots
    will also find it.

    To prevent the body from being set, we override this method from
    ZServerHTTPResponse, so no body is set.
    """
    pass


def start_auth_dialog(request):
    """Start authentication dialog: redirect to passwordwall login view."""
    pwwall_url = request.ACTUAL_URL.rstrip('/') + PASSWORDWALL_VIEW_NAME

    # If user went to /news, we redirect there after login.
    came_from = request.ACTUAL_URL
    request.form = {'came_from': came_from}

    # Override response's setBody method so no Plone content is shown.
    request.response.setBody = setBody

    request.response.redirect(pwwall_url)


def has_valid_cookie(request):
    """Check if request has valid cookie."""
    value = request.cookies.get(COOKIE_NAME)
    password = get_password()
    _hash = hashlib.md5(password).hexdigest()
    return value == _hash


def reject_missing_password(portal, request):
    """Check for passwordwall cookie."""
    # Copied from rejectAnonymous
    if request['REQUEST_METHOD'] == 'OPTIONS':
        return
    # Don't ask again if already logged in
    if not is_anonymous_user():
        return
    # If we're on the passwordwall page, continue
    if request.ACTUAL_URL.rstrip('/').endswith(PASSWORDWALL_VIEW_NAME):
        return
    # If user has a valid cookie, let them in
    if has_valid_cookie(request):
        return
    start_auth_dialog(request)


def insert_reject_missing_password_hook(portal, event):
    """Insert the hook that checks for passwordwall creds."""
    try:
        event.request.post_traverse(
            reject_missing_password,
            (portal, event.request),
        )
    except RuntimeError:
        # Make this work in a testrunner (copied from iw.rejectanonymous)
        pass
