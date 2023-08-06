#! /usr/bin/env python
# coding: utf-8

import sys
import logging

__author__ = '鹛桑够'


logger = logging.getLogger("jy_cli")

sh = logging.StreamHandler()
logger.addHandler(sh)
logger.setLevel(logging.INFO)