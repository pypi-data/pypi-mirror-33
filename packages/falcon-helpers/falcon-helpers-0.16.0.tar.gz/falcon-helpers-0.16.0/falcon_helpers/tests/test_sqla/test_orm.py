import sqlalchemy as sa

from falcon_helpers.sqla.orm import BaseFunctions
from falcon_helpers.tests.fixtures import Base


def test_column_names():

    class Entity(Base, BaseFunctions):
        __tablename__ = 'entity'
        c1 = sa.Column(sa.Integer, primary_key=True)

    assert Entity.orm_column_names() == {
        'c1',
    }
