import logging

import falcon
import requests

from ..middlewares.jinja2 import Jinja2Response


log = logging.getLogger(__name__)


def _default_failed(req, resp, error, message, **kwargs):
    raise falcon.HTTPTemporaryRedirect('/')


class LoginFormResource:
    auth_required = False

    def __init__(self, client_url, client_id, callback_uri, template_path='auth/login.html'):
        self.client_url = client_url
        self.client_id = client_id
        self.callback_uri = callback_uri
        self.template_path = template_path

    # Load form
    def on_get(self, req, resp):
        resp.context['template'] = Jinja2Response(
            self.template_path,
            auth0_config={
                'client_url': self.client_url,
                'client_id': self.client_id,
                'callback_uri': self.callback_uri,
            })


class LoginCallbackResource:
    auth_required = False

    def __init__(self, client_url, client_id, client_secret, callback_uri,
                 cookie_domain, secure_cookie, cookie_name='X-AuthToken',
                 cookie_max_age=(24 * 60 * 60), cookie_path='/',
                 redirect_uri='/dashboard', after_login=None, when_fails=_default_failed,
                 ):
        self.client_url = client_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback_uri = callback_uri
        self.redirect_uri = redirect_uri
        self.failed_action = when_fails

        self.cookie_domain = cookie_domain

        if not isinstance(secure_cookie, bool):
            raise RuntimeError(
                f'secure_cookie must be a literal True or False, got {secure_cookie}.'
            )

        self.secure_cookie = secure_cookie
        self.cookie_name = cookie_name
        self.cookie_max_age = cookie_max_age
        self.cookie_path = cookie_path
        self.after_login = after_login or (lambda data, req, resp: resp)

    def on_get(self, req, resp):
        auth_code = req.params.get('code', None)

        if auth_code is None:
            error = req.params.get('error', None)

            if error is None:
                # Something wierd is happening, likely someone is hitting our callback without it
                # coming from Auth0, in that case, log and run away.
                msg = (
                    f'The callback url was reached without an `auth_code` and without and `error` '
                    f'in the params. That should not be possible if it is coming from Auth0.'
                )
                log.warning(msg)
                self.failed_action(req, resp, error='no_auth_token_or_error', message=msg)
            else:
                msg = req.params.get('error_description', '')
                self.failed_action(req, resp, error=error, message=msg)

            self.failed_action(req, resp, error='no_auth_token',
                               message='No Authentication token was found for this request.')

            # failed_action might not raise and might not eject us from this request, if that
            # happens, we can't continue so through a bad request.
            log.error(
                f'Someone accessed the authentication callback url and did not have an error or an '
                f'auth_code. We called failed_action, but you did not raise an exception. We can '
                f'not continue with this request. Failed actions should handle the error.'
            )
            raise falcon.HTTPInternalServerError(
                title='Authentication Error',
                description='An internal error occurred during authentication.'
            )

        data = self.get_user_data(auth_code)

        self.set_cookie_contents(resp, data)
        resp.set_header('Location', self.redirect_uri)
        resp.status = falcon.HTTP_302

        self.after_login(data, req=req, resp=resp)

    def get_user_data(self, auth_code):
        token = requests.post(
            f'https://{self.client_url}/oauth/token',
            data={
                'grant_type': 'authorization_code',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': auth_code,
                'redirect_uri': self.callback_uri,
            })

        if not token.ok:
            raise falcon.HTTPTemporaryRedirect('/auth/login')

        return token.json()

    def set_cookie_contents(self, resp, data):
        resp.set_cookie(self.cookie_name,
                        data['id_token'],
                        max_age=self.cookie_max_age,
                        secure=self.secure_cookie,
                        path=self.cookie_path,
                        domain=self.cookie_domain)


class LogoutResource:
    auth_required = False

    def __init__(self, cookie_domain, secure_cookie, cookie_name='X-AuthToken',
                 cookie_path='/'):
        self.cookie_domain = cookie_domain
        self.secure_cookie = secure_cookie

        self.cookie_name = cookie_name
        self.cookie_path = cookie_path

    def on_get(self, req, resp):
        resp.set_cookie(self.cookie_name, '', secure=self.secure_cookie,
                        path=self.cookie_path, domain=self.cookie_domain)

        resp.status = falcon.HTTP_302
        resp.set_header('Location', '/auth/login')
