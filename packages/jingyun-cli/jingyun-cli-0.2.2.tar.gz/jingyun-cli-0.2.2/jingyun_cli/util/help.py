#! /usr/bin/env python
# coding: utf-8

import six

__author__ = '鹛桑够'


lang = "cn"

encoding = "utf-8"
second_encoding = "gb18030"


def decode(s):
    if isinstance(s, six.binary_type):
        try:
            return s.decode(encoding)
        except UnicodeError:
            return s.decode(second_encoding, "replace")
    if isinstance(s, (int, six.integer_types)):
        return "%s" % s
    return s


def encode(s):
    if isinstance(s, six.text_type):
        return s.encode(encoding)
    return s


def is_string(s):
    if isinstance(s, (six.binary_type, six.text_type)) is False:
        return False
    return True


def help_value(help_dict, key, *args):
    msg = help_dict[key][lang]
    msg = decode(msg)
    if len(args) > 0:
        args = map(decode, args)
        msg = msg % tuple(args)
    return msg
