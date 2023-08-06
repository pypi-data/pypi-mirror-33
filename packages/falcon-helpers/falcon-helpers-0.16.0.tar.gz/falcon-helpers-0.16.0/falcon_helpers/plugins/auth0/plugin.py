import pathlib
import falcon_helpers.middlewares as mws
import falcon_helpers.resources.auth0 as rescs


BASEDIR = pathlib.Path(__file__).parent


class Auth0Plugin:

    __slots__ = (
        'callback_url',
        'client_id',
        'client_pubkey',
        'client_secret',
        'client_url',
        'cookie_domain',
        'cookie_name',
        'use_secure_cookie',
        'success_url',
        'login_route',
        'logout_route',
        'callback_route',
        'include_jinja2_middleware',
        'include_auto_parse_jwt',
        'template_dpath',
    )

    def __init__(self, client_url, client_id, client_pubkey, client_secret, callback_url,
                 **options):
        self.client_url = client_url
        self.client_id = client_id
        self.client_pubkey = client_pubkey
        self.client_secret = client_secret
        self.callback_url = callback_url

        self.login_route = options.get('login_route', '/auth/login')
        self.logout_route = options.get('logout_route', '/auth/logout')
        self.callback_route = options.get('callback_route', '/auth/callback')
        self.cookie_domain = options.get('cookie_domain', '')
        self.cookie_name = options.get('cookie_name', 'X-AuthToken')

        self.success_url = options.get('success_url', '/')
        self.use_secure_cookie = options.get('use_secure_cookie', True)
        self.include_jinja2_middleware = options.get('include_jinja2_middleware', True)
        self.include_auto_parse_jwt = options.get('include_auto_parse_jwt', True)
        self.template_dpath = options.get(
            'template_dpath', BASEDIR.joinpath('templates').as_posix()
        )

    def register(self, app):
        self.setup_routes(app)

        if self.include_jinja2_middleware:
            app.add_middleware(mws.Jinja2Middleware(self.template_dpath))

        if self.include_auto_parse_jwt:
            app.add_middleware(
                mws.ParseJWTMiddleware(
                    audience=self.client_id,
                    pubkey=self.client_pubkey,
                    secret=self.client_secret,
                    cookie_name=self.cookie_name,
                )
            )

        app.plugins['auth0'] = self

    def setup_routes(self, app):
        app.add_route(
            self.login_route,
            rescs.LoginFormResource(
                client_url=self.client_url,
                client_id=self.client_id,
                callback_uri=self.callback_url,
                template_path='login.html',
            )
        )
        app.add_route(
            self.logout_route,
            rescs.LogoutResource(
                cookie_domain=self.cookie_domain,
                secure_cookie=self.use_secure_cookie,
            )
        )
        app.add_route(
            '/auth/callback',
            rescs.LoginCallbackResource(
                client_url=self.client_url,
                client_id=self.client_id,
                client_secret=self.client_secret,
                callback_uri=self.callback_url,
                cookie_domain=self.cookie_domain,
                cookie_name=self.cookie_name,
                secure_cookie=self.use_secure_cookie,
                redirect_uri=self.success_url,
            )
        )
