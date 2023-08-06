import falcon.testing

from falcon_helpers.middlewares.multi import MultiMiddleware


class FakeMW:
    def process_request(self, req, resp):
        req.context['req'] = True

    def process_resource(self, req, resp, resource, params):
        req.context['resc'] = True

    def process_response(self, req, resp, resource, resp_succeded):
        media = resp.media
        media['resp'] = True
        resp.media = media


class FakeResc:
    def on_get(self, req, resp):
        resp.media = req.context


def test_accepts_middleware_during_init():
    mw = MultiMiddleware()

    assert mw.req_mw == []
    assert mw.resc_mw == []
    assert mw.resp_mw == []

    mw = MultiMiddleware(middleware=FakeMW())
    assert len(mw.req_mw) == 1
    assert len(mw.resc_mw) == 1
    assert len(mw.resp_mw) == 1

    mw = MultiMiddleware(middleware=[FakeMW(), FakeMW()])
    assert len(mw.req_mw) == 2
    assert len(mw.resc_mw) == 2
    assert len(mw.resp_mw) == 2


def test_calls_middlewares():
    app = falcon.API(middleware=MultiMiddleware(middleware=FakeMW()))

    app.add_route('/', FakeResc())

    c = falcon.testing.TestClient(app)
    resp = c.simulate_get('/')

    assert resp.json == {
        'req': True,
        'resc': True,
        'resp': True,
    }
