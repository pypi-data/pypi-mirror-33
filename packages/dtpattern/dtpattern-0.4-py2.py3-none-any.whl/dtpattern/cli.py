# -*- coding: utf-8 -*-

"""Console script for tablerec."""
import sys
import click
import logging
import logging.config

from dtpattern import defaultConf,debugConf,fileConf, infoConf

from dtpattern.services.cli_dtpattern import dtpattern as dtpattern1
from dtpattern.services.cli_dtpattern2 import dtpattern2


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group()
#@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--log', default='default', type=click.Choice(['default','info','debug', 'file']))
@click.option('--logconf', type=click.Path(), help="specify a log config")
def main(log, logconf):
    click.echo(logconf)

    if log=='default':
        logging.config.dictConfig(defaultConf)
    elif log=="debug":
        logging.config.dictConfig(debugConf)
    elif log=="info":
        logging.config.dictConfig(infoConf)
    elif log=="file":
        logging.config.dictConfig(fileConf)

    if logconf:
        logging.config.fileConfig(logconf)

    pass

main.add_command(dtpattern1)
main.add_command(dtpattern2)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
