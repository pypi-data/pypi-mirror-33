import logging
import ujson
import sqlalchemy as sa
import falcon

from ..utils import flatten


log = logging.getLogger(__name__)


class ListBase:
    """A base class for returning list of objects.

    This base class assumes you are using the marshmallow middleware for object
    serialization and sqlalchemy for database access.

    Attributes:
        db_cls: Set this to a SQLAlchemy entity
        schema: Set this a Marshmallow schema

    Filtering:

        Filtering allows you to specify custom logic to limit query results while still using the
        standard ListBase query builder.

        It is possible to define custom type and custom column filters on names properties by using
        the type_filters and the column_filters settings appropriately. `column_filters` will be
        used first and then fallback to a `type_filter`. Basic type filters are defined for common
        types where a sensible default is chosen. Note that `Integer` and `Float` will try to do the
        conversion and error if bad data is sent.


        To specify column filters, assign the `column_filters` class variable to a dictionary
        containing the name of the key and the function(value) you want to call.

            class MyEntityList(ListBase):
                db_cls = MyEntity
                schema = MyEntitySchema

                column_filters = {
                    'my_column': MyEntity.filters_for_string
                }

        To add additional type filters use the `type_filters` class variable.

            class MyEntityList(ListBase):
                db_cls = MyEntity
                schema = MyEntitySchema

                type_filters = {
                    sqlalchemy.types.DateTime: MyEntity.filters_for_string
                }


    """
    db_cls = None
    schema = None

    default_order = None

    # TODO: Deprecate the 50 page size limit and make this None
    default_page_size = 50

    _default_type_filters = frozenset([
        (sa.sql.sqltypes.String,  lambda col, val: col.contains(val)),
        (sa.sql.sqltypes.Unicode, lambda col, val: col.contains(val)),
        (sa.sql.sqltypes.Integer, lambda col, val: col == int(val)),
        (sa.sql.sqltypes.Numeric, lambda col, val: col == float(val)),
    ])
    type_filters = None

    column_filters = None

    @property
    def column_type_filters(self):
        filters = dict()
        filters.update({k: v for k, v in self._default_type_filters})
        filters.update(self.type_filters or {})
        return filters

    def on_get(self, req, resp, **kwargs):
        result = self.get_objects(req, **kwargs)

        if result is None:
            resp.status = falcon.HTTP_404
            resp.media = {'error': 'Unable to find objects with that identifier'}
            return

        resp.status = falcon.HTTP_200
        resp.body = self.response_data(result, req, **kwargs)

    def response_data(self, data, req, **kwargs):
        schema = self.schema(many=True)
        return schema.dump(data)

    def base_query(self, req, **kwargs):
        return self.session.query(self.db_cls)

    def pagination_hook(self, query, req, **kwargs):
        """Create a hook for pagination"""
        size = req.params.get('pageSize')

        if not size:
            size = self.default_page_size
        else:
            size = int(size)

        # -1 here is so that the page numbers start at 1
        page = int(req.params.get('page', 1)) - 1

        if page < 0:
            page = 0

        if size:
            return query.limit(size).offset((page * size))
        else:
            return query

    def columns_for_params(self, params):
        return {getattr(self.db_cls, x)
                for x in self.db_cls.orm_column_names() & params.keys()}

    def filter_for_column(self, column, value):
        filters = self.column_type_filters
        if (type(column.property) == sa.orm.properties.ColumnProperty
                and type(column.type) in filters):
            return filters[type(column.type)](column, value)

        return None

    def filter_for_param(self, key, value):
        try:
            f = self.column_filters[key]
        except KeyError:
            return None

        return f(value)

    def filter_hook(self, query, req, **kwargs):
        filters = {col.key: self.filter_for_column(col, req.params[col.key])
                   for col in self.columns_for_params(req.params)}

        # Custom column filters
        if self.column_filters:
            filters.update({key: self.filter_for_param(key, value)
                            for key, value in req.params.items()})
        return query.filter(*[x for x in filters.values() if x is not None])

    def order_hook(self, query, req, **kwargs):
        request_order = req.params.get('sort_by', [])

        # This takes advantage of falcons duplicate-param parsing which returns
        # a list when it finds a param multiple times.
        if type(request_order) != list:
            request_order = [request_order]

        request_order = list(flatten([x.split(';') for x in request_order]))
        request_order = [sa.desc(x[1:]) if x.startswith('-') else sa.asc(x) for x in request_order]

        default_order = request_order or self.default_order or self.db_cls.__mapper__.primary_key
        return query.order_by(*default_order)

    def custom_hook(self, query, req, **kwargs):
        return query

    def get_objects(self, req, *args, **kwargs):
        base = self.base_query(req, **kwargs)
        filtered = self.filter_hook(base, req, **kwargs)
        order = self.order_hook(filtered, req, **kwargs)
        paged = self.pagination_hook(order, req, **kwargs)
        final = self.custom_hook(paged, req, **kwargs)

        return final.all()


class CrudBase:
    """A very simple CRUD resource.

    This base class assumes you are using the marshmallow middleware for object
    serialization and sqlalchemy for database access.

    Attributes:
        db_cls: Set this to a SQLAlchemy entity
        schema: Set this a Marshmallow schema
    """
    db_cls = None
    schema = None
    default_param_name = 'obj_id'

    def delete_object(self, obj, req, **kwargs):
        self.session.delete(obj)
        self.session.flush()

    def get_object(self, req, **kwargs):
        try:
            obj_id = kwargs[self.default_param_name]
        except KeyError:
            log.error(
                f'The resource {self.__class__.__name__} route is not using the correct parameter '
                f'name for the object identifier. Expecting `{self.default_param_name}` but it was '
                f'not in the matched route parameters. Add a `default_param_name` to the resource '
                f'which matches the route variable. Found these items: {",".join(kwargs.keys())}.'
            )
            raise falcon.HTTPInternalServerError("Misconfigured route")

        try:
            return self.session.query(self.db_cls).get(obj_id)
        except sa.exc.DataError as e:
            self.session.rollback()
            log.warning(f'Bad primary key given to  {self.__class__.__name__}')
            return None

    def on_get(self, req, resp, **kwargs):
        result = self.get_object(req, **kwargs)

        if not result:
            raise falcon.HTTPNotFound

        schema = self.schema()
        resp.body = schema.dump(result)
        resp.status = falcon.HTTP_200

    def on_put(self, req, resp, **kwargs):
        self.session.add(req.context['dto'].data)
        self.session.flush()

        resp.status = falcon.HTTP_200
        resp.body = self.schema().dump(req.context['dto'].data)

    def on_post(self, req, resp, **kwargs):
        self.session.add(req.context['dto'].data)

        try:
            self.session.flush()
        except sa.exc.IntegrityError as e:
            self.session.rollback()
            resp.status = falcon.HTTP_409
            resp.media = {
                'errors': ['An object with that identifier already exists.']
            }
            return

        resp.status = falcon.HTTP_201
        resp.media = self.schema().dump(req.context['dto'].data).data

    def on_delete(self, req, resp, **kwargs):
        try:
            obj = self.get_object(req, **kwargs)

            if obj:
                self.delete_object(obj, req, **kwargs)

        except sa.exc.IntegrityError as e:
            self.session.rollback()
            resp.status = falcon.HTTP_400
            resp.media = {'errors': [('Unable to delete because the object is '
                                      'connected to other objects')]}
        else:
            resp.status = falcon.HTTP_204
