import falcon.testing
import pytest
import sqlalchemy as sa

from falcon_helpers.middlewares.sqla import SQLAlchemySessionMiddleware
import falcon_helpers.sqla.db as db


class MockResource(falcon.testing.SimpleTestResource):

    def on_delete(self, req, resp):
        self.session.execute('BAD')
        self.session.execute('BAD')


@pytest.fixture()
def client():
    api = falcon.API(middleware=[
        SQLAlchemySessionMiddleware()
    ])

    return falcon.testing.TestClient(api)


def test_mw_takes_custom_session(client):
    sess = sa.orm.session.Session()
    assert db.session != sess

    mw = SQLAlchemySessionMiddleware(sess)
    api = falcon.API(middleware=[mw])
    resc = MockResource()
    api.add_route('/', resc)
    custom_client = falcon.testing.TestClient(api)

    custom_client.simulate_get('/')
    assert resc.session == sess

    resc2 = MockResource()
    client.app.add_route('/', resc2)
    client.simulate_get('/')
    assert resc2.session == db.session
