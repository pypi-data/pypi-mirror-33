import logging
import wsgiref.simple_server


log = logging.getLogger(__name__)


class CustomLoggingWSGIRequestHandler(wsgiref.simple_server.WSGIRequestHandler):

    def log_message(self, format, *args):
        log.info(f'{format%args}')
