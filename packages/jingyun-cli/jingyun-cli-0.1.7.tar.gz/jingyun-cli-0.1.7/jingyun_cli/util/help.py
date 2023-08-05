#! /usr/bin/env python
# coding: utf-8
__author__ = '鹛桑够'


lang = "cn"


def help_value(help_dict, key, *args):
    msg = help_dict[key][lang]
    if len(args) > 0:
        msg = msg % args
    return msg
