"""Passwordwall views."""
import hashlib

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from .settings import COOKIE_NAME
from .utils import get_password


def set_cookie(request):
    """Set cookie name + value + path.

    Value is an MD5 hash of the site password.
    Cookie doesn't expire (yet).
    """
    password = get_password()
    _hash = hashlib.md5(password).hexdigest()
    request.response.setCookie(
        COOKIE_NAME,
        _hash,
        path='/',
    )


class PasswordwallView(BrowserView):
    """Passwordwall view. Shows a login form."""

    index = ViewPageTemplateFile("passwordwall_form.pt")

    def __call__(self):
        """On succesful login, set cookie and redirect."""
        self.errors = []
        form = self.request.form
        if 'password' not in form:
            return self.index()
        if form['password'] != get_password():
            self.errors.append('Invalid password.')
            return self.index()

        # Apparently the creds were valid, set cookie.
        set_cookie(self.request)
        redirect_url = form.get('came_from') or self.context.absolute_url()
        self.request.response.redirect(redirect_url)
