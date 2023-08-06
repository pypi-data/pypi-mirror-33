from flask_oidc import OpenIDConnect
from flask import session, request


class Login:

    def __init__(self):
        self.oidc = OpenIDConnect()

    def init_app(self, app):

        app.config.setdefault('LOGIN_BEFORE_REQUEST', True)
        app.config.setdefault('LOGIN_USERINFO_FIELDS', [])

        self.oidc.init_app(app)
        self.userinfo_fileds = app.config['LOGIN_USERINFO_FIELDS']
        self.callback_route = app.config['OIDC_CALLBACK_ROUTE']
        if app.config['LOGIN_BEFORE_REQUEST']:
            app.before_request(self._before_request)

    def _before_request(self):
        redirect = self.oidc.authenticate_or_redirect()
        if not redirect and request.path != self.callback_route:
            session['user'] = self.oidc.user_getinfo(self.userinfo_fileds)
        return redirect

    def allowed(self, types):
        return session['user']['type'] in types
