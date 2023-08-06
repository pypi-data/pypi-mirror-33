import logging
import sys
import subprocess
import os
from kryptoflow import definitions
import click
from . import dataset
from . import data_interface
from . import model

from .utils import parse_start_args, setup_logging


@click.command()
@click.option('--monitor', default=False, help='Monitor scraping jobs')
def scrape(monitor):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_start_args(args)
    setup_logging(args.loglevel)
    subprocess.run(['supervisord', '-c', os.path.join(definitions.RESOURCES_PATH, 'supervisord.conf')])


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == '__main__':
    run()

