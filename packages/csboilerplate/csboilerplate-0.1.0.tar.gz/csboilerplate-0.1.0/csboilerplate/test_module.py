import argparse
import logging
import pytest
import signal
import sys
from unittest.mock import patch, Mock

import csboilerplate


# missing: test SIGTERM handling, dunno how to mock that


def noop(app):
    pass


@pytest.fixture(autouse=True)
def reset_sigterm_handler():
    signal.signal(signal.SIGTERM, signal.SIG_DFL)


def test_export():
    assert 'cli_app' in dir(csboilerplate)
    assert 'CommandLineApp' in dir(csboilerplate)


def test_cli_app():
    decorator = csboilerplate.cli_app()
    assert callable(decorator)
    app = decorator(noop)
    assert isinstance(app, csboilerplate.CommandLineApp)


@patch('csboilerplate.CommandLineApp')
def test_cli_app_kwargs(patched):
    decorator = csboilerplate.cli_app(a='a', b='b')
    decorator(noop)
    patched.assert_called_once()
    patched.assert_called_once_with(noop, a='a', b='b')


def test_CommandLineApp():
    dummy_main = Mock()
    app = csboilerplate.CommandLineApp(dummy_main)
    assert callable(app)
    dummy_main.assert_not_called()
    with pytest.raises(SystemExit):
        app()
    dummy_main.assert_called_once_with(app)


def test_CommandLineApp_argparser():
    app = csboilerplate.CommandLineApp(noop)
    assert isinstance(app.argparser, argparse.ArgumentParser)
    assert app.args is None
    with pytest.raises(SystemExit):
        app()
    assert isinstance(app.args, argparse.Namespace)


def test_CommandLineApp_attribute_defaults():
    app = csboilerplate.CommandLineApp(noop)
    assert app.name == sys.argv[0]
    assert app.exit is sys.exit


def test_CommandLineApp_name():
    app = csboilerplate.CommandLineApp(noop, name='test_name')
    assert app.name == 'test_name'


def test_CommandLineApp_exit_handler():
    exit = Mock()
    app = csboilerplate.CommandLineApp(noop, exit_handler=exit)
    exit.assert_not_called()
    app()
    exit.assert_called_once_with(app)
    app.exit()
    exit.assert_called_with(app)
    assert exit.call_count == 2
    app.exit(error_message='error')
    exit.assert_called_with(app, error_message='error')


def test_CommandLineApp_interrupt():
    interrupted = Mock(side_effect=KeyboardInterrupt)
    exit = Mock(side_effect=SystemExit)
    app = csboilerplate.CommandLineApp(interrupted, exit_handler=exit)
    with pytest.raises(SystemExit):
        app()
    exit.assert_called_once_with(app, 'KeyboardInterrupt')


def test_CommandLineApp_sigterm_handler():
    csboilerplate.CommandLineApp(noop, sigterm_handler=False)
    assert signal.getsignal(signal.SIGTERM) == signal.SIG_DFL
    csboilerplate.CommandLineApp(noop)
    assert callable(signal.getsignal(signal.SIGTERM))
    with pytest.raises(SystemExit):
        signal.getsignal(signal.SIGTERM)('signal', 'frame')
    csboilerplate.CommandLineApp(noop, sigterm_handler=noop)
    assert signal.getsignal(signal.SIGTERM) == noop


def test_CommandLineApp_uncaught_exception():
    broken = Mock(side_effect=ValueError)
    app = csboilerplate.CommandLineApp(broken)
    logger_exception = Mock()
    app.logger.exception = logger_exception
    with pytest.raises(SystemExit) as excinfo:
        app()
    assert excinfo.value.code == 'uncaught exception'
    logger_exception.assert_called_once()
    assert isinstance(logger_exception.call_args[0][0], ValueError)


@patch('csboilerplate.logging.basicConfig')
def test_CommandLineApp_logging_config(basicConfig):
    app = csboilerplate.CommandLineApp(noop)
    app.logging_config(log_level=0)
    assert basicConfig.call_args[1]['level'] == logging.WARNING
    app.logging_config(log_level=1)
    assert basicConfig.call_args[1]['level'] == logging.INFO
    app.logging_config(log_level=2)
    assert basicConfig.call_args[1]['level'] == logging.DEBUG
    with pytest.raises(IndexError):
        app.logging_config(log_level=3)
    app.logging_config(handlers=[42])
    assert basicConfig.call_args[1]['handlers'] == [42]
    app.logging_config(log_level=3, log_levels=[0, 1, 2, 3])
    assert basicConfig.call_args[1]['level'] == 3
