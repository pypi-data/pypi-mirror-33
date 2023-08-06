import unittest.mock as mock

import pytest
import click.testing

import falcon_helpers.contrib.cli as cli
import falcon_helpers.contrib.wsgi as wsgi


@pytest.fixture(scope='function')
def cli_with_app():
    @click.group()
    @click.pass_context
    def test(ctx):
        ctx.meta['app'] = 'fake'

    test.add_command(cli.server)
    return test


@pytest.fixture(scope='function')
def runner(request):
    return click.testing.CliRunner()


def test_server_without_host_and_port(runner, cli_with_app):
    with mock.patch('falcon_helpers.contrib.cli.make_server') as m_make_server:
        runner.invoke(cli_with_app, ['server', 'start'])
        m_make_server.assert_called_with(
            '127.0.0.1', 9090, 'fake',
            handler_class=wsgi.CustomLoggingWSGIRequestHandler)


def test_server_with_host(runner, cli_with_app):
    with mock.patch('falcon_helpers.contrib.cli.make_server') as m_make_server:
        runner.invoke(cli_with_app, ['server', 'start', '-h', 'localhost'])
        m_make_server.assert_called_with(
            'localhost', 9090, 'fake',
            handler_class=wsgi.CustomLoggingWSGIRequestHandler)


def test_server_with_port(runner, cli_with_app):
    with mock.patch('falcon_helpers.contrib.cli.make_server') as m_make_server:
        runner.invoke(cli_with_app, ['server', 'start', '-p', '9'])
        m_make_server.assert_called_with(
            '127.0.0.1', 9, 'fake',
            handler_class=wsgi.CustomLoggingWSGIRequestHandler)


def test_server_with_long(runner, cli_with_app):
    with mock.patch('falcon_helpers.contrib.cli.make_server') as m_make_server:
        runner.invoke(cli_with_app, ['server', 'start', '--port', '9', '--host', 'localhost'])
        m_make_server.assert_called_with(
            'localhost', 9, 'fake',
            handler_class=wsgi.CustomLoggingWSGIRequestHandler)


def test_server_without_app(runner):
    with mock.patch('falcon_helpers.contrib.cli.make_server') as m_make_server:
        res = runner.invoke(cli.server, ['start'])
        m_make_server.assert_not_called()

        assert 'Unable to find an application' in res.output
