import pathlib

import falcon
import falcon.testing
import jwt
import pytest

from falcon_helpers.middlewares.parsejwt import ParseJWTMiddleware as MW
from falcon_helpers.config import ConfigurationError


@pytest.fixture(scope='module')
def rsa_priv_key():
    p = pathlib.Path(__file__).parent.parent.joinpath('files', 'keys', 'testkey')

    with open(p.as_posix(), mode='r') as fd:
        data = fd.read()
    return data


@pytest.fixture(scope='module')
def rsa_pub_key():
    p = pathlib.Path(__file__).parent.parent.joinpath('files', 'keys', 'testkey.pub')

    with open(p.as_posix(), mode='r') as fd:
        data = fd.read()
    return data


@pytest.fixture()
def hs_token():
    return jwt.encode({'key': 'hs', 'aud': 'test'}, 'secret', algorithm='HS256')


@pytest.fixture()
def rsa_token(rsa_priv_key):
    return jwt.encode({'key': 'rsa', 'aud': 'test'}, rsa_priv_key, algorithm='RS256')


def test_init_requires_one_of_a_cookie_or_header():
    with pytest.raises(ConfigurationError):
        MW(audience='blah')

    with pytest.raises(ConfigurationError):
        MW(audience='blah', cookie_name='cookie', header_name='header')

    assert MW(audience='blah', cookie_name='cookie')
    assert MW(audience='blah', header_name='cookie')


def test_init_pubkeys_checks():
    with pytest.raises(ConfigurationError):
        MW(audience='blah', cookie_name='cookie', pubkey='blank')

    assert MW(audience='blah', cookie_name='cookie', pubkey='ssh-rsa blah')
    assert MW(audience='blah', cookie_name='cookie', pubkey=None)


def test_verify_request_fails_without_token():
    mw = MW(audience='blah', cookie_name='cookie', secret='secret')

    with pytest.raises(ValueError):
        mw.verify_request(None)


def test_verification_types(hs_token, rsa_token, rsa_pub_key):
    with pytest.raises(ConfigurationError) as e:
        mw = MW(audience='test', cookie_name='cookie')
        mw.verify_request(hs_token)

    assert 'HS256' in str(e.value)
    assert 'requires a secret key.' in str(e.value)

    mw = MW(audience='test', cookie_name='cookie', secret='secret')
    assert mw.verify_request(hs_token) == {
        'key': 'hs',
        'aud': 'test',
    }

    with pytest.raises(ConfigurationError) as e:
        mw = MW(audience='test', cookie_name='cookie')
        mw.verify_request(rsa_token)

    assert 'RS256' in str(e.value)
    assert 'requires a public key.' in str(e.value)

    mw = MW(audience='test', cookie_name='cookie', pubkey=rsa_pub_key)
    assert mw.verify_request(rsa_token) == {
        'key': 'rsa',
        'aud': 'test',
    }


def test_process_request_with_header(hs_token):
    app = falcon.API(
        middleware=[MW(audience='test', secret='secret', header_name='Auth')]
    )
    client = falcon.testing.TestClient(app)

    resc = falcon.testing.SimpleTestResource()
    app.add_route('/', resc)

    resp = client.simulate_get('/')
    assert resp.status_code == 200
    assert 'auth_token_contents' not in resc.captured_req.context

    resp = client.simulate_get(
        '/',
        headers={
            'Auth': hs_token.decode(),
        }
    )
    assert resp.status_code == 200
    assert 'auth_token_contents' in resc.captured_req.context
    assert resc.captured_req.context['auth_token_contents'] == {
        'key': 'hs',
        'aud': 'test',
    }


def test_process_request_with_cookie(hs_token):
    app = falcon.API(
        middleware=[MW(audience='test', secret='secret', cookie_name='Auth')]
    )
    client = falcon.testing.TestClient(app)

    resc = falcon.testing.SimpleTestResource()
    app.add_route('/', resc)

    resp = client.simulate_get('/')
    assert resp.status_code == 200
    assert 'auth_token_contents' not in resc.captured_req.context

    resp = client.simulate_get('/', headers={'Cookie': 'Auth=' + hs_token.decode()})
    assert resp.status_code == 200
    assert 'auth_token_contents' in resc.captured_req.context
    assert resc.captured_req.context['auth_token_contents'] == {
        'key': 'hs',
        'aud': 'test',
    }


def test_process_request_with_default_failed_action():
    app = falcon.API(
        middleware=[MW(audience='test', secret='secret', header_name='Auth')]
    )
    client = falcon.testing.TestClient(app)

    resc = falcon.testing.SimpleTestResource()
    app.add_route('/', resc)

    resp = client.simulate_get('/', headers={'Auth': 'token'})
    assert resp.status_code == 200
    assert 'auth_token_contents' not in resc.captured_req.context


def test_process_request_with_custom_failed_action():
    def custom_failed(exc, req, resp):
        raise RuntimeError("works")

    app = falcon.API(
        middleware=[MW(audience='test', secret='secret', header_name='Auth',
                       when_fails=custom_failed)]
    )
    client = falcon.testing.TestClient(app)

    resc = falcon.testing.SimpleTestResource()
    app.add_route('/', resc)

    with pytest.raises(RuntimeError) as e:
        client.simulate_get('/', headers={'Auth': 'token'})

    assert 'works' == str(e.value)
