# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import sys

import click

from sagify.api import local as api_local
from sagify.commands import ASCII_LOGO
from sagify.log import logger

click.disable_unicode_literals_warning = True


@click.group()
def local():
    """
    Commands for local operations: train and deploy
    """
    pass


@click.command()
@click.option(u"-d", u"--dir", required=False, default='.', help="Path to sagify module")
def train(dir):
    """
    Command to train ML model(s) locally
    """
    logger.info(ASCII_LOGO)
    logger.info("Started local training...\n")

    try:
        api_local.train(dir=dir)

        logger.info("Local training completed successfully!")
    except ValueError:
        logger.info("This is not a sagify directory: {}".format(dir))
        sys.exit(-1)
    except Exception as e:
        logger.info("{}".format(e))
        return


@click.command()
@click.option(u"-d", u"--dir", required=False, default='.', help="Path to sagify module")
def deploy(dir):
    """
    Command to deploy ML model(s) locally
    """
    logger.info(ASCII_LOGO)
    logger.info("Started local deployment at localhost:8080 ...\n")

    try:
        api_local.deploy(dir=dir)
    except ValueError:
        logger.info("This is not a sagify directory: {}".format(dir))
        sys.exit(-1)
    except Exception as e:
        logger.info("{}".format(e))
        return


local.add_command(train)
local.add_command(deploy)
