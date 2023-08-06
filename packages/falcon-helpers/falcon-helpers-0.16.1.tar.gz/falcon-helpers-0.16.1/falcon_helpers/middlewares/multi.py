from falcon import util


class MultiMiddleware:
    """MultiMiddleware allows dynamic addition of middlewares onto the main middleware stack

    NOTE(nZac): If you use falcon_helpers.app.API you get this by default and `API.add_middleware`
    is mapped to this object.

    NOTE(nZac): This middleware only supports independent middleware. All process responses will be
    run regardless of the corresponding process_request being run.

    """
    __slots__ = (
        'req_mw',
        'resc_mw',
        'resp_mw',
    )

    def __init__(self, middleware=None):
        self.req_mw = list()
        self.resc_mw = list()
        self.resp_mw = list()

        middleware = middleware if middleware else list()

        if not isinstance(middleware, list):
            self.add_middleware(middleware)
        else:
            for mw in middleware:
                self.add_middleware(mw)

    def add_middleware(self, mw):
        process_request = util.get_bound_method(mw, 'process_request')
        process_resource = util.get_bound_method(mw, 'process_resource')
        process_response = util.get_bound_method(mw, 'process_response')

        if process_request:
            self.req_mw.append(process_request)

        if process_resource:
            self.resc_mw.append(process_resource)

        if process_response:
            self.resp_mw.append(process_response)

    def process_request(self, req, resp):
        for mw in self.req_mw:
            mw(req, resp)

    def process_resource(self, req, resp, resource, params):
        for mw in self.resc_mw:
            mw(req, resp, resource, params)

    def process_response(self, req, resp, resource, resp_succeded):
        for mw in self.resp_mw:
            mw(req, resp, resource, resp_succeded)
