import falcon.testing
import pytest
import sqlalchemy as sa
import marshmallow as mm
import marshmallow_sqlalchemy as mms

import falcon_helpers.sqla.orm as orm
import falcon_helpers.sqla.db as db
from falcon_helpers.middlewares.marshmallow import MarshmallowMiddleware


@pytest.fixture()
def client():
    api = falcon.API(middleware=[
        MarshmallowMiddleware()
    ])

    return falcon.testing.TestClient(api)


class ObjEntity(orm.BaseColumns, orm.ModelBase):
    __tablename__ = 'obj_entity'

    name = sa.Column(sa.String)


class Obj(mms.ModelSchema):
    name = mm.fields.String()

    class Meta:
        model = ObjEntity


class WithoutSchemaResc(falcon.testing.SimpleTestResource):
    pass


class WithSchemaResc(falcon.testing.SimpleTestResource):
    schema = Obj


class WithCustomLoader(WithSchemaResc):
    def schema_loader(self, data, req, resource, params):
        result = self.schema().load(data, session=db.session)
        result.data.name = 'other'
        return result


def test_get_is_not_marshalled(client):
    resource = falcon.testing.SimpleTestResource()

    client.app.add_route('/test', resource)
    resp = client.simulate_get('/test')

    assert resp.status_code == 200
    assert not resource.captured_req.context['_marshalled']


def test_post_is_not_marshalled_without_body(client):
    resource = falcon.testing.SimpleTestResource()

    client.app.add_route('/test', resource)
    resp = client.simulate_post('/test')

    assert resp.status_code == 200
    assert not resource.captured_req.context['_marshalled']


def test_post_is_not_marshalled_with_json_but_has_schema(client):
    resource = WithoutSchemaResc()

    client.app.add_route('/test', resource)
    resp = client.simulate_post(
        '/test',
        json={}
    )

    assert resp.status_code == 200
    assert not resource.captured_req.context['_marshalled']


def test_turning_off_auto_marshalling(client):
    resource = WithSchemaResc()
    resource.auto_marshall = False

    client.app.add_route('/test', resource)
    resp = client.simulate_post(
        '/test',
        json={}
    )

    assert resp.status_code == 200
    assert not resource.captured_req.context['_marshalled']


def test_turning_verify_content_type_is_json(client):
    resource = WithSchemaResc()

    client.app.add_route('/test', resource)
    resp = client.simulate_post(
        '/test',
        body='["looks like json"]'
    )

    assert resp.status_code == 200
    assert not resource.captured_req.context['_marshalled']


def test_turning_verify_content_length(client):
    resource = WithSchemaResc()

    client.app.add_route('/test', resource)
    resp = client.simulate_post(
        '/test',
        headers={'Content-Type': 'application/json'},
        body=''
    )

    assert resp.status_code == 200
    assert not resource.captured_req.context['_marshalled']


def test_the_happy_path(client):
    resource = WithSchemaResc()
    client.app.add_route('/test', resource)
    resp = client.simulate_post(
        '/test',
        json={'name': 'john'}
    )

    assert resp.status_code == 200
    assert resource.captured_req.context['_marshalled']


def test_keeps_the_media_and_populates_the_raw_stream(client):
    resource = WithSchemaResc()
    client.app.add_route('/test', resource)

    resp = client.simulate_post(
        '/test',
        json={'name': 'john'}
    )

    assert resp.status_code == 200
    assert resource.captured_req.context['_marshalled']
    assert resource.captured_req.media == {'name': 'john'}
    assert resource.captured_req.context['marshalled_stream'] == b'{"name":"john"}'


def test_support_default_loader(client):
    resource = WithSchemaResc()
    client.app.add_route('/test', resource)

    resp = client.simulate_post(
        '/test',
        json={'name': 'john'}
    )

    assert resp.status_code == 200
    assert resource.captured_req.context['_marshalled']
    assert resource.captured_req.context['dto'].data.name == 'john'


def test_support_custom_loader(client):
    resource = WithCustomLoader()
    client.app.add_route('/test', resource)

    resp = client.simulate_post(
        '/test',
        json={'name': 'john'}
    )

    assert resp.status_code == 200
    assert resource.captured_req.context['_marshalled']
    assert resource.captured_req.context['dto'].data.name == 'other'


def test_errors_during_loading(client):
    resource = WithSchemaResc()
    client.app.add_route('/test', resource)

    resp = client.simulate_post(
        '/test',
        json={'name': 1}
    )

    assert resp.status_code == 400
    assert resp.json == {'errors': {'name': ['Not a valid string.']}}
    assert resource.captured_req is None
