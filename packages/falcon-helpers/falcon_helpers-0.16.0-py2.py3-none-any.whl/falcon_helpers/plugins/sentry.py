import logging
import falcon
import raven

from falcon_helpers.config import ConfigurationError

log = logging.getLogger(__name__)


class SentryPlugin:
    """Simple Sentry integration plugin

        sentry = falcon_helpers.plugins.SentryPlugin()
        app = falcon_helpers.API()
        app.config = {'sentry': {dsn': 'rand_sentry_dsn'}}

        sentry.register_app(app)

    You can get access to this globally so that you can capture exceptions without it having to get
    all the way up to the Falcon layer again.  Any exception that is caught by the falcon error
    handler will be sent to sentry (except HTTPError's and HTTPStatus's).

        sentry = Sentry()

        def create_app(config):
            app = falcon_helpers.API()
            app.config = config

            sentry.register(app)
            return app


        class SomeResource:

            def on_get(self, req, resp):
                try:
                    some_failure()
                except Exception as e:
                    sentry.captureException(e)
                    pass

    You have full access to the client with `sentry_plugin.client` and can update that do have
    special configurations.

    NOTE(nZac): if environment is passed or in the configuration, we will try to set that as well on
    the client to get environment support. By default the environment is `None`.
    """

    __slots__ = (
        '_dsn',
        'client',
        'environment',
    )

    @property
    def dsn(self):
        return self._dsn

    @dsn.setter
    def dsn(self, dsn):
        if dsn is None:
            self._dsn = None
            return

        self._dsn = dsn

        if self.client:
            self.client.set_dsn(self.dsn)

    def __init__(self, dsn=None, environment=None):
        self.client = None
        self.environment = environment
        self.dsn = dsn

    def _make_client(self):
        if not self.dsn:
            log.warning('No sentry client configured, errors will not be reported with Sentry.')

        return raven.Client(
            dsn=self.dsn,
            environment=self.environment,
        )

    def update_settings_from_app_config(self, app):
        """A hook allowing setup of sentry through a config convention.

        Subclass and override as necessary.
        """

        config = getattr(app, 'config', None)

        if config is None:
            return

        if self.environment is None:
            try:
                self.environment = config['sentry']['environment']
            except (KeyError, ConfigurationError):
                self.environment = None

        if self.dsn is None:
            try:
                self.dsn = config['sentry']['dsn']
            except (KeyError, ConfigurationError):
                self.dsn = None

        if not self.client:
            self.client = self._make_client()

    def register(self, app):
        self.update_settings_from_app_config(app)

        if not self.client:
            self.client = self._make_client()

        if self.client:
            app.add_error_handler(Exception, self.handle)

        app.plugins['sentry'] = self

    def handle(self, ex, req, resp, params):
        raisable = (falcon.http_error.HTTPError, falcon.http_status.HTTPStatus)

        if isinstance(ex, raisable):
            raise ex
        elif self.dsn:
            self.client.captureException(ex)
            raise falcon.HTTPInternalServerError()
        else:
            raise
