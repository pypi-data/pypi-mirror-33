#! /usr/bin/env python
# coding: utf-8

import logging
import argparse
from jingyun_cli import logger
from help import help_value

__author__ = '鹛桑够'


args_man = argparse.ArgumentParser()


def parse_args(args=None, namespace=None):
    args_man.add_argument("--verbose", "--debug", dest="debug", action="store_true", default=False,
                          help=help_value({}, "debug"))
    args_r = args_man.parse_args(args, namespace)
    if args_r.debug is True:
        logger.setLevel(logging.DEBUG)
    return args_r