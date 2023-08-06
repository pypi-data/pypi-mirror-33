import pytest
import sqlalchemy as sa

from falcon_helpers.app import API
from falcon_helpers.plugins import SQLAlchemyPlugin


def test_plugin_takes_string_url():
    assert SQLAlchemyPlugin('sqlite://').url == sa.engine.url.make_url('sqlite://')


def test_plugin_takes_dict():
    assert SQLAlchemyPlugin({
        'drivername': 'sqlite',
        'host': 'localhost',
        'username': 'myuser',
        'password': 'mypassword',
    }).url == sa.engine.url.make_url('sqlite://myuser:mypassword@localhost')


def test_plugin_takes_url():
    url = sa.engine.url.URL(**{
        'drivername': 'sqlite',
    })
    assert SQLAlchemyPlugin(url).url == sa.engine.url.make_url('sqlite://')


def test_plugin_raises_on_bad_url():
    with pytest.raises(RuntimeError):
        SQLAlchemyPlugin(['bad'])


def test_register_plugin():
    url = sa.engine.url.URL(**{
        'drivername': 'sqlite',
    })
    sess = sa.orm.session.Session()
    pl = SQLAlchemyPlugin(url=url, session=sess)

    app = API()
    pl.register(app)

    assert app.plugins['sqla'] == pl
    assert pl.engine.url == url

    assert pl.session.bind == pl.engine

    assert app._dynmw.req_mw == []
    assert app._dynmw.resc_mw == [pl.mw.process_resource]
    assert app._dynmw.resp_mw == [pl.mw.process_response]


def test_register_plugin_with_sessionmaker():
    url = sa.engine.url.URL(**{
        'drivername': 'sqlite',
    })
    sess = sa.orm.session.sessionmaker()
    pl = SQLAlchemyPlugin(url=url, session=sess)

    app = API()
    pl.register(app)

    assert pl.session().bind == pl.engine
