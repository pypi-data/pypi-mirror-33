import typing
import sqlalchemy as sa

import falcon_helpers.sqla.db as db
from falcon_helpers.middlewares.sqla import SQLAlchemySessionMiddleware


class SQLAlchemyPlugin:
    """Setup SQLAlchemy for use within an application

    If the application has a config property, that property is a dictionary, and that dictionary has
    a key called `sqla` which has the standard SQLA Engine properties, all you have to do is call
    the `register` function and this plugin will do everything for you.

    Quick start:

        import falcon_helpers.plugins as plugins

        sqla = plugins.SQLAlchemyPlugin()

        class MyApp(falcon_helpers.API):
            pass


        app = MyApp()

        # consider using the configuration class as a part of Falcon-Helpers
        app.config = {
            'sqla': {
                'drivername': '',
                'username': 'myuser',
                'password': 'somepassword',
                'host': 'localhost',
                'port': '5432',
                database': 'myapp'
            }
        }

        sqla.register(app)


    """

    __slots__ = (
        '_url',
        'engine',
        'session',
        'mw',
    )

    def __init__(self, url=None, session=db.session):
        if url:
            self.url = url
        else:
            self._url = None

        self.session = session
        self.engine = None
        self.mw = None

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        if isinstance(url, typing.Dict):
            self._url = sa.engine.url.URL(**url)
        elif isinstance(url, str):
            self._url = sa.engine.url.make_url(url)
        elif isinstance(url, sa.engine.url.URL):
            self._url = url
        else:
            raise RuntimeError(
                'Passed SQLAlchemy URL does not seem to be a valid value. Expecting dict, string '
                'or url, got {type(url)}'
            )

    def register(self, app):
        if not self.url:
            self.url = app.config.get('sqla', None)

        self.engine = sa.create_engine(self.url)

        if isinstance(self.session, sa.orm.session.Session):
            self.session.bind = self.engine
        else:
            self.session.configure(bind=self.engine)

        self.mw = SQLAlchemySessionMiddleware()
        app.add_middleware(self.mw)

        app.plugins['sqla'] = self
