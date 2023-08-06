from datetime import timezone as tz
import pytest
import sqlalchemy as sa

import falcon
import falcon.testing
import marshmallow_sqlalchemy as ms

from falcon_helpers.resources.crud import CrudBase, ListBase
from falcon_helpers.middlewares.sqla import SQLAlchemySessionMiddleware
from falcon_helpers.middlewares.marshmallow import MarshmallowMiddleware
from falcon_helpers.sqla.orm import BaseColumns, BaseFunctions, Testable
from falcon_helpers.sqla.db import session

from falcon_helpers.tests.fixtures import Base


class ModelOther(Base, BaseColumns, Testable):
    __tablename__ = 'mother'

    test_id = sa.Column(sa.Integer, sa.ForeignKey('mtest.id'), nullable=False)


class ModelTest(Base, BaseColumns, BaseFunctions, Testable):
    __tablename__ = 'mtest'

    name = sa.Column(sa.Unicode, nullable=False)
    uni = sa.Column(sa.Unicode, unique=True)
    other = sa.orm.relationship("ModelOther")


class ModelSchema(ms.ModelSchema):
    class Meta:
        model = ModelTest
        exclude = ('other',)


class BasicCrud(CrudBase):
    db_cls = ModelTest
    schema = ModelSchema

class List(ListBase):
    db_cls = ModelTest
    schema = ModelSchema

class ListSub(ListBase):
    db_cls = ModelTest
    schema = ModelSchema

    def get_objects(self, req, *args, **kwargs):
        if kwargs['objid'] == 'missing':
            return None

        if kwargs['objid'] == 'zero':
            return []


@pytest.fixture
def app():
    Base.metadata.drop_all()
    Base.metadata.create_all()

    app = falcon.API(
        middleware=[
            SQLAlchemySessionMiddleware(session),
            MarshmallowMiddleware(),
        ]
    )

    app.add_route('/crud/{obj_id}', BasicCrud())
    app.add_route('/bad', BasicCrud())
    app.add_route('/list', List())
    app.add_route('/list/{objid}/other', ListSub())
    return app


@pytest.fixture
def client(app):
    return falcon.testing.TestClient(app)


class TestCrudBase:
    def test_crud_base_get_404_with_no_object(self, client):
        resp = client.simulate_get('/crud/1')
        assert resp.status_code == 404

    def test_crud_base_get_500_with_misconfigured_route(self, client):
        resp = client.simulate_get('/bad')
        assert resp.status_code == 500

    def test_crud_base_get_200_with_object(self, client):
        m1 = ModelTest.testing_create()
        resp = client.simulate_get(f'/crud/{m1.id}')

        assert resp.status_code == 200
        assert resp.json == {
            'id': m1.id,
            'name': m1.name,
            'uni': m1.uni,
            'created_ts': m1.created_ts.replace(tzinfo=tz.utc).isoformat(),
            'updated_ts': m1.updated_ts.replace(tzinfo=tz.utc).isoformat(),
        }

    def test_crud_base_get_404_with_bad_primary_key(self, client):
        assert client.simulate_get(f'/crud/abs').status_code == 404

    def test_crud_base_post_duplicate_object(self, client):
        ModelTest.testing_create(uni='test')
        resp = client.simulate_post(
            f'/crud/new',
            json={
                'uni': 'test',
                'name': 'thing'
            })

        assert resp.status_code == 409

    def test_crud_base_get_404_with_wrong_id(self, client):
        m1 = ModelTest.testing_create()
        session.add(m1)
        session.commit()
        resp = client.simulate_get(f'/crud/{m1.id + 1}')

        assert resp.status_code == 404

    def test_crud_base_post(self, client):
        resp = client.simulate_post(
            f'/crud/new',
            json={
                'name': 'thing'
            })

        assert resp.status_code == 201
        assert session.query(ModelTest).get(resp.json['id']).name == 'thing'
        assert resp.json['name'] == 'thing'

    def test_crud_base_delete(self, client):
        m1 = ModelTest.testing_create()
        session.add(m1)
        session.commit()

        resp = client.simulate_delete(f'/crud/{m1.id}')

        assert resp.status_code == 204
        assert session.query(ModelTest).get(m1.id) is None

    def test_crud_base_delete_with_relationship(self, client):
        m1 = ModelTest.testing_create()
        session.add(m1)
        session.flush()

        mo1 = ModelOther.testing_create(test_id=m1.id)
        session.add(mo1)
        session.commit()

        resp = client.simulate_delete(f'/crud/{m1.id}')

        assert resp.status_code == 400
        assert session.query(ModelTest).get(m1.id) == m1
        assert session.query(ModelOther).get(mo1.id) == mo1

        assert 'errors' in resp.json
        assert resp.json['errors'] == [
            'Unable to delete because the object is connected to other objects'
        ]


class TestListBase:

    def test_default_filter_for_type(self):
        lb = ListSub()
        result = lb.filter_for_column(ModelTest.name, 'name')
        assert result.left == ModelTest.name
        assert result.right.value == 'name'
        assert result.operator.__name__ == 'contains_op'

    def test_default_filter_for_column(self):
        lb = ListSub()
        lb.column_filters = {
            'name': ModelTest.name.__eq__
        }

        result = lb.filter_for_param('name', 'val')
        assert result.left == ModelTest.name
        assert result.right.value == 'val'
        assert result.operator.__name__ == 'eq'

    def test_column_type_filter_creations(self):
        lb = ListSub()
        lb.type_filters = {
            (sa.sql.sqltypes.String, lambda a, b: 'works')
        }

        # check the defaults
        assert sa.sql.sqltypes.String in lb.column_type_filters

        # check the overriding
        assert lb.column_type_filters[sa.sql.sqltypes.String]('col', 'val') == 'works'

    def test_listbase_get_with_default_pagination(self, app):
        m1 = ModelTest.testing_create()
        m2 = ModelTest.testing_create()
        session.add_all([m1, m2])
        session.commit()

        resource = List()
        resource.default_page_size = None

        app.add_route('/pagination', resource)
        c = client(app)

        resp = c.simulate_get(f'/pagination')
        assert len(resp.json) == 2

        resp = c.simulate_get(f'/pagination', query_string=f'pageSize=1')
        assert len(resp.json) == 1

    def test_listbase_get(self, client):
        m1 = ModelTest.testing_create()
        m2 = ModelTest.testing_create()
        session.add_all([m1, m2])
        session.commit()

        resp = client.simulate_get(f'/list', query_string=f'name={m1.name}')

        assert len(resp.json) == 1
        assert resp.json[0]['id'] == m1.id
        assert resp.json[0]['name'] == m1.name

    def test_listbase_get_sends_404_for_subobj_with_none_respose(self, client):
        resp = client.simulate_get(f'/list/missing/other')
        assert resp.status_code == 404
        assert 'error' in resp.json

    def test_listbase_get_sends_200_for_subobj_with_empty_respose(self, client):
        ModelTest.testing_create()

        resp = client.simulate_get(f'/list/zero/other')
        assert resp.status_code == 200
        assert resp.json == []
