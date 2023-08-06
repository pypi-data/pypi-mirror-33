from wsgiref.simple_server import make_server
import logging
import click

from falcon_helpers.contrib.wsgi import CustomLoggingWSGIRequestHandler

log = logging.getLogger(__name__)


@click.group()
def server():
    """Basic development server

    Add this to your base command application command like this

        @click.group()
        @click.pass_context
        @click.option('-c', '--config', type=click.Path(exists=True), default='config.ini')
        def app(ctx, config):
            ctx.meta['app'] = app.create_app(config)


        app.add_command(server)
    """
    pass


@server.command()
@click.option('-h', '--host', type=str, default='127.0.0.1')
@click.option('-p', '--port', type=int, default=9090)
@click.pass_context
def start(ctx, host, port):
    try:
        app = ctx.meta['app']
    except KeyError:
        raise click.ClickException(
            'Unable to find an application in click context, looking for meta[\'app\']'
        )

    log.info(f'Starting the dev server on {host}:{port} this should not be used in production...')

    httpd = make_server(host, port, app, handler_class=CustomLoggingWSGIRequestHandler)
    httpd.serve_forever()
