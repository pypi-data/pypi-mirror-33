import falcon

from falcon_helpers.config import Config
from falcon_helpers.middlewares import multi as multimw


class API(falcon.API):
    __slots__ = (
        'config',
        'plugins',
        '_dynmw',
        'enable_dynamic_mw',
    )

    def __init__(self, middleware=None, enable_dynamic_mw=True, independent_middleware=True,
                 **kwargs):

        if enable_dynamic_mw and not independent_middleware:
            raise RuntimeError(
                f'Independent middleware must be enabled to use dynamic middleware. Either turn '
                'off dynamic middleware (enable_dynamic_mw=False) or enable independent middleware '
                '(independent_middleware=True).'
            )
        elif enable_dynamic_mw:
            self._dynmw = multimw.MultiMiddleware(middleware)
            kwargs['middleware'] = [self._dynmw]
            kwargs['independent_middleware'] = True
        else:
            kwargs['middleware'] = middleware

        self.plugins = {}

        super().__init__(**kwargs)

    def add_middleware(self, mw):
        self._dynmw.add_middleware(mw)

    @classmethod
    def from_inis(cls, *paths, api_kwargs=None):
        """Create an instance of the API from configuration files"""

        app = cls(**(api_kwargs or {}))

        app.config = Config.from_inis(*paths)

        return app
