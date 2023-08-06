import unittest.mock as mock
import falcon.testing
import pytest

from falcon_helpers import API
from falcon_helpers.resources.auth0 import LoginCallbackResource


@pytest.fixture()
def app():
    return API()


@pytest.fixture()
def client(app):
    return falcon.testing.TestClient(app)


class TestLoginCallbackResource:

    def test_callback_resource_default_failed(self, client):
        resc = LoginCallbackResource('url', 'id', 'secret', 'uri', 'domain', False)
        client.app.add_route('/auth/callback', resc)
        resp = client.simulate_get('/auth/callback')

        assert resp.status_code == 307
        assert resp.headers['location'] == '/'

    def test_callback_resource_custom_failed(self, client):
        def when_fails(req, resp, error, message, **kwargs):
            resp.media = {'error': 'custom'}
            raise falcon.HTTPStatus('200 OK')

        resc = LoginCallbackResource('url', 'id', 'secret', 'uri', 'domain', False,
                                     when_fails=when_fails)
        client.app.add_route('/auth/callback', resc)
        resp = client.simulate_get('/auth/callback')

        assert resp.status_code == 200
        assert resp.json == {'error': 'custom'}

    def test_callback_resource_custom_failed_doesnt_raise(self, client):
        def when_fails(req, resp, error, message, **kwargs):
            resp.media = {'error': 'custom'}

        resc = LoginCallbackResource('url', 'id', 'secret', 'uri', 'domain', False,
                                     when_fails=when_fails)
        client.app.add_route('/auth/callback', resc)
        resp = client.simulate_get('/auth/callback')

        assert resp.status_code == 500

    @mock.patch('falcon_helpers.resources.auth0.requests.post')
    def test_callback_resource_happy_path(self, m_request, client):
        resc = LoginCallbackResource('url', 'id', 'secret', 'uri', 'domain', False)
        client.app.add_route('/auth/callback', resc)
        resp = client.simulate_get('/auth/callback', params={'code': 'thing'})

        assert resp.status_code == 302

    def test_callback_resource_with_error_code(self, client):
        def when_fails(req, resp, error, message, **kwargs):
            resp.media = {'error': error, 'message': message}
            raise falcon.HTTPStatus('200 OK')

        resc = LoginCallbackResource('url', 'id', 'secret', 'uri', 'domain', False,
                                     when_fails=when_fails)
        client.app.add_route('/auth/callback', resc)
        resp = client.simulate_get('/auth/callback', params={
            'error': 'error',
            'error_description': 'description'
        })

        assert resp.status_code == 200
        assert resp.json == {'error': 'error', 'message': 'description'}
