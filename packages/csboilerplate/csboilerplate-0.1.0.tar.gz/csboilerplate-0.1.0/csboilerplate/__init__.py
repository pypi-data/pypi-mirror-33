import argparse
import logging
import signal
import sys
import types


def cli_app(**kwargs):
    """

    >>> from csboilerplate import cli_app, CommandLineApp
    >>> decorator = cli_app(name='my_app_name')
    >>> app = decorator(lambda x: x)
    >>> isinstance(app, CommandLineApp)
    True
    >>> app.name
    'my_app_name'


    :param kwargs:
    :return:
    :rtype: :class:`CommandLineApp`
    """
    def decorator(func):
        return CommandLineApp(func, **kwargs)
    return decorator


class CommandLineApp(object):
    """basic cli functionality.

    inspired by `pyCLI`.

    provides:
    - `argparser` and parsed `args`
    - logging helper
    - `SIGTERM` and `KeyboardInterrupt` handling
    - exit handling
    """
    args = None
    argparser = None
    _main = None
    name = None
    exit = None
    logger = None

    def __init__(self, main, name=sys.argv[0], exit_handler=None, sigterm_handler=None):
        self._main = main
        self.name = name
        self.logger = logging.getLogger(self.name)
        if exit_handler is None:
            self.exit = sys.exit
        else:
            self.exit = types.MethodType(exit_handler, self)
        self.argparser = argparse.ArgumentParser()
        if sigterm_handler is not False:
            signal.signal(signal.SIGTERM, sigterm_handler or (lambda signal, frame: self.exit('Terminated')))

    def __call__(self):
        self.args = self.argparser.parse_args()
        try:
            self._main(self)
        except KeyboardInterrupt:
            self.exit('KeyboardInterrupt')
        except Exception as e:
            self.logger.exception(e)
            self.exit('uncaught exception')
        self.exit()

    def logging_config(self, log_level=0, log_levels=(logging.WARNING, logging.INFO, logging.DEBUG), **kwargs):
        """increase log level.

        :param log_level int: index of `log_levels` to be chosen, defaults to `0` - warning, `1` - info, `2` - debug
        :param log_levels iterable: list of log levels
        :raise IndexError: if `log_level` is not in `log_levels`
        :return: None
        """
        logging.basicConfig(level=log_levels[log_level], **kwargs)
