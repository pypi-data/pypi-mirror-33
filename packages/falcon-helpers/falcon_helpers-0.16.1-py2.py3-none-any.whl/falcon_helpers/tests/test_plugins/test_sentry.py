import falcon.testing
import pytest

from falcon_helpers import API
from falcon_helpers.plugins import SentryPlugin


class FakeException(Exception):
    pass


@pytest.fixture()
def app():
    app = API()

    class FakeResource:
        def on_get(self, req, resp):
            raise FakeException('Failed')

    app.add_route('/fails', FakeResource())

    return app


@pytest.fixture()
def client(app):
    return falcon.testing.TestClient(app)


def test_sentry_with_dsn(mocked_sentry_client, client):
    plugin = SentryPlugin('test_dsn')
    plugin.register(client.app)

    client.simulate_get('/fails')
    name, args, kwargs = mocked_sentry_client.method_calls[0]

    assert plugin.dsn == 'test_dsn'
    assert isinstance(args[0], FakeException)


def test_sentry_without_dsn_still_raise(mocked_sentry_client, client):
    plugin = SentryPlugin()
    plugin.register(client.app)

    with pytest.raises(FakeException):
        client.simulate_get('/fails')


def test_sentry_pulls_from_app_config(mocked_sentry_client, client):
    plugin = SentryPlugin()
    client.app.config = {
        'sentry': {
            'dsn': 'something',
            'environment': 'prod',
        }
    }
    plugin.register(client.app)

    assert plugin.dsn == 'something'
    assert plugin.environment == 'prod'
