import sqlalchemy as sa

from falcon_helpers.sqla.orm import ModelBase

def test_column_names():

    class Entity(ModelBase):
        __tablename__ = 'entity'
        c1 = sa.Column(sa.Integer, primary_key=True)

    assert Entity.orm_column_names() == {
        'c1',
    }


