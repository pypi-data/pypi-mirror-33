#!/usr/bin/env python3
import logging
import os
import sys

from csboilerplate import cli_app


logger = logging.getLogger(__name__)


def exit(error_message=None):
    """log and exit.

    :param str error_message: will be logged. changes exit status to `1`.
    :exit 0: success
    :exit 1: error
    """
    if error_message is None:
        logger.info(f'pid `{os.getpid()}` exit without errors')
        sys.exit()
    logger.error(f'pid `{os.getpid()}` exit with error: {error_message}')
    sys.exit(1)


@cli_app(name='demo', exit_handler=exit)
def main(app):
    app.logging_config(log_level=app.args.debug)
    logger.info(f'start `{app.name}` w/ pid `{os.getpid()}`')
    if app.args.error:
        raise ValueError('something bad happened')


main.argparser.add_argument('-d', '--debug', action='count', default=0,
                            help='lower logging threshold, may be used twice')
main.argparser.add_argument('-e', '--error', action='store_true', help='raise some error')


if __name__ == '__main__':
    main()
