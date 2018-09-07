# -*- coding: utf-8 -*-
from .random_logger import RandomLogger
from .random_logger import RandomLoggerConfig
from .random_logger import RandomLoggerError

import click
import logging
import sys
import time


@click.command()
@click.option('--configuration', '-f', default='random_logger.yml',
                type=click.Path(exists=True, dir_okay=False, resolve_path=True),
                help='The path to the configuration file.')
def main(configuration):
    logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)s [%(name)s] {%(threadName)s} %(message)s',
                        level=logging.DEBUG)
    try:
        config = RandomLoggerConfig(click.format_filename(configuration))
    except RandomLoggerError as e:
        click.echo(e)
        sys.exit(-1)

    logger = RandomLogger(config)
    logger.start()

    while True:
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    main()

