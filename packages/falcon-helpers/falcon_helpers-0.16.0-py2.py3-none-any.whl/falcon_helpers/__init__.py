from .middlewares.jinja2 import Jinja2Middleware
from .middlewares.auth_required import AuthRequiredMiddleware

from .resources import auth0
from .config import Config
from .app import API

from . import contrib
