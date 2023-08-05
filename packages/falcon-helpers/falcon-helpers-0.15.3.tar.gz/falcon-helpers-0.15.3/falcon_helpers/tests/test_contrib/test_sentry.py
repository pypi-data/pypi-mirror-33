import falcon.testing
import unittest.mock as mock
import pytest

import falcon_helpers.contrib.sentry as sentry


class FakeException(Exception):
    pass


@pytest.fixture()
def app():
    app = falcon.API()

    class FakeResource:
        def on_get(self, req, resp):
            raise FakeException('Failed')

    app.add_route('/fails', FakeResource())

    return app


@pytest.fixture()
def client(app):
    return falcon.testing.TestClient(app)


@mock.patch('falcon_helpers.contrib.sentry.raven.Client', spec_set=True, autospec=True)
def test_sentry(m_client, client):
    plugin = sentry.Sentry('test_dsn')
    plugin.register(client.app)

    client.simulate_get('/fails')
    name, args, kwargs = m_client.method_calls[0]

    assert plugin.dsn == 'test_dsn'
    assert isinstance(args[0], FakeException)
